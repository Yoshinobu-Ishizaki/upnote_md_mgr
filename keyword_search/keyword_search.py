
import os
from pathlib import Path
# import polars as pl
import pandas as pd

import numpy as np
import unicodedata
import re
import sudachipy 

import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

dict = sudachipy.Dictionary()
tokenizer = dict.create()

def strtrans(s):
    tokens = [] # normalized token
    s1 = unicodedata.normalize("NFKC",s).lower()
    s2 = re.sub(r"([a-z]{2})-([djm])-([0-9]{4,5})", r"\1\2\3",s1) # replace drawing number
    tkn = tokenizer.tokenize(s2)
    for t in tkn:
        w = t.surface()
        if not w.isspace():
            if t.part_of_speech()[0] in ["名詞","形容詞","動詞"]:
                n = t.normalized_form()
                tokens.append(n)
    
    return (tokens)

def strtrans_text(s):
    return(" ".join(strtrans(s)))

# change working directory
os.chdir(Path(__file__).parent / "..")

# Step 1: Read a CSV file as a Polars DataFrame "dfm"
dfm = pd.read_csv("data/upnote_text_split.csv")

def count_words(s,kwd):
    # count product of found count
    return np.prod([s.split(" ").count(k) for k in kwd])

def keyword_filter(kwd):
    """kwd: list of keywords"""

    d1 = dfm.with_columns([
        pl.col("tokens").map_elements(lambda x: count_words(x, kwd)).alias("wc")
    ]).filter(pl.col("wc") > 0).sort(by = "wc", descending=True)
    
    return d1

# --------------------------------------
# Streamlit panel
# --------------------------------------

# Set page layout
st.set_page_config(layout="wide")

gb = GridOptionsBuilder.from_dataframe(dfm.head(10))
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_pagination(paginationAutoPageSize = False, paginationPageSize = 10)
gridOptions = gb.build()

if 'keyword' not in st.session_state:
    st.session_state['keyword'] = ''

def update_page():
    """change input text to sudachi normalized text"""
    st.session_state['keyword'] = strtrans_text(st.session_state.keywordinput)

# Create side panel
with st.sidebar:
    st.header('Side Panel')
    
    text_input = st.text_input('Enter some text', key = "keywordinput", on_change=update_page)

    text_output = st.text_input("keyword text", disabled=True, placeholder=st.session_state.keyword)

    # multi selectors
    showcols = st.multiselect('Columns', dfm.columns, default=['fpath','created','category', 'tags','tokens'] ) 

# Create main panel
with st.container():
    st.header('Upnote Data Viewer')
    
    # Upper area for DataFrame
    # st.subheader('DataFrame')
    grid_response = AgGrid(dfm.head(30),
                            gridOptions=gridOptions, 
                            enable_enterprise_modules=True, 
                            allow_unsafe_jscode=True, 
                            update_mode=GridUpdateMode.SELECTION_CHANGED)
    
    # Bottom area for multi-line text
    st.subheader('Original text of selected row')
    text_area = st.text_area('outtext', disabled=True, label_visibility='hidden', height=160)


