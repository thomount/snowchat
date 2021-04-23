from flask import Flask, make_response, request
import time
import random
import json
import sqlite3
import threading
app = Flask(__name__)

from threading import Thread
from time import sleep


def asy(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


@asy
def watcher(A):
    while True:
        sleep(3)
        A.debug()
        A.update()

@app.route('/')
def index():
    return 'Hello World'
@app.route('/register', methods=['POST'])
def reg():
    #register new user
    global us, ms
    uname = request.form.get('username')
    pwd = request.form.get('password')
    nname = uname
    ret = us.addUser(uname, pwd, nname)
    if ret == True:
        #return success
        return make_response("reg success", 200)
    else:
        #return fail
        return make_response("reg error", 401)
    
@app.route('/login', methods=['POST'])
def login():
    #login with user
    global us, ms
    uname = request.form.get('username')
    pwd = request.form.get('password')
    ret = us.login(uname, pwd)
    if ret != None:
        #return success
        return make_response(json.dumps({"auth":ret}), 200)
    else:
        #return fail
        return make_response("login error", 401)        
    
@app.route('/send', methods=['POST'])
def send():
    # send message
    global us, ms
    un = request.form.get('username')
    au = request.form.get('auth')
    tun = request.form.get('target')
    cont = request.form.get('content') # last chat id
    
    if un != None and au != None and us.get_auth(un) == au and us.users.get(tun) != None:
        ms.add_msg(un, tun, cont, time.strftime('%Y-%m-%d %H:%M:%S'))
        #return success
        return make_response("send success", 200)
    else:
        #return fail
        return make_response("send error", 401)

@app.route('/search', methods=['POST'])
def search():
    # search for history
    return "search not support"

@app.route('/content', methods=['POST'])
def get_content():
    # get normal content
    global us, ms
    un = request.form.get('username')
    au = request.form.get('auth')
    lid = request.form.get('lid') # last chat id
    print(un, au, lid)
    if un != None and au != None and us.get_auth(un) == au:
        ret = ms.get_msgs(un, lid)  # return new message
        # make chat list to json
        return make_response(json.dumps(ret), 200)
    else:
        #error message
        return make_response("content error", 401)

def get_Auth():
    return str(random.randint(0, 10**8))

class User:
    def __init__(self):
        self.uname = None
        self.password = None
        self.nname = None
        self.state = False
        self.clean = True
    def write(self, f):
        for c in self.uname:
            print(ord(c), end = ',', file = f)
        print(file = f)
        for c in self.password:
            print(ord(c), end = ',', file = f)
        print(file = f)
        for c in self.nname:
            print(ord(c), end = ',', file = f)
        print(file = f)
    def read(self, f):
        self.uname = ''.join([chr(c) for c in eval('['+f.readline()+']')])
        self.password = ''.join([chr(c) for c in eval('['+f.readline()+']')])
        self.nname = ''.join([chr(c) for c in eval('['+f.readline()+']')])
        return self
    def create(self, un, pw, nn):
        self.uname = un
        self.password = pw
        self.nname = nn
        self.clean = False
        return self
    def login(self):
        self.state = True
        self.auth = get_Auth()
        return self.auth
    def logout(self):
        self.state = False
        self.auth = None
    def change_nname(self, nname):
        self.clean = False
        self.nname = nname
    def change_passwd(self, pwd):
        self.clean = False
        self.password = pwd
        
class User_pool:      
    def __init__(self, file_name):
        self.source = file_name
        self.users = {}
        try:
            fi = open(file_name, 'r')
        except:
            fi = None
        if fi != None:
            self.n = eval(fi.readline())
            for i in range(self.n):
                u = User().read(fi)
                self.users[u.uname] = u
            fi.close()
    def update(self):
        clean = True
        for user in self.users.values():
            if user.clean == False:
                clean = False
                break
        if clean == False:
            self.save()
    def save(self):
        fo = open(self.source, 'w')
        print(len(self.users), file = fo)
        for user in self.users.values():
            user.write(fo)
            user.clean = True
        fo.close()
    def addUser(self, un, pw, nn):
        if self.users.get(un) == None:
            self.users[un] = User().create(un, pw, nn)
            return True
        else:
            return False
    def debug(self):
        for user in self.users.values():
            print(user.uname, user.password, user.nname)
    def login(self, un, pwd):
        if self.users.get(un) != None:
            u = self.users[un]
            if u.password == pwd:
                return u.login()
            else:
                return None
        else:
            return None
        
    def logout(self, un):
        if self.users.get(un) != None:
            u = self.users[un]
            if u.state == True:
                u.logout()
                return True
            else:
                return False
        else:
            return False
    def chg_pwd(self, un, old_pwd, new_pwd):
        if self.users.get(un) != None:
            u = self.users[un]
            if u.password == old_pwd:
                u.change_passwd(new_pwd)
                return True
            else:
                return False
        else:
            return False
    def chg_nnm(self, un, new_nn):
        if self.users.get(un) != None:
            u = self.users[un]
            u.change_nname(new_nn)
            return True
        else:
            return False
    def get_auth(self, un):
        if self.users.get(un) == None or self.users[un].auth == None:
            return None
        else:
            return self.users[un].auth
        
class RWLock:
    def __init__(self):
        self.rlock = threading.Lock()
        self.rnum = 0
        self.wlock = threading.Lock()
    def rAcquire(self):
        self.rlock.acquire()
        self.rnum += 1
        if self.rnum == 1:
            self.wlock.acquire()
        self.rlock.release()
    def rRelease(self):
        self.rlock.acquire()
        self.rnum -= 1
        if self.rnum == 0:
            self.wlock.release()
        self.rlock.release()
    def wAcquire(self):
        self.wlock.acquire()
    def wRelease(self):
        self.wlock.release()
        
class User_pool_db:
    def __init__(self, file_name):
        self.source = file_name
    
        
class Message_pool:

        
    def __init__(self, file_name):
        self.source = file_name
        self.conn = sqlite3.connect(self.source, check_same_thread=False)
        self.rw = RWLock()
        #self.mesList = []
    def add_msg(self, a, b, cont, t):
        #conn = sqlite3.connect(self.source)
        self.rw.wAcquire()

        cur = self.conn.cursor()
        cur.execute("SELECT tick FROM message ORDER BY tick DESC")
        last = cur.fetchone()
        if last != None:
            tick = last[0] + 1
        else:
            tick = 1
        cur.execute("INSERT INTO message VALUES ('%s', '%s', '%s', '%s', '%f')" % (a, b, cont, t, tick))
        cur.close()
        self.conn.commit()

        self.rw.wRelease()
    def get_msgs(self, a, st):
        self.rw.rAcquire()
        
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM message WHERE name1 = ? OR name2 = ? AND tick > ?", (a, a, st))
        ret = cur.fetchall()
        cur.close()
        
        self.rw.rRelease()
        return ret
    def update(self):
        pass
    def debug(self):
        self.rw.rAcquire()
        
        cur = self.conn.cursor()
        for row in cur.execute("SELECT * FROM message ORDER BY tick"):
            print(row)
        cur.close()

        self.rw.rRelease()

us = None
ms = None
def init():
    global us, ms
    us = User_pool('users.txt')
    ms = Message_pool('message.db')
    

if __name__ == '__main__':
    init()
    #test1()
    #global us, ms
    watcher(us)
    watcher(ms)
    
    app.run(host='0.0.0.0', port=80, debug = True) 