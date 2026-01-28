# 🚀 Sales Enablement & Outreach Agent

An intelligent AI Agent designed to eliminate the "grunt work" of sales research. By automating the discovery and copywriting phase, this agent allows Sales Development Representatives (SDRs) and Account Executives (AEs) to focus on **building relationships and closing deals.**

---

## 🕵️ The Problem: The "Research Trap"

Sales professionals spend **20-30% of their day** manually researching leads. This involves opening multiple tabs to find company data, news for a "hook," and business pain points. This manual work is slow, inconsistent, and prevents scaling.

## 🛠️ The Solution: Automated Sales Intelligence

This agent performs the full SDR lifecycle in seconds using **Vertex AI Reasoning Engine**:

1. **Discovery (The Detective):** Uses **Google Search** to find real-time company data and "trigger events" (news, press releases).
2. **Strategy:** Analyzes the lead's role and company context to predict likely business pain points.
3. **Outreach (The Copywriter):** Generates high-conversion, professional cold emails or LinkedIn messages.

---

## 🌐 Live Demo

The agent is currently deployed and available here:
👉 **[Sales Intelligence Agent Hub](https://sales-agent-app-243890394709.us-central1.run.app/)**

> [!NOTE]
> Access to the backend is restricted. To test with your own leads, please email **guilherme.svalerio@hotmail.com** for access.

---

## 🧪 Local Execution Examples

### 1. Terminal CLI (Direct Agent Interaction)

You can interact with the agent logic directly through the terminal to verify the search tools and reasoning flow.

```bash
# Creating and Activating environment and running the agent
python -m venv venv

venv\Scripts\activate

python agent.py      

--- Connecting to Sales Enablement Agent ---
```

### 2. ADK Web Server (Developer Interface)

The ADK Web Server provides a local GUI and detailed debug traces for tool execution.

```bash
adk web      
# INFO: Started server process
# INFO: Uvicorn running on http://127.0.0.1:8000

```

*This interface allows for real-time monitoring of function calls and candidate responses during development.*

---

## ⚙️ Setup & Configuration

### 1. Prerequisites

* **Python 3.11+**
* **Google Cloud SDK (gcloud CLI)** installed and authenticated.
* Vertex AI Project with **Reasoning Engine** enabled.

### 2. Installation

```bash
git clone <your-repo-link>
pip install -r requirements.txt
gcloud auth application-default login

```

### 3. Environment Variables

Create a `.env` file:

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

```

---

## 🏗️ Technical Architecture

* **Frontend:** [Streamlit](https://streamlit.io/) for the user-facing chat interface.
* **Agent Engine:** [Vertex AI Reasoning Engine](https://www.google.com/search?q=https://cloud.google.com/vertex-ai/docs/reasoning-engine/overview) for orchestration.
* **LLM:** Gemini 2.5 Pro.
* **Tools:** Custom Python functions with **Google Search** integration.
* **Deployment:** [Google Cloud Run](https://cloud.google.com/run) (Containerized via Docker).

---

## 🔮 Roadmap

* **CRM Integration:** Push generated briefs directly to **Salesforce/HubSpot**.
* **Batch Processing:** Upload a CSV of 100+ leads for automated bulk enrichment.

**Developed by Guilherme Valerio**
*Specializing in Sales Automation & Generative AI.*

---