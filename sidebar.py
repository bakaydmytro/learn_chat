import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import get_store
import os

store = get_store()


def process_uploaded_file(uploaded_file):
    if uploaded_file:
        upload_dir = "./upload/"
        os.makedirs(upload_dir, exist_ok=True)
        temp_file_path = os.path.join(upload_dir, uploaded_file.name)
        print("File path:", temp_file_path)
        with open(temp_file_path, "wb") as file:
            file.write(uploaded_file.getvalue())
        return temp_file_path
    else:
        print("No file uploaded.")
        return None


def split_documents(file_path):
    loader = PyPDFLoader(file_path)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return text_splitter.split_documents(data)


def init_sidebar():
    with st.sidebar:
        st.session_state["topic"] = st.text_input(
            "Enter a topic or upload a document:",
            key="topic_input",
            value=st.session_state.get("topic", ""),
        )
        if "file_name" in st.session_state:
            st.success(f"✔️ File uploaded: {st.session_state['file_name']}")
        else:
            uploaded_file = st.file_uploader("Upload file", type=["pdf"])
            if uploaded_file:
                file_path = process_uploaded_file(uploaded_file)
                if file_path:
                    st.session_state["file_path"] = file_path
                    st.session_state["file_name"] = uploaded_file.name

                    texts = split_documents(file_path)
                    store.add_documents(texts)
