# UpNoteフォルダのテキストファイルを処理して データフレームを出力する。

library(tidyverse)

# chdir
if (basename(getwd()) == "script"){
  setwd("..")
}

#---- 一通りの処理をする関数 

read_upnote_text <- function(fpath){
  
  fname = basename(fpath)
  d1 <- read_lines(fpath, skip = 1)
  endl <- length(d1)
  
  lno <-  1
  lbdy <- 1
  isheader <- TRUE
  cat_mode <-  FALSE
  title_str <-  "" # default
  tags = c()
  bdytxt = c()
  
  for (l in d1){
    lno = lno + 1
    if(isheader){
      if( str_detect(l, "date:")){
        update_dt <- as_datetime(str_remove(l,"date: "), tz = Sys.timezone())
      }else if( str_detect(l, "created:")){
        create_dt <- as_datetime(str_remove(l,"created: "), tz = Sys.timezone())
      }else if(str_detect(l,"categories:")){
        cat_mode <-  TRUE
        cc = c()
      }else if(str_detect(l,"---")){
        cat_mode <-  FALSE 
        isheader <- FALSE # end of header lines
        next
      }else{
        if(cat_mode){
          cc = c(cc, str_remove(l,"^- "))
        } 
      } 
    }else{ # body
      if(str_detect(l,"^#+ ")){
        # handle headers
        bdytxt = c(bdytxt, str_remove(l,"^#+ "))
      }else if(str_detect(l,"^[\\s\\*]+$")){
        # ignore ruler line
        bdytxt = c(bdytxt, str_replace(l,"^[\\s\\*]+$",""))
      }else if(str_detect(l,"^#[^[:punct:] ]*$")){
        # search tag lines
        tags <-  c(tags,str_remove(l,"^#"))
      }else{
        bdytxt = c(bdytxt, l)
      }
    }
  }
  
  contents <- str_c(bdytxt, collapse = "\n") # contents without headers and tags
  
  if(str_length(title_str) == 0 ){
    title_str <- str_remove(fpath, ".md$")
  }
  
  catstr <- str_c(cc, collapse = "|")
  tagstr <- str_c(tags, collapse = "|")
  
  return(tibble(fpath = fname, update = update_dt, created = create_dt,
                category = catstr, tags = tagstr,
                contents = contents))
}

#---- 全ファイルを対象に一気に処理

all_files <- list.files("UpNote/General Space/", pattern = "*.md", full.names = TRUE)

dfm <- all_files |> map(read_upnote_text) |> list_rbind()

# 結果出力

dfm |> write_csv("data/upnote_text.csv")

