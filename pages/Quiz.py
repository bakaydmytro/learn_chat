import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from sidebar import init_sidebar
from google.cloud import bigquery
import os
import logging
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET = os.getenv("DATASET")
TABLE = os.getenv("TABLE")
REGION = os.getenv("REGION")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(
    temperature=0.1, model_name="gpt-3.5-turbo-16k", openai_api_key=OPENAI_API_KEY
)
client = bigquery.Client(project=PROJECT_ID, location=REGION)
log = logging.getLogger(__name__)

st.set_page_config(page_title="Quiz", page_icon="📈")


init_sidebar()

if "quiz_started" not in st.session_state:
    st.session_state["quiz_started"] = False
if "file_path" not in st.session_state:
    st.session_state["file_path"] = ""
if "quiz_level" not in st.session_state:
    st.session_state["quiz_level"] = "Easy"
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "question_history" not in st.session_state:
    st.session_state["question_history"] = []
if "last_context" not in st.session_state:
    st.session_state["last_context"] = ""


def start_quiz(level):
    st.session_state["quiz_started"] = True
    st.session_state["quiz_level"] = level


def generative_ai_call(template, data):
    prompt = PromptTemplate.from_template(template)
    llm_chain = prompt | llm
    return llm_chain.invoke(data)


def generate_question_based_on_topic():
    level = st.session_state["quiz_level"]
    topic = st.session_state["topic"]
    history = st.session_state["question_history"]
    template = """Your role is to assess a student's knowledge.
        Generate a unique question for the specified topic and difficulty level. Ensure that the question is not repetitive or similar to those previously asked. The optional history of questions is provided to avoid redundancy.
        Topic: {topic}
        Difficulty Level: {level}
        History of Questions: {history}

        Example Questions:

        What is the capital of France?
        How do you define a variable in Python?"""
    response = generative_ai_call(
        template, {"topic": topic, "level": level, "history": history}
    )
    print(response.content)
    st.session_state["question_history"].append(response.content)
    return response.content


def get_text_context_for_document_question():
    query = f"""
        SELECT content
        FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
        ORDER BY RAND()
        LIMIT 1
    """
    query_job = client.query(query)
    results = query_job.result()

    for row in results:
        return row["content"]

    return None


def generate_question_based_on_document():
    context = get_text_context_for_document_question()
    level = st.session_state["quiz_level"]
    history = st.session_state["question_history"]
    template = """Your role is to assess a student's knowledge.
        Generate a unique question for the specified context and difficulty level. Ensure that the question is not repetitive or similar to those previously asked. The optional history of questions is provided to avoid redundancy.
        Context: {context}
        Difficulty Level: {level}
        History of Questions: {history}

        Example Questions:

        What is the capital of France?
        How do you define a variable in Python?"""
    response = generative_ai_call(
        template, {"context": context, "level": level, "history": history}
    )
    log.info(f"{template}\n +context:{context}\n")

    st.session_state["question_history"].append(response.content)
    st.session_state["last_context"] = context
    return response.content


def generate_question():
    if st.session_state["topic"]:
        return generate_question_based_on_topic()
    elif st.session_state["file_name"]:
        return generate_question_based_on_document()


def check_answer_based_on_topic():
    topic = st.session_state["topic"]
    question = st.session_state["question_history"][-1]
    answer = st.session_state["messages"][-1]
    template = """Your role is to evaluate a student's knowledge.
        Assess the correctness of the provided answer.
        After evaluating, give a brief explanation and the correct answer if the student's response is incorrect.
        Topic: {topic}
        Question: {question}
        Answer: {answer}

        Example Responses:

        Excellent, your answer is correct!
        Good attempt, but let's try to refine your understanding.
        Incorrect, the correct answer is...
    """
    result = generative_ai_call(
        template, {"topic": topic, "question": question, "answer": answer}
    )
    return result.content


def check_answer_based_on_document():
    context = st.session_state["last_context"]
    question = st.session_state["question_history"][-1]
    answer = st.session_state["messages"][-1]
    template = """Your role is to evaluate a student's knowledge.
        Assess the correctness of the provided answer.
        After evaluating, give a brief explanation and the correct answer if the student's response is incorrect.
        Context: {context}
        Question: {question}
        Answer: {answer}

        Example Responses:

        Excellent, your answer is correct!
        Good attempt, but let's try to refine your understanding.
        Incorrect, the correct answer is...
    """
    log.info(f"template: {template}\n +context: {context}\n +qestion: {question}")

    result = generative_ai_call(
        template, {"context": context, "question": question, "answer": answer}
    )
    return result.content


def check_answer():
    os.write(1, b"Checking answers.\n")
    if st.session_state["topic"]:
        return check_answer_based_on_topic()
    if st.session_state["file_name"]:
        return check_answer_based_on_document()


if not st.session_state["quiz_started"]:
    st.header("Welcome to the Quiz")
    level = st.selectbox("Choose the level:", ["Easy", "Mid", "Hard"])
    if st.button("Start Quiz"):
        start_quiz(level)
        st.session_state["quiz_level"] = level
        st.rerun()
else:
    st.write(f"Quiz started! Your selected level is {st.session_state['quiz_level']}.")

    if st.button("Restart"):
        st.session_state["quiz_started"] = False
        st.session_state["messages"] = []
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Write your answer here?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    if st.session_state["messages"]:
        result = check_answer()
        st.chat_message("administrator").markdown(result)
        st.session_state.messages.append({"role": "administrator", "content": result})
        question = generate_question()
        st.chat_message("administrator").markdown(question)
        st.session_state.messages.append({"role": "administrator", "content": question})

    if not st.session_state["messages"]:
        question = generate_question()
        st.chat_message("administrator").markdown(question)
        st.session_state.messages.append({"role": "administrator", "content": question})
