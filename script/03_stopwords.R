# stopwordsを使って単語を整理

library(tidyverse)

# 分かち書きされているデータを読込む

dfm <- read_csv("upnote_text_split.csv") |>
  select(fpath, contents_split) |> 
  separate_rows(contents_split, sep = " ") |> 
  rename(words = contents_split)

# stopwords オリジナルの用語も使う。

mystopwords <- tibble( words = c(
  stopwords("ja", source = "marimo"),
  stopwords("en"),
  read_lines("mystopwords.txt")
))

# filtering by stopwords and etc

dfm1 <- dfm |> 
  mutate(words = stringi::stri_trans_nfkc(words)) |> # convert to canonical zenkaku hankaku 
  mutate(words = tolower(words)) |> # lower case 
  filter(!str_detect(words, "-?\\d+\\.?\\d*(?:[eE][-+]?\\d+)?")) |> # numeric words
  filter(!str_detect(words, "^[a-z]$")) |> # single alpha
  anti_join(mystopwords, by = c("words"))  
  
# output to keywords file

dfm1 |> write_csv("upnote_keywords.csv")

