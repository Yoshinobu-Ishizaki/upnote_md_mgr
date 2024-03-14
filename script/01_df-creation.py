from pathlib import Path
import os 
import glob
from datetime import datetime
import re
import pandas as pd
import hashlib

upnote_path = Path("../UpNote/General Space")

def convtxt(path):
    s = ""
    update_dt = ""
    create_dt = ""
    cat_mode = False
    isheader = True
    categories = []
    bdytxt = []
    tags = []

    with open(path,"r", encoding='utf-8') as f:
        txt = f.readlines()

    for i, line in enumerate(txt):
        if i > 0:
            # skip first line
            s = line.rstrip()
            if s.startswith("date:"):
                s2 = s.replace("date: " ,"")
                update_dt = datetime.strptime(s2, "%Y-%m-%d %H:%M:%S")
            elif s.startswith("created: "):
                s2 = s.replace("created: ","")
                create_dt = datetime.strptime(s2, "%Y-%m-%d %H:%M:%S")
            elif s.startswith("categories:"):
                cat_mode = True
            elif s == "---":
                isheader = False
                cat_mode = False
                continue
            else:
                if cat_mode:
                    s2 = re.sub(r"^- ","",s)
                    categories.append(s2)

            # start of body parser
            if not isheader:
                if bool(re.match(r"#+ ",s)):
                    s2 = re.sub(r"#+ ","",s)
                    bdytxt.append(s2)
                elif bool(re.match(r"^[\s\*]+$",s)):
                    s2 = re.sub(r"^[\s\*]+$","",s)
                    bdytxt.append(s2)
                elif bool(re.findall(r"#\w+", s)):
                    # tag search
                    for m in re.findall(r"#\w+", s):
                        s2 = re.sub(r"^#","",m)
                        if not s2.isdigit():
                            tags.append(s2)
                else:
                    bdytxt.append(s)
            # body
        # i > 0
    # i
    
    cat_str = "|".join(categories)
    contents = "\n".join(bdytxt)
    tags_str = "|".join(tags)
    
    fpath = os.path.basename(path)
    
    sha1 = hashlib.sha1()
    sha1.update(fpath.encode('utf-8'))
    id = sha1.hexdigest()

    yield [id, fpath, update_dt, create_dt, cat_str, tags_str, contents]

# main loop 
if __name__ == "__main__":

    files = [os.path.join(upnote_path,f) for f in glob.glob("*.md", root_dir=upnote_path)]

    maxi = len(files)
    # do convert text for all data
    alldata = []
    for (i,f) in enumerate(files):
        for output in convtxt(f):
            alldata.append(output)

        if (i % 100) == 0:
            fname = os.path.basename(f)
            print("\x1b[2K", end='\r') # clear line first
            print(f"{i}/{maxi}:{fname}", end='\r') # do not linefeed

    dfm = pd.DataFrame(alldata, columns=["id", "fpath","update","created","category","tags","contents"])

    dfm.to_csv("upnote_text.csv", index=False)

