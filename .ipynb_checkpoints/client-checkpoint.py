import requests

def send(sub_url, data):
    headers={ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
    code = 401
    try_time = 0
    while code != 200 and try_time < 5:
        response = requests.post('http://47.97.152.52/'+sub_url, data = data, headers = headers)
        try_time += 1
        code = response.status_code
    if try_time == 5:
        print('error code =', code)
        return None
    return response

class User:
    def __init__(self, u, a):
        self.d = {}
        self.d['username'] = u
        self.d['auth'] = a
        self.ums = {}
        self.msgs = []

    def send(self, t, m):
        self.d['content'] = m
        self.d['target'] = t
        send('send', self.d)
    def mes(self):
        self.d['lid'] = self.msgs[-1][4] if len(self.msgs) > 0 else -1
        #print(self.d['lid'])
        ret = send('content', self.d)
        if ret != None:
            msgs = eval(ret.text)
            #print('ret = ', ret.text)
            for msg in msgs:
                if msg[0] != self.d['username']:
                    if self.ums.get(msg[0]) == None:
                        self.ums[msg[0]] = []
                    self.ums[msg[0]].append(msg)
                if msg[1] != self.d['username']:
                    if self.ums.get(msg[1]) == None:
                        self.ums[msg[1]] = []
                    self.ums[msg[1]].append(msg)        
            #print(ret.text)
            self.msgs += msgs
    def friends(self):
        self.mes()
        return self.ums.keys()

    def show(self, tar = None):
        self.mes()
        if tar == None:
            return self.msgs
        elif self.ums.get(tar) != None:
            return self.ums[tar]
        else:
            return []

class System:
    def __init__(self):
        self.user = None
    def login(self, username, password):
        if self.user != None:
            print('Already Login')
            return
        
        ret = send('login', {'username': username, 'password': password})
        if ret != None:
            self.user = User(username, eval(ret.text)['auth'])
    def register(self, username, password1, password2):
        if self.user != None:
            print('Already login')
            return
        
        if password1 != password2:
            return
        send('register', {'username': username, 'password': password1})
    def logout(self):
        if self.user == None:
            print('Not login yet')
            return
        self.user = None
        print('logout success')
    def send(self, tar, message):
        if self.user == None:
            print('Not login yet')
            return
        self.user.send(tar, message)
    def friends(self):
        if self.user == None:
            print('Not login yet')
            return
        self.user.friends()
    def show(self, friend):
        if self.user == None:
            print('Not login yet')
            return
        for msg in self.user.show(friend):
            print(msg)
    def history(self):
        if self.user == None:
            print('Not login yet')
            return
        for msg in self.user.show():
            print(msg)
                

if __name__ == '__main__':
    system = System()
    while True:
        order = input()
        fpos = order.find(' ')
        if fpos != -1:
            op = order[:fpos].lower()
        else:
            op = order
        if op == 'login':
            params = order[fpos+1:].split()
            if len(params) == 2:
                system.login(params[0], params[1])
            else:
                print('params error')
        elif op == 'register':
            params = order[fpos+1:].split()
            if len(params) == 3:
                system.register(params[0], params[1], params[2])
            else:
                print('params error')
        elif op == 'logout':
            system.logout()
        elif op == 'send':
            so = order[fpos+1:]
            npos = so.find(' ')
            system.send(so[:npos], so[npos+1:])
        elif op == 'list':
            system.history()
        elif op == 'chat':
            params = order[fpos+1:].split()
            system.show(params[0])
            
        
            
        