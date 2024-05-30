# Learning and Quiz Application

This application is built with Streamlit and integrates Google Cloud BigQuery, OpenAI and Langchain to facilitate both learning and testing knowledge. It provides two main functionalities: answering user questions based on a specific topic or uploaded documents using a RAG system, and a quiz section where users can test their knowledge.

## Features

- **Learning Page**: Users can study by asking questions. The application uses a RAG system to generate answers based on the topic or content of uploaded documents.
- **Quiz Page**: Users can test their knowledge through a quiz that generates questions based on a selected topic or uploaded documents.
- **Dynamic Content Generation**: Leverages the capabilities of language models to generate and evaluate content dynamically.

## Setup
- Clone repository: `git clone https://github.com/bakaydmytro/learn_chat`
- Install dependency
- Configure `.env` variables
- Google Cloud Auth: `gcloud auth application-default login`
- Run app: `streamlit run Summary.py`
