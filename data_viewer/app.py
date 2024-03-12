import os
from pathlib import Path
import polars as pl

# from shiny.express import input, render, ui
from shiny import ui, render, App

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

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text(id = "keyword_input", label= "Search Keywords", value="")
    ),
    ui.layout_columns(
        ui.card(ui.output_data_frame("output_dfm"),full_screen=True,)
    )
)

def server(input, output, session):
    @render.data_frame
    def output_dfm():
        return render.DataGrid(dfm)

app = App(app_ui, server)

