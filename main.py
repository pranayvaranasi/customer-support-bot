import streamlit as st
import os
import json
from openai import OpenAI

# 1. API Configuration (OpenRouter)
# We use the standard OpenAI SDK but point the base_url to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY") 
)

# 2. SOP & Prompts
SOP_DATA = """
Business: Bloom Aesthetics Clinic
Hours: Mon-Sat, 9 am-7 pm
Services: Botox (from £200), Fillers (from £250), Consultations (free)
Booking: Via WhatsApp or website. 24hr cancellation required.
Escalate if: complaint, medical question, pricing negotiation, or >2 unanswered questions.
"""

SYSTEM_PROMPT = f"""
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
"""

# 3. Core Agent Logic
class BloomAgent:
    def __init__(self):
        self.chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.is_escalated = False

    def process_message(self, user_input: str) -> str:
        """Stages 1 & 2: FAQ Answering and Lead Qualification"""
        self.chat_history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini", 
            messages=self.chat_history,
            temperature=0.2
        )
        
        ai_message = response.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": ai_message})
        
        return self.check_escalation(ai_message)

    def check_escalation(self, ai_message: str) -> str:
        """Stage 3: Detects if the LLM flagged an escalation."""
        if "[ESCALATE" in ai_message:
            self.is_escalated = True
        return ai_message

    def generate_summary(self) -> str:
        """Stage 4: Generate a structured JSON summary of the session."""
        summary_prompt = {
            "role": "user",
            "content": "The conversation has ended. Please provide a JSON summary with the following keys: 'customer_intent', 'key_details_collected' (list), 'sop_gaps_identified' (if any), and 'recommended_next_action'."
        }
        
        temp_history = self.chat_history + [summary_prompt]
        
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=temp_history,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        return response.choices[0].message.content


# 4. Streamlit User Interface
st.set_page_config(page_title="Closira Support Agent", page_icon="🌸")
st.title("🌸 Bloom Aesthetics Support")
st.markdown("Powered by OpenRouter & Streamlit | **Closira Assignment**")

# Initialize the agent in Streamlit's session state so it persists across reruns
if "agent" not in st.session_state:
    st.session_state.agent = BloomAgent()

# Display chat history (excluding the hidden system prompt)
for msg in st.session_state.agent.chat_history:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Chat Input & Logic
if not st.session_state.agent.is_escalated:
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Display user message instantly
        with st.chat_message("user"):
            st.markdown(user_input)
            
        # Get and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Typing..."):
                reply = st.session_state.agent.process_message(user_input)
                st.markdown(reply)
                
        # Force a rerun to update the UI state
        st.rerun()
else:
    st.warning("⚠️ **Conversation Escalated.** A human agent will take over shortly.")

# Sidebar for Stage 4: Session Summary
with st.sidebar:
    st.header("Admin / Evaluation Tools")
    st.write("Use this panel to trigger the Stage 4 conversation summary.")
    
    if st.button("Generate Session Summary"):
        with st.spinner("Generating structured summary..."):
            summary_json = st.session_state.agent.generate_summary()
            
            # Safely parse and display the JSON
            try:
                parsed_summary = json.loads(summary_json)
                st.json(parsed_summary)
            except json.JSONDecodeError:
                st.error("Failed to parse JSON. Raw output:")
                st.code(summary_json)
                
    if st.button("Reset Session"):
        st.session_state.agent = BloomAgent()
        st.rerun()
