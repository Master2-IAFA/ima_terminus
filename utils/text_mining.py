# Import libraries
import json
import os
from collections import defaultdict

import networkx as nx
import numpy as np
import streamlit as st
import torch
from transformers import (AutoModel, AutoTokenizer, T5ForConditionalGeneration,
                          T5Tokenizer)


@st.cache_resource
def download_models(GOOGLE=1):
    if GOOGLE:
        summary_tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
        summary_model =  T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
    else :
        summary_tokenizer = T5Tokenizer.from_pretrained("t5-base", model_max_length=1024)
        summary_model =  T5ForConditionalGeneration.from_pretrained("t5-base")
    return summary_tokenizer, summary_model

summary_tokenizer, summary_model = download_models()
print("T5 model loaded")

device = torch.device('cpu')




@st.cache_data
def get_embedding(text):
    import torch.nn.functional as F

    def average_pool(last_hidden_states,
                     attention_mask):
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained('intfloat/e5-base')
    model = AutoModel.from_pretrained('intfloat/e5-base')
    batch_dict = tokenizer([text], max_length=512, padding=True, truncation=True, return_tensors='pt')
    outputs = model(**batch_dict)
    embedding = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
    embedding = F.normalize(embedding, p=2, dim=1)
    
    return embedding

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '' if t.startswith('@') and len(t) > 1 else t
        t = '' if t.startswith('http') else t
        t = '' if t == 'RT' else t
        new_text.append(t)
    return " ".join(new_text)


# def extractive_summarization(tweets_info, text_col="text", max_tweets = 20) :
#     """
#     The goal of this function is to extract the most important sentences from a text.
#     ie. extractive summarization
#     """

#     # Create a similarity matrix    
#     sim_matrix = np.zeros([len(tweets_info), len(tweets_info)])
#     for i in range(len(tweets_info)):
#         for j in range(len(tweets_info)):
#             if i != j:
#                 sim_matrix[i][j] = torch.cosine_similarity(tweets_info.iloc[i]['text_embedding'], tweets_info.iloc[j]['text_embedding'], dim=0)
    
#     # Create a graph from the similarity matrix
#     nx_graph = nx.from_numpy_array(sim_matrix)

#     # Compute the pagerank of each sentence
#     scores = nx.pagerank(nx_graph)

#     # Sort the sentences by score
#     ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(tweets_info[text_col])), reverse=True)

#     # Extract the top sentences
#     top_sentences = [x[1] for x in ranked_sentences[:min(max_tweets, len(tweets_info))]]

#     return top_sentences

def abstractive_summarization(sentences) :
    text = " ".join(sentences)
    preprocess_text = preprocess(text)
    preprocess_text = preprocess_text.strip().replace("\n"," ")
    t5_prepared_Text = "What happened in these tweets :" + preprocess_text

    # tokenize the text
    tokenized_text = summary_tokenizer.encode(t5_prepared_Text, return_tensors="pt", truncation=True)

    # summmarize
    summary_ids = summary_model.generate(tokenized_text,
                                        num_beams=4,
                                        no_repeat_ngram_size=2,
                                        min_length=30,
                                        max_length=100,
                                        early_stopping=True)
    
    output = summary_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return output






if __name__ == "__main__":
    # query = "The book was awesome! Thanks for the recommendation @Allan. Go to https://www.google.com for more info."

    # tweets = ["I just ordered fried chicken 🐣", 
    #         "The movie was great", 
    #         "What time is the next game?", 
    #         "Just finished reading 'Embeddings in NLP'"]

    # d = defaultdict(int)


    # embedding_query = get_embedding(query)
    # for tweet in tweets:
    #     sim = torch.cosine_similarity(embedding_query, get_embedding(tweet), dim=0)
    #     d[tweet] = sim


    # print('Most similar to: ',query)
    # print('----------------------------------------')
    # for idx,x in enumerate(sorted(d.items(), key=lambda x:x[1], reverse=True)):
    #     print(idx+1,x[0], f"{x[1].item():.3f}")

    
    text = """
The US has "passed the peak" on new coronavirus cases, President Donald Trump said and predicted that some states would reopen this month.
The US has over 637,000 confirmed Covid-19 cases and over 30,826 deaths, the highest for any country in the world.
At the daily White House coronavirus briefing on Wednesday, Trump said new guidelines to reopen the country would be announced on Thursday after he speaks to governors.
"We'll be the comeback kids, all of us," he said. "We want to get our country back."
The Trump administration has previously fixed May 1 as a possible date to reopen the world's largest economy, but the president said some states may be able to return to normalcy earlier than that.
"""
    preprocess_text = preprocess(text)
    preprocess_text = preprocess_text.strip().replace("\n"," ")
    t5_prepared_Text = "summarize: " + preprocess_text

    # tokenize the text
    tokenized_text = summary_tokenizer.encode(t5_prepared_Text, return_tensors='pt')

    # summmarize
    summary_ids = summary_model.generate(tokenized_text,
                                         num_beams=4,
                                         no_repeat_ngram_size=2,
                                         min_length=10,
                                         max_length=100,
                                         early_stopping=True)
    
    output = summary_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    print(output)