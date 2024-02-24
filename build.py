import re
import json
def new_story_session():
    return {
        "str":""
    }

p_0 = r'^- \w+$'
p_1 = r'^- \w+ \S+$'
p_2 = r'^- \w+ \S+ \S+$'
p_3 = r'^- \w+ \S+ \S+ \S+$'
code_0_set = {"end"}
code_1_set = {"label","goto","choice","title","author","image"}
code_2_set = {"choice",}
code_3_set = {"date",}
def check_decode(sline):
    is_code = False
    spl = sline.split(" ")
    if len(spl)==2:
        ret = re.match(p_0, sline)
        if ret:
            if spl[1] in code_0_set:
                is_code = True
    elif len(spl)==3:
        ret = re.match(p_1, sline)
        if ret:
            if spl[1] in code_1_set:
                is_code = True
    elif len(spl)==4:
        ret = re.match(p_2, sline)
        if ret:
            if spl[1] in code_2_set:
                is_code = True
    elif len(spl)==5:
        ret = re.match(p_3, sline)
        if ret:
            if spl[1] in code_3_set:
                is_code = True
    if is_code:
        return (True,spl[1:])
    else:
        return (False,)

def add_in_label(LL,key,value):
    global is_correct
    if key in LL:
        if LL[key]>=0:
            print("错误！第%d行：标签重定义",value)
            is_correct = False
        else:
            LL[key] = value
    else:
        LL[key] = value

def check_label(LL,key):
    if key not in LL:
        LL[key] = -1

label_list = {}
story = []
str_lines = []
title = ""
author = []
date = (0,0,0)
with open("story.md",encoding="utf-8") as story_file:
    str_lines = story_file.read().split("\n")
    story_file.close()



session = new_story_session()
is_correct = True
i=0
for sline in str_lines:
    if not sline:
        if session["str"]:
            story.append(session)
            i += 1
        session = new_story_session()
    else:
        code_ret = check_decode(sline)
        if code_ret[0]:
            if code_ret[1][0] == "title":
                title = code_ret[1][1]
            elif code_ret[1][0] == "date":
                date = tuple(code_ret[1][1:])
            if code_ret[1][0] == "author":
                author.append(code_ret[1][1])
            elif code_ret[1][0] == "label":
                add_in_label(label_list,code_ret[1][1],i)
            elif code_ret[1][0] in session:
                if code_ret[1][0] == "choice":
                    session[code_ret[1][0]].append(tuple(code_ret[1][1:]))
                    if len(code_ret[1])==3:
                        check_label(label_list,code_ret[1][2])
                else:
                    print("错误！第%d行：命令冲突",i)
                    is_correct = False
                    break
            else:
                if code_ret[1][0] == "choice":
                    session[code_ret[1][0]]=[tuple(code_ret[1][1:])]
                    if len(code_ret[1])==3:
                        check_label(label_list,code_ret[1][2])
                else:
                    session[code_ret[1][0]]=tuple(code_ret[1][1:])
                    if code_ret[1][0] == "goto":
                        check_label(label_list,code_ret[1][1])
        else:
            if session["str"]:
                session["str"] += "\n"
            session["str"] += sline

if is_correct:
    for k in label_list:
        if label_list[k]<0:
            print("错误！未定义标签 %s",k)
            is_correct = False
            break
if session["str"]:
    story.append(session)
# print(story)
# print(label_list)

story_json = {
    "title":title,
    "author":author,
    "date":date,
    "story":story,
    "label_list":label_list
}
with open('story.json', 'w',encoding="utf-8") as file:
    json.dump(story_json, file)
    file.close()