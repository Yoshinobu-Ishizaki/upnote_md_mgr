
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

from rank_bm25 import BM25Okapi

poc = ["名詞","形容詞","動詞","接尾辞","接頭辞"]

# Set page layout
st.set_page_config(layout="wide")

# -----------------------------------------
# some function defintion
# -----------------------------------------

@st.cache_resource
def create_tokenizer():
    dict = sudachipy.Dictionary()
    tokenizer = dict.create()

    return tokenizer

@st.cache_data
def read_split_data(path):
    d = pd.read_csv(path).assign(score = 0) 
    return d

@st.cache_data
def read_text_data(path):
    d = pd.read_csv(path)[["id","contents"]]
    return d

@st.cache_resource
def create_bm25(txtarray):
    # create okapi_bm25 search engine object
    # txtarray : list of space delimitered text 
    corpus = [doc.split(" ") for doc in txtarray]
    bm25 = BM25Okapi(corpus)
    return bm25

# not used 
def count_words(s,kwd):
    # count product of found count
    lst = [s.split(" ").count(k) for k in kwd]

    return np.prod(lst)

@st.cache_data
def filter_dataframe(df, _bm25,  kwd):
    # do not check _bm25 for cache 
    d1 = df.copy()

    if len(kwd) > 0:
        d1['score'] = _bm25.get_scores(kwd)
        d1 = (d1[d1.score > 0]).sort_values(by = "score", ascending = False )
    else:
        d1['score'] = 0

    return d1

def normalize_word(txt):
    # convert txt by hilighting keywords
    s1 = unicodedata.normalize("NFKC",txt).upper() 
    s2 = re.sub(r"([A-Z]{2})-([DJM].*)", r"\1\2",s1) # replace drawing number
    tkn = tokenizer.tokenize(s2) # tokenize
 
    return list(tkn)

def normalize_word_chunk(s):
    if len(s) > 2**14 -1:
        tokens = []
        ss = s.split("\n")
        for sl in ss:
            tk =  normalize_word(sl) 
            tokens = tokens + tk
    else:
        tokens = normalize_word(s)

    return tokens

def strtrans(s):
    tokens = []
    tkn = normalize_word_chunk(s) # normalized token
    for t in tkn:
        w = t.surface()
        if not w.isspace():
            if t.part_of_speech()[0] in poc:
                n = t.normalized_form()
                tokens.append(n)
    
    return (tokens)

# to display original contents
def get_original_text(dfm_org, id, kwd):
    d1 = dfm_org[dfm_org.id == id]
    txt = d1.contents.iloc[0]

    if len(kwd) > 0:
        tlist = []
        tkn = normalize_word_chunk(txt)

        for t in tkn:
            w = t.surface()
            if not w.isspace():
                # just ignore tabs and spaces
                # if not w.isspace():
                if t.part_of_speech()[0] in poc:
                    n = t.normalized_form()
                    if(n in kwd ):
                        w = f":red[{n}]"
    
                tlist.append(w)
            else:
                tlist.append("\n\n") # add LF when space text

        txt = "".join(tlist)
        return txt
    else:
        return txt

# -------------------------------------
# initialize data
# -------------------------------------

# change working directory
os.chdir(Path(__file__).parent / "..")

tokenizer = create_tokenizer()

# Step 1: Read a CSV file as a Polars DataFrame "dfm"
dfm = read_split_data("data/upnote_text_split.csv")

# Read original dataframe 
dfm_org = read_text_data("data/upnote_text.csv")

# create bm25 object
bm25 = create_bm25(dfm.tokens)

# --------------------------------------
# Streamlit panel
# --------------------------------------

gb = GridOptionsBuilder.from_dataframe(dfm.head())
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_pagination(paginationAutoPageSize = False, paginationPageSize = 10)
gb.configure_default_column(initialHide = True)

if 'keyword' not in st.session_state:
    st.session_state['keyword'] = ''

def update_page():
    """change input text to sudachi normalized text"""
    st.session_state['keyword'] = strtrans(st.session_state.keywordinput)

# Create side panel
with st.sidebar:
    st.header('Side Panel')
    
    text_input = st.text_input('Search text', key = "keywordinput", on_change=update_page)

    text_output = st.text_input("Normalized keyword", disabled=True, value = " ".join(st.session_state.keyword))

    # multi selectors
    showcols = st.multiselect('Columns', dfm.columns, default=['fpath','created','category', 'tags','tokens'] ) 

# Create main panel
with st.container():
    st.header('Upnote Data Viewer')
    
    # Upper area for DataFrame
    
    gb.configure_columns(showcols, hide = False)
    gb.configure_column('tokens', width = 500)
    gridOptions = gb.build()

    df_filtered = filter_dataframe(dfm, bm25, st.session_state.keyword)
    
    grid_response = AgGrid(df_filtered,
                            gridOptions=gridOptions, 
                            enable_enterprise_modules=True, 
                            allow_unsafe_jscode=True, 
                            update_mode=GridUpdateMode.SELECTION_CHANGED)
    

    selected_rows = grid_response["selected_rows"]

    # Bottom area for multi-line text
    st.subheader('Normalized text of selected row')

    with st.container(height=250):
        if len(selected_rows) > 0:
            iid = selected_rows[0]["id"]
            txt = get_original_text(dfm_org, iid, st.session_state.keyword)

            text_area = st.markdown(txt)
        else:
            text_area = st.markdown("")



