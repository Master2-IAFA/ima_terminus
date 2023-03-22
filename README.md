# Video Demo

Youtube link [here](https://youtu.be/_4plo1sFjaE) (video in French).

# Instructions

In order to have the application work on your system :

-   Create a Neo4j database and import the data from the file `data/whole_database.json` into it.
-   Check that the connection to the database is correct in the file utils/neo4j.py
-   Create a file named `config.py` in the `utils/ChatGPT` directory. It should contain the following variable :

```python
 API_KEY = "your_OpenAI_API_key"
```

-   Make sure to have all the required packages installed.
-   Run the file `app.py` using streamlit (`streamlit run app.py`).

---

Application developed by Anne-Sophie Dusart, Sokhna Fàtmà Joo'p, Chloé Michel, Auguste Verdier and Ludovic Tuncay from the [**@M2-IMA**] class.
