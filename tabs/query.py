from time import time

import pandas as pd
import streamlit as st
import torch
from streamlit_ace import st_ace
from utils import neo4j, text_mining

graph = neo4j.connect()
pd.set_option('display.max_colwidth', None)

st.session_state["query_result"] = None
st.session_state["query_text_columns"] = None

preset_query_1 = '''
MATCH 
    (t:Tweet)-->(h:Hashtag), 
    (u:User)-[POSTED]->(t:Tweet) 
WHERE 
    h.id = "ymm" 
RETURN 
    u.screen_name, 
    t.retweet_count, 
    t.favorite_count, 
    t.text as text
ORDER BY t.favorite_count DESC
'''

preset_query_2 = '''
MATCH 
    (t:Tweet)-->(h1:Hashtag),
    (t:Tweet)-->(h2:Hashtag),
    (u:User)-[POSTED]->(t:Tweet)
WHERE 
    h1.id = "ymmfire" 
    AND 
    h2.id = "ymm"
RETURN 
    u.screen_name, 
    t.retweet_count, 
    t.favorite_count, 
    t.text as text
ORDER BY t.favorite_count DESC
'''


def preset_queries() :
    st.subheader("Preset queries")
    # add a dropdown menu to select the preset query
    query_name = st.selectbox(
        "Select the preset query",
        ("Tweets containing the hashtag \"#ymm\"", "Tweets containing the hashtag \"#ymmfire\" and the hashtag \"#ymm\"")

    )
    query = ""
    if query_name == "Tweets containing the hashtag \"#ymm\"" :
        query = preset_query_1
    elif query_name == "Tweets containing the hashtag \"#ymmfire\" and the hashtag \"#ymm\"" :
        query = preset_query_2
    
    return query


