using Glob
using DataFrames
using Dates
using CSV

if basename(pwd()) == "notebook"
    cd("..")
end 

upnote_path = "UpNote/General Space"

function convtxt(path)
    s = ""
    update_dt = ""
    create_dt = ""
    cat_mode = false
    isheader = true
    categories = String[]
    bdytxt = String[]
    tags = String[]

    txt = readlines(path)

    for i in eachindex(txt)
        if i > 1
            # skip first line
            s = txt[i]
            if startswith(s,"date:")
                s2 = replace(s, "date: " => "")
                update_dt = DateTime(s2, DateFormat("yyyy-mm-dd HH:MM:SS"))
            elseif startswith(s,"created: ")
                s2 = replace(s, "created: " => "")
                create_dt = DateTime(s2, DateFormat("yyyy-mm-dd HH:MM:SS"))
            elseif startswith(s,"categories:")
                cat_mode = true
                
            elseif s == "---"
                isheader = false
                cat_mode = false
                continue
            else
                if cat_mode
                    s2 = replace(s, r"^- " => "")
                    push!(categories, s2)
                end
            end
            # start of body parser
            if !isheader 
                if startswith(s,r"#+ ")
                    s2 = replace(s, r"#+ " => "")
                    push!(bdytxt,s2)
                elseif contains(s, r"^[\s\*]+$")
                    s2 = replace(s, r"^[\s\*]+$" => "")
                    push!(bdytxt,s2)
                elseif contains(s,r"^#[^[:punct:] ]*$")
                    s2 = replace(s,r"^#" => "")
                    push!(tags, s2)
                else
                    push!(bdytxt,s)
                end
            end # body
        end # i > 1
    end # i
    
    cat_str = join(categories, "|")
    contents = join(bdytxt, "\n")
    tags_str = join(tags, "|")
    
    return(DataFrame("fpath" => basename(path), "update" => update_dt, "created" => create_dt, "category" => cat_str, "tags" => tags_str, "contents" => contents))
end

# do excecution

tfiles = glob("*.md", upnote_path)

dfm = DataFrame()
 
for f in tfiles
    append!(dfm, convtxt(f))
end

CSV.write("data/upnote_text.csv", dfm)

