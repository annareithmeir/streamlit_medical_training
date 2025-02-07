import streamlit as st
import requests
import fitz

def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")  # Read PDF
    for page in doc:
        pdf_text += page.get_text() + "\n"
    return pdf_text.strip()

def query_model(prompt, context=""):
    headers = {"Authorization": f"Bearer {st.session_state.hf_api_key}"}
    full_prompt = f"Context: {context}\n\nUser: {prompt}\n\nBot:"
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 200}}

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{MODEL_NAME}",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        generated_text = response.json()[0]["generated_text"]

        # Remove the user's input from the model's response
        if generated_text.startswith(prompt):
            return generated_text[len(prompt):].strip()
        return generated_text.strip()
    else:
        return f"Error: {response.json()}"

# Hugging Face API settings
#HF_API_KEY = st.secrets["hf_key"]
MODEL_NAME = "google/gemma-2-2b-it"  # Change to other models if needed
#MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
#PDF_PATH = "/home/anna/Downloads/Basiswissen Allgemeinmedizin-1.pdf"
#HF_API_URL = "https://api-inference.huggingface.co/models/deepseek/deepseek-chat"

#  Sidebar for file upload and system prompt
st.sidebar.title("Setup Menu")

# API Key Input
hf_api_key = st.sidebar.text_input("Hugging Face API Key")
apply_key = st.sidebar.button("Apply")

# Store API key and status in session state
if "hf_api_key" not in st.session_state:
    st.session_state.hf_api_key = None
if "api_key_applied" not in st.session_state:
    st.session_state.api_key_applied = False

if apply_key:
    st.session_state.hf_api_key = hf_api_key
    st.session_state.api_key_applied = True
    st.sidebar.write("✅ Key Applied")

st.sidebar.markdown("---")
instruction = st.sidebar.text_area("Enter an initial system prompt")
instruction_apply_key = st.sidebar.button("Upload instruction")

if instruction_apply_key:
    st.session_state.instruction_applied = True
    st.session_state.context = f"System Prompt: {instruction}"
    print(st.session_state.context)
    st.sidebar.write("✅ Instruction uploaded")

st.sidebar.markdown("---")

context_file = st.sidebar.file_uploader("knowledge database PDF file", type=["pdf"])
apply_context = st.sidebar.button("Upload Context")

# # Store context status
# if "context" not in st.session_state:
#     st.session_state.context_applied = False

# Save context in session state
if apply_context:
    pdf_text = extract_text_from_pdf(context_file)
    print(pdf_text[:500])
    st.session_state.context = st.session_state.context + f"\nFile Content: {pdf_text}"
    st.session_state.context_applied = True
    st.sidebar.write("✅ Context uploaded")

# Streamlit UI
st.title("🗨️ Patient Simulator")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align: right; background-color: #6082B6; padding: 10px; border-radius: 10px; max-width: 60%; margin-left: auto;'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='padding: 10px; border-radius: 10px; max-width: 80%;'>{msg['content']}</div>", unsafe_allow_html=True)

# User input
if user_input := st.chat_input("Type your message..."):
    if not st.session_state.context:
        st.warning("No context file used.")
    if not st.session_state.hf_api_key:
        st.warning("Please enter and apply a valid Hugging Face API key.")
    else:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": "Doctor:   " + user_input})

        # Get model response using PDF content
        response = query_model(user_input, context=st.session_state.context)

        # Add model response to history
        st.session_state.messages.append({"role": "bot", "content": response})

        # Refresh the page to display messages correctly
        st.rerun()
