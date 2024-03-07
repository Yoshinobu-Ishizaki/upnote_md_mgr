# How to compile userdic

```
mecab-dict-index -d "C:\Program Files\MeCab\dic\ipadic" -u userdic.dic -f utf-8 -t utf-8 userdic.csv
```

mecabのrcfileに以下のエントリを追加

```
userdic = $(rcpath)\..\dic\userdic.dic
```

