
# Closira AI Support Agent: Bloom Aesthetics 🌸

**Live Prototype:** [Streamlit App Deployment](https://customer-support-workflow.streamlit.app/)
**Video Walkthrough:** https://youtu.be/LB27tMokmX0

An AI-powered customer support workflow built to handle inbound customer enquiries for small and medium businesses (SMBs). Developed by Pranay Varanasi for the Closira AI Engineering Intern assignment.

This prototype demonstrates a full end-to-end support session, strictly adhering to business-defined SOPs to answer FAQs, qualify leads, generate structured summaries, and escalate out-of-scope or sensitive issues to human agents.

---

## 🚀 Features (The 4 Stages)

* **Stage 1: FAQ Answering:** Reliably answers customer questions strictly using the provided Bloom Aesthetics SOP, with explicitly enforced hallucination prevention.
* **Stage 2: Lead Qualification:** Smoothly collects necessary booking details (past visit history, preferred date/time) before moving forward.
* **Stage 3: Escalation Detection:** Automatically halts the automated flow and flags for human handoff if the user complains, asks a medical question, or requests unlisted services.
* **Stage 4: Conversation Summary:** Generates a structured JSON summary at the end of the session, capturing intent, collected details, and recommended next actions.

---

## 🛠️ Tech Stack & Dependencies

* **Python 3.8+**
* **[Streamlit](https://streamlit.io/)**: Provides the interactive, user-friendly chat UI.
* **[OpenRouter API](https://openrouter.ai/)**: Utilizing `openai/gpt-4o-mini` for fast, cost-effective, and highly steerable inference.
* **[OpenAI Python SDK](https://github.com/openai/openai-python)**: Used to interface with the OpenRouter endpoint.

*Dependencies are listed in `requirements.txt`.*

---

## ⚙️ Setup & Local Installation

If you prefer to run the application locally instead of using the live deployment:

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/closira-support-agent.git
cd closira-support-agent

```

**2. Install dependencies**

```bash
pip install -r requirements.txt

```

**3. Set your API Key**
This application uses OpenRouter. Set your API key as an environment variable in your terminal:

* **Mac/Linux:**
```bash
export OPENROUTER_API_KEY="your_openrouter_api_key_here"

```


* **Windows (Command Prompt):**
```bash
set OPENROUTER_API_KEY=your_openrouter_api_key_here

```



**4. Run the App**
Launch the Streamlit interface by running the following command in your terminal:

```bash
streamlit run main.py

```

The app will open automatically in your browser at `http://localhost:8501`.

> **Evaluation Note:** Use the sidebar panel in the UI to trigger the Stage 4 "Generate Session Summary" JSON output or to reset the agent.

---
## ⚖️ Trade-offs & Known Limitations

* **Prompt Injection vs. RAG:** For this prototype, the SMB SOP is injected directly into the system prompt. This guarantees zero retrieval latency and eliminates the risk of retrieval failures (hallucinations caused by missing context). I specifically opted out of building a complex Retrieval-Augmented Generation (RAG) pipeline for this build because, for a short and static SOP, direct context injection is significantly more deterministic, lightweight, and cost-effective.
* **Escalation via LLM Flagging:** Escalation detection relies on the core LLM generating an `[ESCALATE]` tag rather than utilizing a secondary sentiment-analysis model. This reduces API calls and speeds up response times, but it does mean the system relies entirely on the instruction-following capabilities of `gpt-4o-mini` to catch edge cases.
* **Session Persistence:** The current Streamlit session state stores conversation history in memory. If the page is refreshed, the chat resets. In a production Closira environment, this conversation state would be stored in a persistent database (e.g., PostgreSQL or Redis) linked to a user's WhatsApp or email session ID.
