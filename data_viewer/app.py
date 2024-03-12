import os
from pathlib import Path
import polars as pl

import numpy as np

# from shiny.express import input, render, ui
from shiny import ui, render, App, reactive

import unicodedata
import re

import sudachipy 

# dict = sudachipy.Dictionary(config_path="../sudachi/sudachi.json")
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
dfm = pl.read_csv("data/upnote_text_split.csv")

def count_words(s,kwd):
    # count product of found count
    return np.prod([s.split(" ").count(k) for k in kwd])

def keyword_filter(kwd):
    """kwd: list of keywords"""

    d1 = dfm.with_columns([
        pl.col("tokens").map_elements(lambda x: count_words(x, kwd)).alias("wc")
    ]).filter(pl.col("wc") > 0).sort(by = "wc", descending=True)
    
    return d1

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text(id = "keyword_input", label= "Search Keywords", value=""),
        ui.output_text(id = "keyword_output"),
        ui.input_action_button("go", "Search")
    ),
    ui.layout_columns(
        ui.card(ui.output_data_frame("output_dfm"),full_screen=True,)
    )
)

def server(input, output, session):
    @render.text
    def keyword_output():
        return strtrans_text(input.keyword_input())

    @render.data_frame
    @reactive.event(input.go )
    def output_dfm():

        kwd = strtrans(input.keyword_input())
        d = keyword_filter(kwd)

        return render.DataGrid(d, height="600px")


# run app
app = App(app_ui, server)

