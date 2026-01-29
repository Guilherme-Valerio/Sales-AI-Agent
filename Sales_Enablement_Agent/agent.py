from google.adk import Agent
from vertexai import agent_engines
import vertexai
import os
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types
import asyncio

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# -------------------------------------------------
# CLIENT SETUP
# -------------------------------------------------

def get_genai_client():
    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT is not defined")

    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )

MODEL_NAME = "gemini-2.5-pro"


# -------------------------------------------------
# TOOL 1 — REAL LEAD RESEARCH (WITH INTERNET)
# -------------------------------------------------

def analyze_lead(
    lead_name: str,
    company_name: str,
    email: str,
    role: str
) -> str:
    """
    Researches real public information about the company
    and generates a Sales Brief with 5 key points.
    """
    client = get_genai_client()
    prompt = f"""
You are a Sales Intelligence Agent.

Research PUBLIC information about the company below using web search.
Use ONLY publicly available information.
If data is uncertain, clearly label it as estimated.

Lead:
- Name: {lead_name}
- Company: {company_name}
- Email: {email}
- Role: {role}

Your task:
Generate a Sales Brief following this structure:

1. **Company Context:** Segment, industry, and estimated size.
2. **Strategy:** Likely business pain point related to the role.
3. **The Hook (CRITICAL):** Find 1 RECENT news, press release, or podcast featuring the company or lead. Use this as a conversation starter.
4. **Why it matters:** Why the pain point + news create an opportunity now.
5. **Sources:** List 1-2 URLs used to find this info (so the human can verify).

Rules:
- Use web search results to find specific recent events (last 6 months).
- If no news is found, focus on a company initiative found on their blog.
- Be concise.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    google_search=types.GoogleSearch()
                )
            ]
        )
    )

    return response.text.strip()


# -------------------------------------------------
# TOOL 2 — REFINEMENT
# -------------------------------------------------

def refine_lead_summary(
    current_summary: str,
    focus_area: str
) -> str:
    """
    Refines the Sales Brief maintaining the 5 points
    but adjusting the requested focus.
    """
    client = get_genai_client()

    prompt = f"""
Refine the Sales Brief below.

Rules:
- Keep EXACTLY 5 bullet points
- Do NOT remove uncertainty labels (estimated)
- Shift focus toward: {focus_area}
- Be concise and sales-oriented

Sales Brief:
{current_summary}
"""
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()


# -------------------------------------------------
# TOOL 3 — CONTENT GENERATION (FINAL STEP)
# -------------------------------------------------

def generate_outreach_content(
    sales_brief: str,
    content_type: str,
    sender_name: str = "Sales Representative"
) -> str:
    """
    Generates a Cold Outreach Email or LinkedIn Post
    based strictly on the provided Sales Brief.
    """
    client = get_genai_client()

    prompt = f"""
You are an expert Sales Copywriter.
Create a draft for a {content_type} (e.g., Cold Email or LinkedIn Message).

CONTEXT (Sales Brief):
{sales_brief}

SENDER NAME: {sender_name}

RULES:
1. Tone: Professional, direct, and contextualized (not generic).
2. Focus: Connect the "Likely pain point" from the brief to a solution.
3. Length: Short and respectful of time (max 150 words).
4. No fluff: Avoid phrases like "I hope this email finds you well".
5. Call to Action (CTA): Low friction (e.g., "Worth a chat?", "Open to ideas?").

OUTPUT FORMAT:
If Email: Subject Line + Body
If LinkedIn: Body only
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()


# -------------------------------------------------
# ROOT AGENT INSTRUCTION
# -------------------------------------------------

ROOT_AGENT_INSTRUCTION = """
You are the **Sales Lead Research Agent**.

Your goal is to prepare the salesperson for the first contact.
You perform the full cycle: Research -> Strategy -> Drafting.

---

## 🔧 TOOLS

### 1. analyze_lead (MANDATORY START)
- Researches the lead on the internet.
- Generates the inputs (Sales Brief).

### 2. refine_lead_summary (OPTIONAL)
- Use only if the user asks to change the research focus.

### 3. generate_outreach_content (FINALIZATION)
- Generates the final text for sending (Email or LinkedIn).
- Requires the output from step 1 or 2.

---

## 🧠 THOUGHT PROCESS (WORKFLOW)

1.  **Received a name/company?** -> Call `analyze_lead`.
2.  **Have the Brief?** -> Ask if the user wants to generate the email/LinkedIn message or refine the data.
3.  **User asked for Email/LinkedIn?** -> Call `generate_outreach_content` using the Brief text you already have.

---

## ❗ RULES

- Do not invent lead data; rely on the research.
- When generating the email, be concise and use the discovered data.
"""

# -------------------------------------------------
# AGENT ENGINE SETUP
# -------------------------------------------------

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    staging_bucket=os.getenv("STAGING_BUCKET")
)

root_agent = Agent(
    model="gemini-2.5-pro",
    name="sales_enablement_agent",
    description="B2B Sales Research and Drafting Agent",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[analyze_lead, refine_lead_summary, generate_outreach_content],
)

AGENT_RESOURCE_NAME = (
    f"projects/243890394709/locations/us-central1/reasoningEngines/2448160495778136064"
)

USER_ID = "user"

# -------------------------------------------------
# CHAT LOOP
# -------------------------------------------------

async def chat_with_sales_agent():
    """
    Interactive terminal chat with a deployed Sales Enablement Agent.
    Type 'exit' to end the session.
    """

    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT is not set")

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print("\n--- Connecting to Sales Enablement Agent ---\n")

    # 1. Get remote agent
    remote_app = agent_engines.get(AGENT_RESOURCE_NAME)

    # 2. Create session
    session = await remote_app.async_create_session(user_id=USER_ID)
    session_id = session["id"]

    print(f"Session created: {session_id}")
    print("Type your message below. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("\nEnding session. Goodbye 👋")
            break

        if not user_input:
            continue

        async for event in remote_app.async_stream_query(
            user_id=USER_ID,
            session_id=session_id,
            message=user_input,
        ):
            if "content" not in event:
                continue

            parts = event["content"].get("parts", [])

            for part in parts:

                if "text" in part:
                    print(f"Agent: {part['text']}")

                elif "function_call" in part:
                    fn = part["function_call"]
                    print(
                        f"[Tool Call] {fn['name']} | Args: {fn['args']}"
                    )

                elif "function_response" in part:
                    print("[Tool Result] Success")

        print("")  # visual spacing between turns


# -------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------

if __name__ == "__main__":
    asyncio.run(chat_with_sales_agent())
