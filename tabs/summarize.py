import streamlit as st
from utils import text_mining
from utils.ChatGPT import ask_ChatGPT


def summarize(query_result, text_column, summarization_method):
    result = ""
    if summarization_method == "T5" :
        sentences = query_result[text_column]
        with st.spinner("Summarizing tweets using T5-base..."):
            result = text_mining.abstractive_summarization(sentences)
    elif summarization_method == "ChatGPT" :
        sentences = query_result[text_column]
        with st.spinner("Asking ChatGPT to summarize the tweets..."):
            result = ask_ChatGPT.summarize(sentences)
    elif summarization_method == "LEAD-3" :
        sentences = query_result[text_column]
        result = "\n\n".join(sentences[:3]) # LEAD-3 is the first 3 sentences/tweets
    return result


def run_page():
    st.title("Summarize Page")

    if st.session_state.get("query_result", None) is None :
        st.write("You need to run a query first.")
    elif st.session_state.get("query_text_columns", None) is None or len(st.session_state["query_text_columns"]) == 0 :
        st.write("The query you ran does not contain any text column.")
    else :
        st.subheader("Query result")
        st.dataframe(st.session_state["query_result"], use_container_width=True)
        
        # add a dropdown menu to select the text column
        text_column = st.selectbox(
            "Select the text column to summarize",
            st.session_state["query_text_columns"]
        )

        # add a dropdown menu to select the method to use for summarization
        summarization_method = st.selectbox(
            "Select the method to use for summarization (ChatGPT gives the best results)",
            ("ChatGPT", "T5", "LEAD-3")
        )

        # add a button to run automatic summarization
        if st.button("Run automatic summarization") :
            result = summarize(st.session_state["query_result"], text_column, summarization_method)
        
            # Display the result of the summarization in a text area
            st.subheader("Summary")
            st.text_area(label=f"{summarization_method} summary :", value=result, height=200)