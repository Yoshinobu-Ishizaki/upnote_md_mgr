sudachiの準備
===


1. python環境の作成: `python -m venv .venv`
1. sudachiのインストール: `pip install sudachipy sudachidict_core`
2. 設定ファイルのコピー: `.venv/Lib/site-packages/sudachipy/resources/sudachi.json`をこのフォルダに
3. ユーザー辞書の作成: `userdic.csv`を参照
4. ユーザー辞書のコンパイル: `add_user_dict.bat`参照。
5. ユーザー辞書読込設定: `sudachi.json`に`"userDict":`の行を追加。
6. ユーザー辞書の確認: `sudachipy -r sudachi.json`
7. 



