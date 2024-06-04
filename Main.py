import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from sidebar import init_sidebar
from dotenv import load_dotenv
from config import get_embedding, get_store
from langchain.chains.question_answering import load_qa_chain
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    temperature=0.1, model_name="gpt-3.5-turbo-16k", openai_api_key=OPENAI_API_KEY
)

embedding = get_embedding()
store = get_store()


def main():
    st.set_page_config(page_title="Main", page_icon="📈")

    st.title("Learn")

    init_sidebar()

    question = st.text_input("Enter your question", key="summary_question")

    if st.button("Submit Question", key="submit_summary_question"):
        response = generate_response(question)
        st.write(response)


def generative_ai_call(template, data):
    llm_chain = template | llm
    return llm_chain.invoke(data)


def generate_answer_based_on_topic(question, topic):
    template = PromptTemplate.from_template(
        """Provide answer for question with related topic.
    Question: {question}
    Topic: {topic}"""
    )
    response = generative_ai_call(template, {"question": question, "topic": topic})
    return response.content


def generate_answer_based_on_document(question):
    query_vector = embedding.embed_query(question)
    docs = store.similarity_search_by_vector(query_vector, k=2)
    result = chain.run(input_documents=docs, question=question)
    return result


def generate_response(question):
    if st.session_state["topic"]:
        return generate_answer_based_on_topic(question, st.session_state["topic"])
    if st.session_state["file_name"]:
        return generate_answer_based_on_document(question)


if __name__ == "__main__":
    main()
