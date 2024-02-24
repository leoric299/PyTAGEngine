from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os
from urllib import parse
import json
import importlib
import copy

story_json = {}
with open("story.json",encoding="utf-8") as file:
    story_json = json.load(file)
    file.close()

player_state = {}
with open("player_save.json",encoding="utf-8") as file:
    player_state = json.load(file)
    file.close()

def save_player():
    global player_state
    with open("player_save.json","w",encoding="utf-8") as file:
        json.dump(player_state, file)
        file.close()

def DoScheme(scheme):
    ret = []
    _output = {}
    for task in scheme:
        ret.append({
            "input":_output,
            "output":{},
            "parameter":task["parameter"],
        })
        modulename = task["path"]+task["name"]
        modulename = modulename.replace("./", "");
        modulename = modulename.replace("/", ".");
        tasklib = importlib.import_module(modulename)
        _output = tasklib.main(_input=_output, _parameter=task["parameter"])
        ret[-1]["output"] = _output
    return {"result":ret}

def GetParam(query):
    param = {}
    cparams = query.split('&')
    for c in cparams:
        d = c.split('=')
        if len(d)==2:
            param[d[0]] = d[1]
    return param 

def JSONexpand():
    pass


# choice_value:
# -2: reset
# -1: current (default / init)
# 0: enter
# 1: [1]
# 2: [2]
# 3: [3]
# 4: [4]

class Handler(BaseHTTPRequestHandler):
        """docstring fos Handler"""
        def do_GET(self):
            req = parse.urlparse(self.path)
            print(req.path)
            print(req.query)
            # print(GetParam(req.query))
            # print(self.headers)
            path = './web'+req.path # os.path.join('./web',req.path)
            param = GetParam(req.query)
            if req.path == '/':
                choice_value = int(param.get('choice','-1'))
                current_pos = player_state["current_pos"]
                current_image = player_state["current_image"]
                print(choice_value)
                html = {}
                if choice_value == -2:
                    current_pos = 0
                elif choice_value == -1:
                    current_pos = current_pos
                elif "end" in story_json["story"][current_pos]:
                    current_pos = current_pos
                elif "choice" in story_json["story"][current_pos]:
                    user_choice = choice_value-1
                    if len(story_json["story"][current_pos]["choice"])>user_choice and user_choice>=0:
                        if len(story_json["story"][current_pos]["choice"][user_choice])>1:
                            lb = story_json["story"][current_pos]["choice"][user_choice][1]
                            current_pos = story_json["label_list"][lb]
                        else:
                            if "goto" in story_json["story"][current_pos]:
                                lb = story_json["story"][current_pos]["goto"][0]
                                current_pos = story_json["label_list"][lb]
                            else:
                                current_pos += 1
                elif "goto" in story_json["story"][current_pos]:
                    lb = story_json["story"][current_pos]["goto"][0]
                    current_pos = story_json["label_list"][lb]
                elif choice_value==0:
                    current_pos += 1
                else:
                    current_pos = current_pos
                html = copy.deepcopy(story_json["story"][current_pos])
                if "image" in story_json["story"][current_pos]:
                    current_image = story_json["story"][current_pos]["image"]
                player_state["current_pos"] = current_pos
                player_state["current_image"] = current_image
                save_player()
                if choice_value == -1:
                    html["title"] = story_json["title"]
                    html["author"] = story_json["author"]
                    html["date"] = story_json["date"]
                    html["image"] = current_image
                self.send_response(200)
                self.send_header('Content_type','text/html;charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(html).encode())
            else:
                try:
                    ender = path.split('.')[-1]
                    if ender == "png":
                        f = open(path, 'rb')
                        html = f.read()
                        f.close()
                        self.send_response(200)
                        self.send_header('Content_type','image/png')
                        self.end_headers()
                        self.wfile.write(html)
                    else:
                        f = open(path, 'r',encoding="utf-8")
                        html = f.read()
                        f.close()
                        self.send_response(200)
                        self.send_header('Content_type','text/html;charset=utf-8')
                        self.end_headers()
                        self.wfile.write(html.encode())
                except Exception as e:
                    print(e)
                    self.send_response(404)
                    self.send_header('Content_type','text/plain;charset=utf-8')
                    self.end_headers()
                    # self.wfile.write(str(e).encode())

        def do_POST(self):
            if self.path == "/do":
                print('post do ----------------')
                req_datas = self.rfile.read(int(self.headers['content-length']))
                scheme_json = json.loads(req_datas)
                ret_json = DoScheme(scheme_json["scheme"])
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(ret_json).encode())
            else:
                path = './web/clientdata' + self.path
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE':self.headers['Content-Type'],
                    }
                )
                # print(form['file'].value)
                # req_datas = self.rfile.read(int(self.headers['content-length'])) #重点在此步!
                try:
                    f = open(path,'wb')
                    f.write(form['file'].value)
                    f.close()
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                except Exception as e:
                    print(e)
                    self.send_response(404)
                    self.send_header('Content_type','text/plain;charset=utf-8')
                    self.end_headers()

            # print(req_datas.decode())
            # data = {
            #     'result_code': '2',
            #     'result_desc': 'Success',
            #     'timestamp': '',
            #     'data': {'message_id': '25d55ad283aa400af464c76d713c07ad'}
            # }
            

if __name__=='__main__':
    port = 9999
    ip_localhost = '127.0.0.1'
    # ip_inner = '10.134.52.188'
    # ip_outer = 'gametable.xyz'
    homepage = 'VGUI.html'
    server_address=('',9999)
    httpd=HTTPServer(server_address,Handler)
    print('服务已启动，请访问：')
    print('http://'+ip_localhost+':'+str(port)+'/'+homepage)
    # print('http://'+ip_inner+':'+str(port)+'/'+homepage)
    # print('http://'+ip_outer+':'+str(port)+'/'+homepage)
    httpd.serve_forever()