def filtered_queries() :
    st.subheader("Filtered queries")
    # add multiselect
    hashtags, _ = neo4j.run_query(graph, "MATCH (h:Hashtag) RETURN h.id as hashtag")
    # extract the hashtags from the dataframe and sort
    hashtags = hashtags["hashtag"].tolist()
    hashtags.sort()
    st.write("Select the hashtags that need to be included in the tweets (AND condition)")
    selected_hashtags = st.multiselect("Hashtags", hashtags, key="selected_hashtags")
    st.write("Select the hashtags to exclude")
    excluded_hashtags = st.multiselect("Hashtags", hashtags, key="excluded_hashtags")

    # add a text input to enter the text to search for
    st.write("Enter the text to search for in the tweets (word for word search, leave empty if no restriction)")
    text_to_search = st.text_input("Text to search for", value="")
    
    # add a multiselect to select the users to filter the tweets
    users, _ = neo4j.run_query(graph, "MATCH (u:User) RETURN u.screen_name as user")
    users = users["user"].tolist()
    users.sort()
    st.write("Select the users that need to have posted the tweets (leave empty if no restriction)")
    selected_users = st.multiselect("Users", users, key="selected_users")
    st.write("Select the users to exclude (leave empty if no restriction)")
    excluded_users = st.multiselect("Users", users, key="excluded_users")

    # add a multiselect to select the event to filter the tweets
    events, _ = neo4j.run_query(graph, "MATCH (e:Event) RETURN e.id as event")
    events = events["event"].tolist()
    events.sort()
    st.write("Select the events of the tweets (leave empty if no restriction)")
    selected_events = st.multiselect("Events", events, key="selected_events")
    st.write("Select the events to exclude (leave empty if no restriction)")
    excluded_events = st.multiselect("Events", events, key="excluded_events")

    # add a multiselect to select the event type to filter the tweets
    event_types, _ = neo4j.run_query(graph, "MATCH (e:Event) RETURN distinct e.eventType as event_type")
    event_types = event_types["event_type"].tolist()
    event_types.sort()
    st.write("Select the event types of the tweets (leave empty if no restriction)")
    selected_event_types = st.multiselect("Event types", event_types, key="selected_event_types")
    st.write("Select the event types to exclude (leave empty if no restriction)")
    excluded_event_types = st.multiselect("Event types", event_types, key="excluded_event_types")

    # add number input to select the minimum number of interactions
    st.write("Select the minimum number of interactions (leave empty if no restriction, one interaction = one retweet or one like)")
    min_interactions = st.number_input("Minimum number of interactions", value=0, min_value=0, max_value=2244669, step=1)
    # add number input to select the maximum number of interactions
    st.write("Select the maximum number of interactions (leave empty if no restriction)")
    max_interactions = st.number_input("Maximum number of interactions", value=2244669, min_value=0, max_value=2244669, step=1)


    # add number of tweets to display
    st.write("Select the number of tweets to display")
    number_of_tweets = st.number_input("Number of tweets", value=20, min_value=1, max_value=55986, step=1)

    # add a checkbox to select by which order the tweets need to be sorted
    st.write("Select the order of the tweets (sorted by the number of interactions)")
    order = st.selectbox(
        "Select the order",
        ("None", "Ascending", "Descending")
    )


    def add_to_where_query(where_query, condition) :
        if not where_query.endswith("where ") :
            where_query += f"AND\n"
        where_query += condition
        return where_query


    # create a query based on the selected options
    match_query = "match (t:Tweet)"
    where_query = "where "
    order_query = ""
    # add the hashtags
    for i, hashtag in enumerate(selected_hashtags) :
        match_query += f", (h_included_{i}:Hashtag)"
        where_query = add_to_where_query(where_query, f"h_included_{i}.id = \"{hashtag}\" and (t)-->(h_included_{i}) ")
    for i, hashtag in enumerate(excluded_hashtags) :
        match_query += f", (h_excluded_{i}:Hashtag)"
        where_query = add_to_where_query(where_query, f"h_excluded_{i}.id = \"{hashtag}\" and not (t)-->(h_excluded_{i}) ")
    
    # add the text to search for
    if text_to_search != "" :
        where_query = add_to_where_query(where_query, f"t.text contains \"{text_to_search}\"")

    # add the users
    for i, user in enumerate(selected_users) :
        match_query += f", (u_included_{i}:User)"
        where_query = add_to_where_query(where_query, f"u_included_{i}.screen_name = \"{user}\" and (t)<--(u_included_{i}) ")
    for i, user in enumerate(excluded_users) :
        match_query += f", (u_excluded_{i}:User)"
        where_query = add_to_where_query(where_query, f"u_excluded_{i}.screen_name = \"{user}\" and not (t)<--(u_excluded_{i}) ")

    # add the events
    for i, event in enumerate(selected_events) :
        match_query += f", (e_included_{i}:Event)"
        where_query = add_to_where_query(where_query, f"e_included_{i}.id = \"{event}\" and (t)-->(e_included_{i}) ")
    for i, event in enumerate(excluded_events) :
        match_query += f", (e_excluded_{i}:Event)"
        where_query = add_to_where_query(where_query, f"e_excluded_{i}.id = \"{event}\" and not (t)-->(e_excluded_{i}) ")

    # add the event types
    for i, event_type in enumerate(selected_event_types) :
        match_query += f", (et_included_{i}:Event)"
        where_query = add_to_where_query(where_query, f"et_included_{i}.eventType = \"{event_type}\" and (t)-->(et_included_{i}) ")
    for i, event_type in enumerate(excluded_event_types) :
        match_query += f", (et_excluded_{i}:Event)"
        where_query = add_to_where_query(where_query, f"et_excluded_{i}.eventType = \"{event_type}\" and not (t)-->(et_excluded_{i}) ")

    # add the minimum number of interactions
    if min_interactions != 0 :
        where_query = add_to_where_query(where_query, f"t.retweet_count + t.favorite_count >= {min_interactions} ")
    # add the maximum number of interactions
    if max_interactions != 2244669 :
        where_query = add_to_where_query(where_query, f"t.retweet_count + t.favorite_count <= {max_interactions} ")
    
    # add the order
    if order == "Ascending" :
        order_query = "order by t.retweet_count + t.favorite_count asc"
    elif order == "Descending" :
        order_query = "order by t.retweet_count + t.favorite_count desc"
    
    # add the limit
    limit_query = f"limit {number_of_tweets}"

    # create the query
    query = f"{match_query}\n"
    if where_query != "where " :
        query += f"{where_query}\n"
    query += f"with distinct t\n"
    query += f"return t.text as text\n"
    if order_query != "" :
        query += f"{order_query}\n"
    query += f"{limit_query}"
    print(query)

    return query

