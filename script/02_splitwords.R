# 全てのデータを読込み、文を分かち書きにして別ファイルに出力する。

library(tidyverse)
library(RMeCab)

dfm <- read_csv("upnote_text.csv")

pick_word <- function(txt){
  tt <- unlist(RMeCabC(txt))
  nm <- names(tt)
  
  return(str_c(tt[nm %in% c("名詞","動詞","形容詞")], collapse = " "))
}

# ignore blank contents
dfm |> 
  filter(!is.na(contents)) |> 
  rowwise() |> 
  mutate(contents_split = pick_word(contents)) |> 
  select(-contents) |> 
  # remove control characters from its title
  mutate(title = str_remove_all(title,"[\\p{Cc}\\p{Cf}]")) |> 
  write_csv("upnote_text_split.csv")

