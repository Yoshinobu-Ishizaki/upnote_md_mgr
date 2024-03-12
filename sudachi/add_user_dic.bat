sudachipy ubuild -s ../.venv/Lib/site-packages/sudachidict_core/resources/system.dic userdic.csv 

@REM  ユーザー辞書
@REM  java -Dfile.encoding=UTF-8 -cp sudachi-0.6.8.jar com.worksap.nlp.sudachi.dictionary.UserDictionaryBuilder -o user.dic -s system_core.dic userdic.csv

@REM copy sudachi.json to installed directory
COPY sudachi.json ..\.venv\Lib\site-packages\sudachipy\resources\

@REM mv userdic to installed directory without asking overwrite
MOVE /Y user.dic ..\.venv\Lib\site-packages\sudachipy\resources\
