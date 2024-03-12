# How to compile userdic


1. mecabへのパスを通す
1. 次のコードを実行する
    ```
    mecab-dict-index -d "C:\Program Files\MeCab\dic\ipadic" -u userdic.dic -f utf-8 -t utf-8 userdic.csv
    ```
1. mecabのrcfileに以下のエントリを追加

    ```
    userdic = $(rcpath)\..\dic\userdic.dic
    ```

