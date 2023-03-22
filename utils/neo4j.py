from py2neo import Graph
import streamlit as st
from time import time

def connect(username = "neo4j", password = "Twitter"):
    graph = Graph("bolt://localhost:7687", auth=(username, password))
    return graph

@st.cache_data
def run_query(_graph, query): # Use of "_" before the variable name because is cannot be cashed by streamlit and using the "_" disables the cashing for this variable
    # get query result and execution time
    start = time()
    results = _graph.run(query)
    end = time()
    execution_time = (end - start) * 1000
    return results.to_data_frame(), execution_time
