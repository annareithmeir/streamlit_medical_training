import streamlit as st
import requests
import fitz

# Hugging Face API settings
HF_API_KEY = st.secrets["hf_key"]
MODEL_NAME = "google/gemma-2-2b-it"  # Change to other models if needed

#PDF_PATH = "/home/anna/Downloads/Basiswissen Allgemeinmedizin-1.pdf"

# Function to extract text from PDF
# def extract_text_from_pdf(pdf_path):
#     pdf_text = ""
#     doc = fitz.open(pdf_path)  # Open the PDF from file path
#     for page in doc:
#         pdf_text += page.get_text() + "\n"
#     print("Successfully extracted text from pdf file. Length of text:", len(pdf_text))
#     return pdf_text.strip()

def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")  # Read PDF
    for page in doc:
        pdf_text += page.get_text() + "\n"
    return pdf_text.strip()

# Function to query Hugging Face API
def query_model(prompt, context=""):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
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


# Extract text from the specified PDF
#pdf_text = extract_text_from_pdf(PDF_PATH)

# Streamlit UI
st.title("🗨️ Patient Simulator")

# Display PDF filename as a subtitle
#st.subheader(f"(Uploaded: {PDF_PATH})")

# PDF Upload
pdf_text = ""
pdf_file = st.file_uploader("Upload a PDF file", type="pdf")
if pdf_file:
    pdf_text = extract_text_from_pdf(pdf_file)
    st.success("PDF uploaded and processed!")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input
if user_input := st.chat_input("Type your message..."):
    st.session_state.messages.append(("user", user_input))

    # Get model response using PDF content
    response = query_model(user_input, context=pdf_text)
    st.session_state.messages.append(("bot", response))

# Display messages side by side
for role, text in st.session_state.messages:
    col1, col2 = st.columns([1, 1])  # Two equal columns

    if role == "user":
        with col1:
            st.markdown(f"<div style='text-align: left; padding: 8px; background-color: #424242; border-radius: 10px; width: fit-content;'>{text}</div>", unsafe_allow_html=True)
        with col2:
            st.write("")  # Empty to keep alignment
    else:
        with col1:
            st.write("")  # Empty for alignment
        with col2:
            st.markdown(f"<div style='text-align: right; padding: 8px; background-color: #1E88E5; border-radius: 10px; width: fit-content;'>{text}</div>", unsafe_allow_html=True)
