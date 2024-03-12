
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

# Read original dataframe 
dfm_org = (pd.read_csv("data/upnote_text.csv"))[["id","contents"]]

def count_words(s,kwd):
    # count product of found count
    lst = [s.split(" ").count(k) for k in kwd]

    return np.prod(lst)

def keyword_filter(kwd):
    """kwd: list of keywords"""

    d1 = dfm.copy()
    
    d1['wc'] = d1['tokens'].apply(lambda x: count_words(x, kwd))
    d2 = (d1[d1.wc > 0]).sort_values(by = "wc", ascending=False)
    
    return d2

def get_original_text(id, kwd):
    d1 = dfm_org[dfm_org.id == id]
    txt = d1.contents.iloc[0]

    tlist = []

    # convert txt by hilighting keywords
    s1 = unicodedata.normalize("NFKC",txt).lower()
    s2 = re.sub(r"([a-z]{2})-([djm])-([0-9]{4,5})", r"\1\2\3",s1) # replace drawing number
    tkn = tokenizer.tokenize(s2) # tokenize
    for t in tkn:
        w = t.surface()
        if not w.isspace():
            if t.part_of_speech()[0] in ["名詞","形容詞","動詞"]:
                n = t.normalized_form()
                if(n in kwd ):
                    w = f":red[{n}]"

        tlist.append(w)                

    return "".join(tlist)


# --------------------------------------
# Streamlit panel
# --------------------------------------

# Set page layout
st.set_page_config(layout="wide")

gb = GridOptionsBuilder.from_dataframe(dfm.head(10))
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

    df_filtered = keyword_filter(st.session_state.keyword)
    
    grid_response = AgGrid(df_filtered.head(30),
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
            txt = get_original_text(iid, st.session_state.keyword)

            text_area = st.markdown(txt)
        else:
            text_area = st.markdown("")



