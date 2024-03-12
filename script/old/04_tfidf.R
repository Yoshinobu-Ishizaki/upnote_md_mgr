# calculate TFIDF 

library(tidyverse)

dfm <- read_csv("upnote_keywords.csv")

dfm |>     
  count(fpath, words) |>
  group_by(fpath) |> 
  mutate(nwords = sum(n)) |> # add total word count in a doc
  bind_tf_idf(words, fpath, n) |> 
  write_csv("upnote_tfidf.csv")


  

