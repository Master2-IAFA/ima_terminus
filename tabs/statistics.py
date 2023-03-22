import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

STATS_PATH = "./data/statistics/"

def whole_network_stats():
    st.subheader("Whole network")
    tab1, tab2, tab3 = st.columns((1,1,1))
    tab1.caption("<center>Statistics about the whole network</center>", unsafe_allow_html=True)
    tab1.table(pd.read_csv(STATS_PATH+"whole_network/whole_network_stats.csv"))
    tab2.caption("<center>Statistics about the nodes</center>", unsafe_allow_html=True)
    tab2.table(pd.read_csv(STATS_PATH+"whole_network/nodes_stats.csv"))
    tab3.caption("<center>Statistics about the edges</center>", unsafe_allow_html=True)
    tab3.table(pd.read_csv(STATS_PATH+"whole_network/relations_stats.csv"))

@st.cache_resource
def event_network() :
    events = pd.read_csv(STATS_PATH+"events_network/events.csv", index_col=0)
    return events

@st.cache_resource
def event_category_network() :
    events = event_network()
    categories = events.drop(columns=["Event id", "TRECIS-ID"]).groupby("Event category").sum().reset_index().sort_values(by="% interactions", ascending=False)
    return categories

def category_network_stats():
    subnet = st.selectbox(
        "Select whether to study by category of event or by event",
        ("Category", "Event")
    )
    
    if subnet == "Event" :
        st.subheader("Event network")
        st.caption("<center>Statistics about the events</center>", unsafe_allow_html=True)
        st.dataframe(event_network(), use_container_width=True)

    else :
        st.subheader("Event category network")
        st.caption("<center>Statistics about the event categories</center>", unsafe_allow_html=True)
        st.dataframe(event_category_network(), use_container_width=True)


@st.cache_resource
def users_degree_distribution_fig():
    users_rel = pd.read_parquet(STATS_PATH+"users_network/users_rel.parquet")
    users_rel_common = users_rel.groupby(["source", "target"]).sum()

    counts_whole, bins = np.histogram(users_rel_common["weight"], bins=max(users_rel_common["weight"]))
    counts_retweet, bins = np.histogram(users_rel[users_rel["type"] == "RETWEETS"]["weight"], bins=bins)
    counts_reply, bins = np.histogram(users_rel[users_rel["type"] == "REPLIES_TO"]["weight"], bins=bins)
    counts_mentions, bins = np.histogram(users_rel[users_rel["type"] == "MENTIONS"]["weight"], bins=bins)

    fig = go.Figure()
    fig.add_scatter(x=bins[:-1], y=counts_whole, mode="markers", name="All interactions")
    fig.add_scatter(x=bins[:-1], y=counts_retweet, mode="markers", name="Retweet")
    fig.add_scatter(x=bins[:-1], y=counts_mentions, mode="markers", name="Mentions")
    fig.add_scatter(x=bins[:-1], y=counts_reply, mode="markers", name="Reply")

    fig.update_layout(
        # title="Degree distribution of the users obtained from the graph data",
        xaxis_title="Degree",
        yaxis_title="Count",
        xaxis_type="log",
        yaxis_type="log",
        template="plotly_white",
        autosize=False,
        width=600,
        height=500,
    )

    return fig

@st.cache_resource
def users_real_degree_distribution_fig():
    users = pd.read_parquet(STATS_PATH+"users_network/users.parquet")
    bins = np.linspace(0, 10**6, 100000)

    counts_friends_real, _ = np.histogram(users["friends_count"], bins=bins)
    counts_tweets_real, _ = np.histogram(users["tweets_count"], bins=bins)
    counts_listed_real, _ = np.histogram(users["listed_count"], bins=bins)
    counts_statuses_real, _ = np.histogram(users["statuses_count"], bins=bins)
    counts_favourites_real, _ = np.histogram(users["favourites_count"], bins=bins)
    counts_followers_real, _ = np.histogram(users["followers_count"], bins=bins)
    
    fig = go.Figure()
    fig.add_scatter(x=bins[:-1], y=counts_friends_real, mode="markers", name="Friends", )
    fig.add_scatter(x=bins[:-1], y=counts_tweets_real, mode="markers", name="Tweets")
    fig.add_scatter(x=bins[:-1], y=counts_listed_real, mode="markers", name="Listed")
    fig.add_scatter(x=bins[:-1], y=counts_statuses_real, mode="markers", name="Statuses")
    fig.add_scatter(x=bins[:-1], y=counts_favourites_real, mode="markers", name="Favourites")
    fig.add_scatter(x=bins[:-1], y=counts_followers_real, mode="markers", name="Followers")
    
    fig.update_layout(
        # title="Real degree distribution of the users in the dataset",
        xaxis_title="Degree",
        yaxis_title="Count",
        xaxis_type="log",
        yaxis_type="log",
        template="plotly_white",
        autosize=False,
        width=600,
        height=500,
    )

    return fig




