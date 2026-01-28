# 📦 Package: Sales Enablement Agent Internals

This directory contains the core logic, tool definitions, and deployment configurations for the Sales Enablement AI Agent. It is designed to be orchestrated by the **Vertex AI Reasoning Engine**.

---

## 📂 Directory Structure

* `agent.py`: The core script defining the `Agent` object, system instructions, and tool definitions.
* `app.py`: The Streamlit frontend interface for user interaction.
* `requirements.txt`: Package-specific dependencies.
* `.env`: Local environment configuration (Project ID, Location).
* `Dockerfile`: Containerization instructions for Cloud Run deployment.

---

## 🛠️ Core Tool Logic

The agent is built on three primary Python functions that the LLM (Gemini 2 Pro) can trigger autonomously:

### 1. `analyze_lead`

* **Purpose:** Live research using Google Search.
* **Input:** Lead name, Company, Email, Role.
* **Mechanism:** Triggers a search for recent financial news, press releases, and company size. It specifically looks for "hooks" (trigger events) within the last 6 months.

### 2. `generate_outreach_content`

* **Purpose:** Creative copywriting.
* **Input:** Sales Brief (from `analyze_lead`), Content Type (Email/LinkedIn).
* **Mechanism:** Implements a "no-fluff" sales methodology. It bridges the gap between a discovered business pain point and a recommended sales angle.

### 3. `refine_lead_summary`

* **Purpose:** Iterative research.
* **Input:** Existing brief and a "Focus Area."
* **Mechanism:** Allows the user to pivot the research (e.g., "Focus more on their AI server backlog").

---

## 🏗️ Reasoning Engine Integration

This package is designed to be deployed as a **Reasoning Engine** (formerly known as Vertex AI Extensions).

**Key Integration Details:**

* **Base Class:** `google.adk.Agent`
* **Orchestration:** The agent manages state and tool-calling loops automatically via the `agent_engines` SDK.
* **Authentication:** Uses Service Account credentials (via ADC) to access Vertex AI and Google Search APIs.

---

## ⚠️ Security & Standards

* **Data Privacy:** This agent only accesses **publicly available** information via Google Search. It does not access private LinkedIn profiles or internal company databases.
* **Hallucination Control:** The `analyze_lead` tool is strictly instructed to provide **Sources (URLs)** for every financial claim made.

---

**Maintainer:** Guilherme Valerio

**Version:** 1.1.0

---
