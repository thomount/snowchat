import os
import sqlite3

os.system('rm users.db')
os.system('touch users.db')
os.system('rm message.db')
os.system('touch message.db')

conn= sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute("CREATE TABLE user(name char(20), password char(20), nickname char(20), auth int, stat int)")
cur.close()
conn.commit()
conn.close()

conn= sqlite3.connect('message.db')
cur = conn.cursor()
cur.execute("CREATE TABLE message(name1 char(20), name2 char(20), content text, time char(100), tick int)")
cur.close()
conn.commit()
conn.close()