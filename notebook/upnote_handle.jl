# handling upnote data

# post creation 

# gives SHA id from its fpath name

using DataFrames
using SHA
using CSV

#---- 
# add new column with sha1 code as id
#----

dfm = DataFrame(CSV.File("data/upnote_text.csv"))


dfm2 = transform(dfm, :fpath => (x -> @. bytes2hex(sha1(x))) => :id )

# output
# CSV.write("data/upnote_text.csv", 
#     select(dfm2, "id","fpath","update","created","category","tags","contents")
# )

#------------------------ 
# Tokenize
#------------------------

using Awabi
using Unicode

# neologd 辞書を指定
dic = Dict("dicdir" => raw"C:\Program Files\MeCab\dic\ipadic-neologd", "userdic" => "mecab/userdic.dic")

# テストデータ
tstr = subset(dfm, :id => ByRow( x -> x == "d98f2d16ac0b0db6051f91d8dfdab4c8d7509efb"))[!,"contents"][1]

# 全角英数を半角に変換
tstrn = Unicode.normalize(tstr, :NFKC)

# 英数は小文字に変換
tstrl = lowercase(tstrn)

# 治具コードがあったらそれを変換する
tstr2 = replace(tstrl, r"([a-z]{2})-([jd])-([0-9]+)" => s"\1\2\3")

# 品詞分解
tokens = tokenize(Tokenizer(dic), tstr2)

# 分解した品詞から特定の用語を取り出す
w2 = String[]
for (w,p) in tokens
    ps = split(p,",")
    if ps[1] in  ("カスタム名詞","名詞","動詞","形容詞")
        push!(w2, w)
    end
end

# 合成
join(w2,"\t") 



# test
bytes2hex(sha1("asete"))

pwd()