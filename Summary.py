import streamlit as st
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from sidebar import init_sidebar
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = OpenAI(api_key=OPENAI_API_KEY)


@st.cache_data
def fetch_summary(topic, file_path):
    return get_summary(topic, file_path)


def main():
    if "quiz_started" not in st.session_state:
        st.session_state["quiz_started"] = False
    if "topic_submitted" not in st.session_state:
        st.session_state["topic_submitted"] = False
    if "file_path" not in st.session_state:
        st.session_state["file_path"] = ""
    if "quiz_level" not in st.session_state:
        st.session_state["quiz_level"] = "Easy"
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    st.set_page_config(page_title="Summary", page_icon="📈")

    st.title("Learning")

    init_sidebar()

    if st.session_state["topic_submitted"]:
        summary = fetch_summary(
            st.session_state["submitted_topic"], st.session_state["file_path"]
        )
        st.write(summary)
        if "last_response" in st.session_state and st.session_state["last_response"]:
            st.write("Response:", st.session_state["last_response"])

        question = st.text_input(
            "Ask a question about the summary:", key="summary_question"
        )

        if st.button("Submit Question", key="submit_summary_question"):
            response = generate_response(question, st.session_state["submitted_topic"])
            st.session_state["last_response"] = response
            st.rerun()

    else:
        st.write(
            "This section provides a short summary for the provided topic or document."
        )


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


def get_summary(topic, file_path):
    if topic and not file_path:
        template = "Provide 150 words summary for provided topic: {topic}"
        prompt = PromptTemplate.from_template(template)
        llm_chain = prompt | llm
        return llm_chain.invoke(topic)
    elif not topic and file_path:
        return "File summary"
    else:
        return "Error"


def generate_response(question, topic):
    template = """Provide answer for question with related topic
    Question: {question}
    Topic: {topic}"""
    prompt = PromptTemplate.from_template(template)
    llm_chain = prompt | llm
    return llm_chain.invoke({"question": question, "topic": topic})


if __name__ == "__main__":
    main()
