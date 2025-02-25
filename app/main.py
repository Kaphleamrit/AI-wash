import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
from io import BytesIO
import re  # For cleaning text

# Load environment variables
load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)

# Set page configuration with a modern layout
st.set_page_config(
    page_title="AI Wash Service",
    page_icon="🤖",
    layout="wide"
)

# Apply custom CSS for a modern look
st.markdown("""
    <style>
        /* General page styling */
        body {
            background-color: #f0f2f6;
            color: #333;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Title and subtitle styling */
        h1, h3 {
            color: #2c3e50;
            text-align: center;
            font-weight: 600;
        }

        /* Paragraph styling */
        p {
            color: #34495e;
            text-align: center;
            font-size: 1.1rem;
        }

        /* File uploader styling */
        .stFileUploader label {
            color: #2980b9;
            font-weight: bold;
        }

        /* Button styling */
        .stButton button {
            background-color: #3498db;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1rem;
            transition: background-color 0.3s ease;
        }
        .stButton button:hover {
            background-color: #2980b9;
        }

        /* Text area styling */
        .stTextArea textarea {
            border-radius: 5px;
            border: 1px solid #bdc3c7;
        }

        /* Footer styling */
        footer {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

# Title and description with a modern UI
st.title("🚀 AI Wash Service")
st.markdown("""
    <p>
        This app helps you process and refine your documents using AI. Upload a file and let AI enhance its content!
    </p>
""", unsafe_allow_html=True)

# File uploader for TXT, DOCX, PDF
st.markdown("<h3>📤 Upload Your Document</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=['txt', 'pdf', 'docx'])

def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    reader = PdfReader(file)
    text = "\n".join([page.extract_text() or "" for page in reader.pages])
    return text.strip()

def extract_text_from_docx(file):
    """Extract text from a DOCX file."""
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

content = ""

if uploaded_file is not None:
    # Display the file name
    st.markdown(f"<p>📄 Uploaded file: <b>{uploaded_file.name}</b></p>", unsafe_allow_html=True)

    # Read file content based on file type
    if uploaded_file.type == "text/plain":
        content = uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        content = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        content = extract_text_from_docx(uploaded_file)
    else:
        st.warning("⚠ Unsupported file type.")

    # Display extracted content preview
    if content:
        with st.expander("📄 Preview Extracted File Content", expanded=True):
            st.text_area("File Content Preview", content, height=250)

# If there's content, send it to AI model for enhancement
enhanced_content = ""

if content:
    st.markdown("---")
    st.markdown("<h3>✨ AI-Enhanced Content</h3>", unsafe_allow_html=True)

    system_prompt = """You are an exceptional writer with expertise in crafting formal, informative, and engaging articles and papers. Your task is to refine and enhance the provided content, ensuring it is clear, well-structured, and compelling while maintaining a professional and authoritative tone. You follow a step-by-step approach, improving coherence, depth, and readability. Remove any redundancies, vague statements, or filler content, and focus on delivering well-structured, factually accurate, and insightful writing that captivates the reader while effectively conveying key ideas with precision and clarity.
    Don't write I've done this or that when you complete rewriting the article. Just respond with the content of the article, nothing else."""

    try:
        llm_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        )

        enhanced_content = llm_response.choices[0].message.content

        if enhanced_content:
            # Remove all asterisks from the response
            cleaned_content = re.sub(r"\*", "", enhanced_content)
            st.text_area("Enhanced AI Response", cleaned_content, height=250)
    except Exception as e:
        st.error(f"Error processing AI response: {str(e)}")

# Function to generate clean DOCX file
def generate_docx(text):
    """Generates a clean DOCX file from enhanced text content."""
    doc = Document()
    
    # Add a title
    title = doc.add_paragraph()
    title_run = title.add_run("AI-Enhanced Document")
    title_run.bold = True
    title.alignment = 1  # Center align
    
    doc.add_paragraph("\n")  # Add spacing
    
    # Process text into paragraphs
    paragraphs = text.split("\n\n")  # Split text by double new lines for paragraph separation
    for paragraph in paragraphs:
        if paragraph.strip():  # Ignore empty lines
            doc.add_paragraph(paragraph.strip())  # Add clean paragraph

    # Save DOCX to a BytesIO object
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Show download button if enhanced content is available
if enhanced_content:
    st.markdown("---")
    st.markdown("<h3>📥 Download AI-Enhanced Content</h3>", unsafe_allow_html=True)

    # Generate DOCX file with cleaned text (without `*`)
    cleaned_docx = generate_docx(re.sub(r"\*", "", enhanced_content))

    # Streamlit Download Button
    st.download_button(
        label="📄 Download as DOCX",
        data=cleaned_docx,
        file_name="Enhanced_Content.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

# Footer
st.markdown("---")  # Divider line
st.markdown(
    "<footer>Celly Services (CSI) 2025</footer>",
    unsafe_allow_html=True
)
