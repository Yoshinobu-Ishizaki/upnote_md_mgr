# UpNoteフォルダのテキストファイルを処理して データフレームを出力する。

library(tidyverse)


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
      }else if(str_detect(l,"^#+ ")){
        title_str <- str_remove(l,"^#+ ") |> 
          str_remove_all("[\\p{Cc}\\p{Cf}]") # remove control characters 
        isheader <- FALSE # end of header lines
        lbdy <- lno
      }else{
        if(cat_mode){
          cc = c(cc, str_remove(l,"^- "))
        } 
      } 
    }else{ # body
      # search tag lines
      if(str_detect(l,"^#[^[:punct:] ]*$")){
        tags <-  c(tags,str_remove(l,"^#"))
        # replace original line with blank
        d1[lno-1] <- ""
      }
    }
  }
  
  c1 <- str_c(d1[lbdy:endl], collapse = "\n") # contents without headers and tags
  
  if(str_length(title_str) == 0 ){
    title_str <- str_remove(fname, ".md$")
  }
  
  catstr <- str_c(cc, collapse = "|")
  tagstr <- str_c(tags, collapse = "|")
  
  return(tibble(fpath = fname, title = title_str, update = update_dt, 
                created = create_dt, category = catstr, tags = tagstr, contents = c1))
}

#---- 全ファイルを対象に一気に処理

all_files <- list.files("UpNote/General Space/", pattern = "*.md", full.names = TRUE)

dfm <- all_files |> map(read_upnote_text) |> list_rbind()

# 結果出力

dfm |> write_csv("upnote_text.csv")
