import streamlit as st

IMG_PATH = "./data/imgs/"

def run_page() :
    st.title("Visualization Page")
    st.header("Visualize the data present in the graph")

    # Ajouter un menu déroulant pour choisir le type d'embedding a visualiser
    embedding = st.selectbox(
        "Select the type of embedding to visualize",
        ("Text embedding", "Graph embedding")
    )

    if embedding == "Text embedding" :
        st.write("After an ebedding with E5, t-SNE is used to reduce the dimensionality of the embedding to 2D")
        # Plot the raw embedding (no colors)
        st.caption("<center>t-SNE visualization of the embedding</center>", unsafe_allow_html=True)
        st.image(IMG_PATH+"tsne_raw.png", use_column_width=True)

        # Plot the embedding with colors
        tab1, tab2 = st.columns((.44, .56))
        tab1.caption("<center>t-SNE visualization of the embedding colored by event</center>", unsafe_allow_html=True)
        tab1.image(IMG_PATH+"tsne_eventID.png", use_column_width=True)

        tab2.caption("<center>t-SNE visualization of the embedding colored by category</center>", unsafe_allow_html=True)
        tab2.image(IMG_PATH+"tsne_eventType.png", use_column_width=True)

        st.write("There is a very good separation based on the category of the event, but less so based on the event itself. This is due to the fact that some of the events are very similar to each other and contain tweets with the same type of vocabulary. The embedding is then not able to distinguish them. But generally it it seem to be working well.")
        st.write("This embedding beeing good means that the tweet retrieval system is working well. The tweets retrieved are similar to the query.")
    elif embedding == "Graph embedding" :    
        # Ajouter un menu déroulant pour choisir le sous-réseau à étudier
        subnet = st.selectbox(
            "Select the subnetwork to study",
            ("Users network", "Tweets network", "Category (event type) network"))

        st.markdown("##### All embeddings are computed with node2vec")
        if subnet == "Users network" :
            st.image(IMG_PATH+"users/raw_tsne_user.png", caption="t-SNE visualization of the users embedding", width=800)
            st.markdown("")
            tab1, tab2 = st.columns((.50, .50))
            tab1.image(IMG_PATH+"users/tsne_user_colored_by_interected.png", use_column_width=True, caption="t-SNE visualization of the embedding colored if interacted (boolean)")
            tab2.image(IMG_PATH+"users/tsne_user_colored_by_interaction_level.png", use_column_width=True, caption="t-SNE visualization of the embedding colored by interaction level")
            st.write("The analyzed subgraph includes only nodes labeled as \"User,\" and edges between user nodes represent the relationships RETWEETS, MENTIONS, and REPLIED_TO. To distinguish users in the social network based on their interactions, a boolean variable called \"interacted\" has been created. Interacted is true if a user node has retweeted, mentioned, or replied to another user and false otherwise. An \"interaction level\" has also been assigned to each user, with a high level indicating that the user has interacted and has been retweeted, mentioned, or replied to by another user, a medium level indicating that the user has interacted but has not been retweeted, mentioned, or replied to, and a low level indicating no interaction.")
            st.write("Two clusters have been identified based on the \"interacted\" property. The first cluster comprises users who have never interacted, while the second cluster consists of users who have interacted at least once. Three clusters have also been identified based on the \"interaction level\" property. Users with a high interaction level form a small cluster on the right, users with a medium interaction level are in the right cluster, and users with a low interaction level are in the left cluster.")

        elif subnet == "Tweets network" :
            st.image(IMG_PATH+"tweets/raw_tsne_tweet.png", width=800, caption="t-SNE visualization of the tweets embedding")
            st.markdown("") 
            tab1, tab2 = st.columns((.50, .50))
            tab1.image(IMG_PATH+"tweets/tsne_tweet_colored_by_replyto.png", use_column_width=True, caption="t-SNE visualization of the embedding colored by relation \"REPLY_TO\"")
            tab2.image(IMG_PATH+"tweets/tsne_tweet_colored_by_retweeted.png", use_column_width=True, caption="t-SNE visualization of the embedding colored by relation \"RETWEETED\"")
            st.write("The analyzed subgraph consists of nodes labeled as \"Tweet\" and edges corresponding to relationships RETWEETED and REPLY_TO.")
            st.write("We created two boolean variables, 'reply_to' and 'retweeted,' to distinguish tweets based on whether they are replies or retweets. Two clusters were identified based on the 'retweeted' property: a cluster of tweets that are retweets of another tweet and a cluster of tweets that are not retweets. The REPLY_TO relationship is not relevant in this analysis due to the larger number of RETWEETED edges compared to REPLY_TO edges.")

        elif subnet == "Category (event type) network" :
            st.markdown("##### The tweets' subgraph, including the event nodes")
            tab1, tab2 = st.columns((.5, .5))
            tab1.image(IMG_PATH+"tweets+events/tsne_tweet_event_colored_by_eventType.png", use_column_width=True, caption="t-SNE visualization of the embedding colored by event type")
            tab2.image(IMG_PATH+"tweets+events/tsne_tweet_event_colored_by_topic.png", use_column_width=True, caption="t-SNE visualization of the embedding colored by topic")
            st.markdown("")
            st.write("In the second part of our analysis, we expanded the subgraph to include nodes labeled as 'Event' to investigate the IS_ABOUT relationship from tweet nodes to event nodes. We applied the same clustering process used previously and identified several clusters based primarily on topic. However, due to the presence of RETWEETED and REPLY_TO relationships, some noise was observed in the data. Despite this, our analysis suggests that the IS_ABOUT relationship is the most relevant for understanding tweet clustering in the subgraph.")
            st.markdown("")
            st.markdown("##### The tweets' subgraph, including the event nodes but only considering the \"IS_ABOUT\" relationship.")
            tab3, tab4 = st.columns((.5, .5))
            tab3.image(IMG_PATH+"tweets+events/tsne_IS_ABOUT_colored_by_eventType.png", use_column_width=True, caption="t-SNE visualization of the embedding colored by event type")
            tab4.image(IMG_PATH+"tweets+events/tsne_IS_ABOUT_colored_by_topic.png", use_column_width=True, caption="t-SNE visualization of the embedding colored by topic")

            st.image(IMG_PATH+"tweets+events/tsne_IS_ABOUT_colored_by_postPriority.png", width=800, caption="t-SNE visualization of the embedding colored by post priority")
            st.write("In the final part of our analysis, we applied the same clustering process to the same subgraph, but only considered edges labeled as IS_ABOUT that connect tweets to their respective events. Our findings indicate that the data continued to display topic-based separation and that noise was eliminated. However, we also observed the emergence of a main cluster that appeared to amalgamate different topics. This cluster was characterized by the post priority \"Unknown,\" which we attributed to the tweets being linked to their respective topics through their properties, but not through an edge in the social network. This was true for 19321 out of 55986 tweets.")