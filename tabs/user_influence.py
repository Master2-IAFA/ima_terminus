import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = "./data/"

# @st.cache_resource
def user_influence_fig(ranked_users) :
    # color by "isVerified"
    fig = px.scatter(ranked_users, x="rank", y="InfRank",  hover_data=ranked_users.columns, color="isVerified")

    fig.update_layout(
        # title="InfRank vs rank",
        xaxis_title="Rank",
        yaxis_title="InfRank",
        xaxis_type="log",
        yaxis_type="log",
        template="plotly_white",
    )
    
    return fig


def run_page() :
    st.title("Users influence Page")
    st.header("Visualize the influence of users on the graph")

    ranked_users = pd.read_parquet(DATA_PATH+"users_influence/ranked_users.parquet")
    st.dataframe(ranked_users, use_container_width=True)
    
    st.plotly_chart(user_influence_fig(ranked_users), use_container_width=True)
    st.caption("<center>InfRank vs rank</center>", unsafe_allow_html=True)

    st.markdown("")
    st.write("The InfRank of the users is computed using the InfRank algorithm. The rank is the position of the user in the ranked list of users.")
    st.write("Surprisingly, the InfRank follows a powerlaw distribution.")

    st.subheader("Relations with other metrics")

    st.caption("<center>InfRank vs a number of other variables</center>", unsafe_allow_html=True)
    st.markdown("")
    tab1, tab2, tab3, tab4 = st.columns((.25, .25, .25, .25))
    # add images
    tab1.caption("<center>InfRank vs # followers</center>", unsafe_allow_html=True)
    tab1.image(DATA_PATH+"imgs/rank_vs_followers.png", use_column_width=True)
    tab2.caption("<center>InfRank vs # tweets</center>", unsafe_allow_html=True)
    tab2.image(DATA_PATH+"imgs/rank_vs_tweets.png", use_column_width=True)
    tab3.caption("<center>InfRank vs # following</center>", unsafe_allow_html=True)
    tab3.image(DATA_PATH+"imgs/rank_per_following.png", use_column_width=True)
    tab4.caption("<center>InfRank vs # likes</center>", unsafe_allow_html=True)
    tab4.image(DATA_PATH+"imgs/rank_vs_likes.png", use_column_width=True)
    st.markdown("")
    # explain
    st.write("The higher the rank, the more followers a user tend to have and the more tweets they tend to post.")
    st.write("The rank seems to not be correlated with the number of users a user is following. This could be explain by the fact that, as a user is more influent, they tend to follow less users but a user following more people tend to have a higher reach. With these effect counteracting each other, The absence of correlation is not surprising.")
    st.write("Surprisingly, the total number of likes an account has does not have an influence on the rank. We thought that a higher number of likes would translate to a higher rank but this is not what we observed. One explanation could be that accounts that have a high total of likes also have a high number of tweets. And thus the average number of likes a tweet have may be low even if the account as a whole has a lot.")
    

    st.markdown("#### Infrank and verified accounts")
    st.write("Twitter has a feature that allows users to verify their account. This feature is used to verify that the account is the official account of a person or a brand. We wanted to see if the InfRank of verified accounts was higher than the InfRank of non-verified accounts.")
    st.caption("<center>InfRank vs verified</center>", unsafe_allow_html=True)
    
    tab1, tab2 = st.columns((.5, .5))
    tab1.caption("<center>Evolution of the proportion of users at a given rank.</center>", unsafe_allow_html=True)
    tab1.image(DATA_PATH+"imgs/cum_prop_evolution.png", use_column_width=True)

    tab2.caption("<center>Evolution of the recall of verified users at a given rank</center>", unsafe_allow_html=True)
    tab2.image(DATA_PATH+"imgs/recall_evolution.png", use_column_width=True)

    st.write("A majority of verified accounts are in the first 5000 most influential users. Surprisingly, there is another peak of verified users at the 15000th rank mark. This could be explained by the fact that the verified users that are first retrieved are news specific accounts or very famous celebrities while the other ones are either not news related or famous enough.")

