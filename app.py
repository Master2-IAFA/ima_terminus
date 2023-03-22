import streamlit as st

st.set_page_config(page_title="Chef d'Oeuvre !", layout="wide", menu_items={"Get help": None, "Report a bug": None, "About": None})

import tabs.home as home_page
import tabs.query as query_page
import tabs.statistics as statistics_page
import tabs.summarize as summarize_page
import tabs.user_influence as influence_page
import tabs.visualize as visualize_page
from streamlit_option_menu import option_menu

selected = option_menu(
            menu_title=None,  # required
            options=["Home", "Statistics", "Visualize", "Query", "Summarize", "Users influence"],  # required
            icons=["house-fill", "bar-chart-line-fill", "eye-fill", "chat-square-text-fill", "arrows-collapse", "people-fill"],  # optional
            menu_icon="cast",  # optional
            default_index=0,  # optional
            orientation="horizontal",
        )


footer = """
<style>
.footer {
  position: fixed;
  left: 0;
  bottom: 0;
  width: 100%;
  background-color: white;
  color: black;
  text-align: center;
}
</style>
<div class="footer">
<p>Developed by Anne-Sophie Dusart, Sokhna Fàtmà Joo'p, Chloé Michel, Auguste Verdier and Ludovic Tuncay </p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)


if selected == "Home":
    home_page.run_page()
elif selected == "Statistics" :
    statistics_page.run_page()
elif selected == "Query" :
    query_page.run_page()
elif selected == "Summarize" :
    summarize_page.run_page()
elif selected == "Visualize" :
    visualize_page.run_page()
elif selected == "Users influence" :
    influence_page.run_page()

    




