
import requests

def send(sub_url, data):
    headers={ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
    response = requests.post('http://47.97.152.52/'+sub_url, data = data, headers = headers)
    return response

class User:
    def __init__(self, u, p):
        self.d = {}
        self.d['username'] = u
        self.d['password'] = p
        self.msgs = []
    def reg(self):
        ret = send('register', self.d)
    def login(self):
        ret = send('login', self.d)
        self.d['auth'] = eval(ret.text)['auth']
    def send(self, t, m):
        self.d['content'] = m
        self.d['target'] = t
        
        ret = send('send', self.d)
    def u_list(self):
        pass
    def mes(self):
        self.d['lid'] = self.msgs[-1][3] if len(self.msgs) > 0 else -1
        ret = send('content', self.d)
        #print(ret.text)
        self.msgs += eval(ret.text)
    def show(self):
        self.mes()
        print('user =', self.d['username'])
        for msg in self.msgs:
            print(msg)

pby = User('pby', '1234')
lzx = User('lzx', '4321')
admin = User('admin', 'admin')
pby.reg()
lzx.reg()
admin.reg()
pby.login()
lzx.login()
admin.login()
pby.send('lzx', 'i love you')
lzx.send('pby', 'qk')
admin.send('pby', 'hello world')
admin.send('pby', 'wdnmd')
pby.send('admin', 'cnm')
pby.show()
admin.show()
lzx.show()

    