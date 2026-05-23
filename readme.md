
# Closira AI Support Agent: Prompt Design & Architecture

This document outlines the reasoning, prompt engineering strategies, and safety mechanisms used to build the Bloom Aesthetics AI Support Agent.

## 1. The System Prompt

The core behavior of the agent is driven by the following system prompt:

```text
You are the AI support agent for Bloom Aesthetics Clinic. Your tone is warm, professional, and reassuring.

SOP DATA:
{SOP_DATA}

INSTRUCTIONS:
1. FAQ ANSWERING: Answer questions strictly using the SOP data above. Do not hallucinate or invent prices, services, or policies.
2. LEAD QUALIFICATION: If a user shows intent to book a service, smoothly weave in these two questions (one at a time):
   - "Have you visited Bloom Aesthetics before?"
   - "Do you have a specific date or time in mind for your visit?"
3. ESCALATION: You must immediately output the exact phrase "[ESCALATE: <reason>]" followed by a polite human handoff message if the user:
   - Asks a medical question.
   - Expresses frustration or complains.
   - Attempts to negotiate pricing.
   - Asks about a service not listed in the SOP.

```

## 2. Hallucination Prevention Strategy

Small and Medium Businesses (SMBs) cannot afford for their AI to invent policies or pricing. To ensure the AI stays strictly within the boundaries of the provided SOP, two main strategies were deployed:

* **Explicit Prompt Boundaries:** The prompt explicitly instructs the LLM: *"Answer questions strictly using the SOP data above. Do not hallucinate or invent prices, services, or policies."* By placing the SOP data immediately before the behavioral instructions, the context window prioritizes the factual ground truth.
* **Low API Temperature:** In the backend logic (`main.py`), the model's temperature is set to `0.2` for user interactions (and `0.0` for the Stage 4 summary generation). This reduces the model's creative variance, forcing it to stick to the most highly probable tokens derived from the SOP context rather than "guessing" to fill conversational gaps.

## 3. Confidence-Based Escalation Logic

The workflow handles out-of-scope questions and low-confidence scenarios via an **Explicit Flagging** system.

Instead of relying on a secondary sentiment-analysis model (which adds latency and cost), the core LLM is instructed to act as its own monitor. If it detects a predefined trigger (e.g., a medical question, a complaint, or an unlisted service request), it is instructed to prefix its response with the exact string `[ESCALATE: <reason>]`.

**Why this works:**

1. **Deterministic Parsing:** The Python backend simply checks for the substring `if "[ESCALATE" in ai_message`. If found, it flips a state flag (`is_escalated = True`), preventing further automated replies and signaling the UI to freeze the chat.
2. **Graceful Handoff:** The prompt instructs the AI to follow the tag with a polite message (e.g., *"Let me connect you with our clinic manager"*). This ensures the customer feels taken care of while the system routes the ticket to a human agent.

## 4. Tone and Persona for SMB Customers

For a local business like Bloom Aesthetics Clinic, trust is paramount. An overly robotic or highly corporate tone can alienate potential customers.

* **The Persona:** The prompt defines the persona as *"warm, professional, and reassuring."* * **The Execution:** By explicitly defining this tone, the model softens its delivery. Instead of abruptly stating, "We do not offer that," it naturally leans toward empathetic phrasing like, "I'm sorry, I don't have that information right now." Furthermore, the lead qualification instructions force the AI to ask questions *"one at a time,"* mimicking natural human pacing rather than interrogating the customer with a rapid-fire intake form.

## 5. Model Selection Trade-offs

The workflow utilizes **GPT-4o-mini** (via OpenRouter) as the core engine.

* **Why GPT-4o-mini?** It is exceptionally fast and highly cost-effective for repetitive SMB customer service tasks. It has excellent instruction-following capabilities (crucial for adhering to the strict SOP and escalation rules) and natively outputs highly reliable JSON when `response_format={"type": "json_object"}` is required (used in Stage 4: Conversation Summary).
* **Limitation:** While highly capable of processing the current SOP, if the business scales to require massive, multi-page vector-database RAG lookups, the retrieval architecture would need to be expanded beyond a simple injected prompt. However, for a standard SMB profile, injecting the SOP directly into the system prompt is the most deterministic and lowest-latency approach.
