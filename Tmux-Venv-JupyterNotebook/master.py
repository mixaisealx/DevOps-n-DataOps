import os
import sys
import libtmux
import re
import time
import json
import shutil


re_pattern = r"http://localhost:(\d+)/tree\?token=([0-9a-f]+)"

def get_port_and_token(path):
    lines = None
    result = None
    while result == None:
        try:
            with open(path,'r') as f:
                lines = f.readlines()
            for line in lines:
                mth = re.search(re_pattern, line)
                if (mth):
                    result = (int(mth.group(1)), mth.group(2))
                    break
        except:
            time.sleep(1)
    return result


def get_window_id(window):
    try:
        return window.window_id
    except:
        return window._window_id

def act_start(running, count):
    maxid = 0
    if len(running) > 0:
        maxid = running[-1]['id'] + 1
    
    print("Initializing folders...", file=sys.stderr)
    cwd = os.getcwd()
    for n in range(maxid,maxid+count):
        print(f"* dir{str(n)}...")
        os.mkdir("dir"+str(n))
        os.chdir(cwd + "/dir"+str(n))
        
        os.system("python3 -m venv venv")
        os.system("venv/bin/python -m pip install jupyter > /dev/null")

        os.chdir(cwd)

    tserver = libtmux.Server()
    tsession = None
    twindow = None
    try:
        tsession = tserver.find_where({ "session_name": "jupyter-notebook-tmux" })
        if tsession is None:
            raise Exception()
        twindow = tsession.new_window(attach=False, window_name='notebook-'+str(maxid))
    except:
        tsession = tserver.new_session('jupyter-notebook-tmux')
        twindow = tsession.windows[0]
        twindow.rename_window('notebook-'+str(maxid))
    
    print("Initializing notebooks...", file=sys.stderr)
    print(f"* id-{str(maxid)}...", file=sys.stderr)
    pane = twindow.panes[0]
    pane.send_keys('cd dir'+str(maxid))  
    pane.send_keys('source venv/bin/activate')
    pane.send_keys('jupyter notebook --allow-root --ip localhost --no-browser 2>jupyter.log')
    port,token = get_port_and_token('dir'+str(maxid)+'/jupyter.log')
    running.append({'id':maxid, 'port':port, 'token':token, 'winid':get_window_id(twindow)})

    for n in range(maxid+1,maxid+count):
        print(f"* id-{str(n)}...", file=sys.stderr)
        twindow = tsession.new_window(attach=False, window_name='notebook-'+str(n))
        pane = twindow.panes[0]
        pane.send_keys('cd dir'+str(n))
        pane.send_keys('source venv/bin/activate')
        pane.send_keys('jupyter notebook --allow-root --ip localhost --no-browser 2>jupyter.log')
        port,token = get_port_and_token('dir'+str(n)+'/jupyter.log')
        running.append({'id':n, 'port':port, 'token':token, 'winid':get_window_id(twindow)})

    return running


def act_stop_all(running):
    tserver = libtmux.Server()
    tsession = tserver.find_where({ "session_name": "jupyter-notebook-tmux" })
    tsession.kill_session()
    
    cwd = os.getcwd()
    for d in running:
        shutil.rmtree(cwd+"/dir"+str(d['id']))

    return []
    

def act_stop(running, tid):
    tserver = libtmux.Server()
    tsession = tserver.find_where({ "session_name": "jupyter-notebook-tmux" })
    itemi = None
    for rn in range(len(running)):
        if running[rn]['id'] == tid:
            itemi = rn
            break
    if itemi == None:
        exit(8)
    
    try:
        twindow = None
        try:
            twindow = tsession.find_where({"window_id": running[itemi]['winid']})
            if twindow is None:
                raise Exception()
        except:
            twindow = tsession.find_where({"_window_id": running[itemi]['winid']})
            if twindow is None:
                raise Exception()
        
        try:
            twindow.kill_window() #Buggy old libtmux raises exception on the last service stop, but stops it
        except:
            if twindow is None:
                raise
        
        shutil.rmtree(os.getcwd()+"/dir"+str(tid))
        del running[itemi]
    except:
        exit(8)

    return running


def check_if_env_ok(running):
    dirs = [f for f in os.listdir() if not os.path.isfile(f) and f.startswith("dir")]
    if len(dirs) != len(running):
        return False

    tserver = libtmux.Server()
    tsession = None
    try:
        tsession = tserver.find_where({ "session_name": "jupyter-notebook-tmux" })
        if tsession is None:
            raise Exception()
    except:
        if len(dirs) == 0:
            return True
        else:
            return False

    if len(dirs) != len(tsession.windows):
        return False
    
    return True


def act_cleanup():
    tserver = libtmux.Server()
    try:
        tsession = tserver.find_where({ "session_name": "jupyter-notebook-tmux" })
        if tsession is None:
            raise Exception()
        tsession.kill_session()
    except:
        pass

    dirs = [f for f in os.listdir() if not os.path.isfile(f) and f.startswith("dir")]
    cwd = os.getcwd()
    for cdir in dirs:
        shutil.rmtree(os.getcwd()+"/"+cdir)

args = sys.argv[1:]

command = None
payload = None

if len(args) == 0:
    print("usage: main.sh {start|stop|stop_all} [i]")
    exit(8)
else:
    if args[0].lower() == "stop_all":
        command = "stop_all"
    elif len(args) == 1:
        print("usage: main.sh {start|stop} {i}")
    elif args[0].lower() in ["start", "stop"]:
        command = args[0].lower()
        payload = args[1]
    else:
        print("usage: main.sh {start|stop} {i}")


running = [ ]
try:
    with open("master.json", 'r') as f:
        running = json.load(f)
except:
    pass

if len(running) > 0:
    sorted(running, key=lambda x: x['id'])


if command == "start":
    if not check_if_env_ok(running):
        print("Envirionment corrupted! Cleanup...", file=sys.stderr)
        act_cleanup()
        running = []

    count = int(payload)
    if count < 1:
        exit(8)
    running = act_start(running, count)
    for pt in range(len(running)-count,len(running)):
        tmp = running[pt]
        print("notebook: id "+str(tmp['id'])+" ; port "+ str(tmp['port']) + " ; token " + tmp['token'], file=sys.stderr)
    print("Done!")

if command == "stop_all":
    if not check_if_env_ok(running):
        print("Envirionment corrupted! Cleanup...", file=sys.stderr)
        act_cleanup()
        running = []
    else:
        running = act_stop_all(running)
    print("Done!")


if command == "stop":
    if not check_if_env_ok(running):
        print("Envirionment corrupted! Cleanup...", file=sys.stderr)
        act_cleanup()
        running = []
    else:
        tid = int(payload)
        running = act_stop(running, tid)
    print("Done!")

with open("master.json", 'w') as f:
    json.dump(running, f)

