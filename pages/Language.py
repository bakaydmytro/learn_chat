import streamlit as st

with st.sidebar:
    st.session_state["native"] = st.selectbox(
        "Native language", ("English", "Ukrainian", "Spanish")
    )
    st.session_state["learn"] = st.selectbox(
        "Learning language", ("English", "Ukrainian", "Spanish")
    )
