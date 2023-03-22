import streamlit as st

TRECIS_URL = "https://www.dcs.gla.ac.uk/~richardm/TREC_IS/"

def run_page() :
    st.title("Home Page")
    st.write("This is the home page, you can find some information about the project and the data here.")
    st.header("Project")
    st.write("This project is part of the course 'Chef d'Oeuvre' at the Paul Sabatier University.")
    st.write("The objective of this project is to design a dashboard that can describe, query, and mine the TRECIS dataset along with the network it depicts.")

    st.header("Data")
    
    st.write(f"""The TRECIS (Text REtrieval Conference Information Seeking) dataset is a collection of social media posts and corresponding annotations related to natural disasters, crises, and events. It was created for the purpose of information retrieval and classification tasks, and has been used in various research projects related to crisis informatics, natural language processing, and machine learning.

The dataset contains social media posts from Twitter, along with associated metadata such as timestamp and user information. The posts are related to a variety of events, including natural disasters, terrorist attacks, and political crises. Some posts has been manually annotated with labels indicating its relevance, credibility, and other characteristics.

The TRECIS dataset has been used in a number of research studies and competitions, including the TREC-IS track at the Text Retrieval Conference (TREC). The dataset is publicly available and can be accessed through the [TRECIS website]({TRECIS_URL}).""")
    
    # display image of graph :
    col1, col2, col3 = st.columns([1,2,1], )
    col2.image("data/imgs/graph_struct.png", use_column_width=True, caption="Network architecture of the TREC-IS dataset")