def text_query() :
    st.subheader("Text query")
    query = st.text_area("Enter your query here", value="", height=300)
    # 
    return query

def cypher_query() :
    st.subheader("Cypher query")
    query = ""
    query = st_ace(auto_update=True, theme="github")
    return query


def run_query(query) :
    # display the query but default to not show it
    show_query = st.checkbox("Show generated query", value=False)
    if show_query :
        st.write(f"Query :\n```cypher\n{query}\n```")
    # run the query and display the result only if the button is clicked
    result = None
    if st.button("Run query") :
        with st.spinner("Running query..."):
            result, execution_time = neo4j.run_query(graph, query)
            st.write(f"Query executed in {execution_time:.0f} ms")
        with st.spinner("Formatting result..."):
            st.subheader("Result")
            st.dataframe(result, use_container_width=True)
        st.session_state["query_result"] = result
    return result

def text_query() :
    st.subheader("Search tweets")
    text_to_compare_to = st.text_input("Enter the text you want to search for", value="")
    if text_to_compare_to != "" :
        return text_to_compare_to

@st.cache_data 
def get_similar_tweets(text_to_compare_to, top_n=20) :
    query = f'''
    MATCH
        (t:Tweet)
    return 
        t.id as id,
        t.text as text,
        t.text_embedding as text_embedding
    '''
    result, execution_time = neo4j.run_query(graph, query)
    start = time()
    with st.spinner(f"Getting the {top_n} most similar tweets...") :
        result["text_embedding"] = result["text_embedding"].apply(lambda x: torch.tensor(x))
    
        query_embedding = text_mining.get_embedding(f'query: {text_to_compare_to}').reshape(-1)

        with st.spinner(f"Comparing the tweets to the query...") :
            result["similarity_to_query"] = result["text_embedding"].apply(lambda x: torch.cosine_similarity(x, query_embedding, dim=0))
            
        result = result.sort_values(by="similarity_to_query", ascending=False)
        result = result.drop(columns=["text_embedding"])

    execution_time = execution_time + time() - start
    st.write(f"Query executed in {execution_time/1000:.0f} s")
    if top_n > 0 :
        result = result.iloc[:min(top_n, len(result))]
    st.subheader("Result")
    st.dataframe(result, use_container_width=True)
    st.session_state["query_result"] = result
    return result


def run_page() :
    st.title("Query")
    st.write("This is the query page, you can query the database here.")
    # add a dropdown menu to select the type of query (preset queries, custom query, etc.)
    query_type = st.selectbox(
        "Select the type of queries you want to run",
        ("Preset queries", "Filtered queries", "Custom query", "Search tweets"),
    )
    
    result = None
    query = None
    if query_type == "Preset queries" :
        query = preset_queries()
    elif query_type == "Filtered queries" :
        query = filtered_queries()
    elif query_type == "Custom query" :
        query = cypher_query()
    elif query_type == "Search tweets" :
        # add slider to select the number of tweets to return
        text_to_compare_to = text_query()
        check_full_text = st.checkbox("return all the tweets", value=False)
        top_n = -1
        if not check_full_text :
            top_n = st.slider("Select the number of tweets to return", min_value=5, max_value=100, value=20)
        if st.button("Search") :
            result = get_similar_tweets(text_to_compare_to, top_n=top_n)

    if query_type != "Search tweets" and query is not None :
        result = run_query(query)
    
    if result is not None :
        text_columns = [c for c in result.columns if c.lower().endswith("text") or c.lower().endswith("tweet")]
        st.session_state["query_text_columns"] = text_columns
        if len(text_columns) > 0 :
            st.write("This query contains text columns, you can run **automatic summarization** on it.")
            st.write("To do so, go to the **Summarization** page.")
        # st.subheader("")
