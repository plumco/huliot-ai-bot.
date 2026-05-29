import streamlit as st
from streamlit.components.v1 import html

st.title("Huliot Pipe Inspector AI")

with open("app.html", "r", encoding="utf-8") as f:
    page_html = f.read()

html(page_html, height=850)