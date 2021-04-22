
import requests
 
formdata = {
    'username': 'lzx',
    'password': '123456',
    "auth": "81702903",
    'content': 'I love Xin Xin'
}
 
url = "http://47.97.152.52/send"
 
headers={ "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
 
response = requests.post(url, data = formdata, headers = headers)
 
print(response.text)