def users_network_stats():
    st.subheader("Users network")

    st.caption("<center>Statistics about the users network</center>", unsafe_allow_html=True)
    st.dataframe(pd.read_csv(STATS_PATH+"users_network/users_network.csv"), use_container_width=True, height = 457)

    # add graphs side by side
    tab1, _, tab2= st.columns((.4, .1, .4))

    tab1.plotly_chart(users_degree_distribution_fig())
    tab1.caption("<center>Degree distribution of the users obtained from the graph data</center>", unsafe_allow_html=True)

    tab2.plotly_chart(users_real_degree_distribution_fig())
    tab2.caption("<center>Real degree distribution of the users in the dataset</center>", unsafe_allow_html=True)

    # add an empty line
    st.markdown("")
    st.write("All the distributions follow a powerlaw")
    

@st.cache_resource
def likes_distribution_fig() :
    counts, bins = np.histogram(pd.read_csv(STATS_PATH+"tweets_network/likes.csv")["favorite_count"], bins=np.linspace(0, 10**4, 10000))

    fig = go.Figure()

    fig.add_scatter(x=bins[:-1], y=counts, mode="markers")

    fig.update_layout(
        title="Distribution of the number of likes",
        xaxis_title="Number of likes",
        yaxis_title="Count",
        xaxis_type="log",
        yaxis_type="log",
        template="plotly_white",
        autosize=False,
        width=600,
        height=500,
    )

    return fig

@st.cache_resource
def degree_distribution_fig() :
    degree_distrib = pd.read_csv(STATS_PATH+"tweets_network/degree_distrib.csv")
    fig = go.Figure()
    fig.add_scatter(x=degree_distrib["degree"], y=degree_distrib["count"], mode="markers")

    fig.update_layout(
        title="Degree distribution from the graph data",
        xaxis_title="Degree",
        yaxis_title="Count",
        xaxis_type="log",
        yaxis_type="log",
        template="plotly_white",
        autosize=False,
        width=600,
        height=500,
    )

    return fig


def tweets_network_stats():
    st.subheader("Tweets network")

    st.caption("<center>Statistics about the tweets network</center>", unsafe_allow_html=True)
    st.dataframe(pd.read_csv(STATS_PATH+"tweets_network/tweets_network.csv"), use_container_width=True)
    
    st.caption("<center>Statistics about the tweets likes</center>", unsafe_allow_html=True)
    st.dataframe(pd.read_csv(STATS_PATH+"tweets_network/likes_stats.csv"), use_container_width=True)

    tab1, _, tab2= st.columns((.4, .1, .4))

    tab1.plotly_chart(likes_distribution_fig())
    tab2.plotly_chart(degree_distribution_fig())

    st.markdown("")
    st.write("All the distributions follow a powerlaw")
    

def run_page() :
    st.title("Statistics Page")
    st.header("Basic statistics")
    st.write("This is the statistics page, you can find some basic statistics about the data here.")
    # ajouter un menu déroulant pour choisir le sous-réseau à étudier
    subnet = st.selectbox(
        "Select the subnetwork to study",
        ("Whole network", "Event/Category network", "Users network", "Tweets network")
    )

    if subnet == "Whole network" :
        whole_network_stats()

    elif subnet == "Event/Category network" :
        category_network_stats()

    elif subnet == "Users network" :
        users_network_stats()

    elif subnet == "Tweets network" :
        tweets_network_stats()

    else :
        st.write("Error")