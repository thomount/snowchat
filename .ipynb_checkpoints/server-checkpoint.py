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
    
    if un != None and au != None and us.get_auth(un) == au and us.findUser(tun) != None:
        ms.add_msg(un, tun, cont, time.strftime('%Y-%m-%d %H:%M:%S'))
        #return success
        return make_response("send success", 200)
    else:
        #return fail
        print(us.get_auth(un), au, type(us.get_auth(un)), type(au))
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
    #print(un, au, lid)
    if un != None and au != None and us.get_auth(un) == au:
        ret = ms.get_msgs(un, lid)  # return new message
        # make chat list to json
        return make_response(json.dumps(ret), 200)
    else:
        #error message
        return make_response("content error", 401)

def get_Auth():
    return random.randint(1, 10**8)

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
        self.conn = sqlite3.connect(self.source, check_same_thread=False)
        self.lock = RWLock()
    def update(self):
        pass
    def save(self):
        pass
    def findUser(self, username):
        self.lock.rAcquire()
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM user WHERE name = ?", (username,))
        ret = cur.fetchone()
        cur.close()
        self.lock.rRelease()
        return ret

    def addUser(self, un, pw, nn):
        
        if self.findUser(un) == None:
            self.lock.wAcquire()
            
            cur = self.conn.cursor()
            cur.execute("INSERT INTO user VALUES (?, ?, ?, 0, 0)", (un, pw, nn))
            cur.close()
            self.conn.commit()
            
            self.lock.wRelease()
            return True
        else:
            return False
    def debug(self):
        pass
    def login(self, un, pwd):
        u = self.findUser(un)
        if u != None and u[1] == pwd:
            self.lock.wAcquire()
            
            cur = self.conn.cursor()
            auth = get_Auth()
            cur.execute("UPDATE user SET stat = 1, auth = ? WHERE name = ?", (auth, un))
            cur.close()
            self.conn.commit()
            
            self.lock.wRelease()
            return auth
        else:
            return None
        
    def logout(self, un):
        u = self.findUser(un)        
        if u != None and u[4] == 1:
            self.lock.wAcquire()
            
            cur = self.conn.cursor()
            auth = get_Auth()
            cur.execute("UPDATE user SET stat = 0, auth = 0 WHERE name = ?", (un, ))
            cur.close()
            self.conn.commit()
            
            self.lock.wRelease()
            return True
        else:
            return False
    def chg_pwd(self, un, old_pwd, new_pwd):
        '''
        if self.users.get(un) != None:
            u = self.users[un]
            if u.password == old_pwd:
                u.change_passwd(new_pwd)
                return True
            else:
                return False
        else:
            return False
        '''
        return True
    def chg_nnm(self, un, new_nn):
        '''
        if self.users.get(un) != None:
            u = self.users[un]
            u.change_nname(new_nn)
            return True
        else:
            return False
        '''
        return True
    def get_auth(self, un):
        u = self.findUser(un)
        if u == None or u[3] == 0:
            return None
        else:
            return str(u[3])
    
        
class Message_pool:

        
    def __init__(self, file_name):
        self.source = file_name
        self.conn = sqlite3.connect(self.source, check_same_thread=False)
        self.rw = RWLock()
        #self.mesList = []
    def add_msg(self, a, b, cont, t):
        print("%s talk to %s at %s: %s" % (a, b, t, cont))
        #conn = sqlite3.connect(self.source)
        self.rw.wAcquire()

        cur = self.conn.cursor()
        cur.execute("SELECT tick FROM message ORDER BY tick DESC")
        last = cur.fetchone()
        if last != None:
            tick = last[0] + 1
        else:
            tick = 1
        cur.execute("INSERT INTO message VALUES (?, ?, ?, ?, ?)" , (a, b, cont, t, tick))
        cur.close()
        self.conn.commit()

        self.rw.wRelease()
    def get_msgs(self, a, st):
        self.rw.rAcquire()
        
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM message WHERE tick > ? AND (name1 = ? OR name2 = ?)", (st, a, a))
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
    #us = User_pool('users.txt')
    us = User_pool_db('users.db')
    ms = Message_pool('message.db')
    

if __name__ == '__main__':
    init()
    #test1()
    #global us, ms
    #watcher(us)
    #watcher(ms)
    
    app.run(host='0.0.0.0', port=80, debug = True) 