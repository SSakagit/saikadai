import requests 
import sqlite3

url = 'https://github.com/google'

res = requests.get(url)

#sqlの接続
path = './db/sai.db'

db_name = 'sai_git.sqlite'

con = sqlite3.connect(path + db_name)

cur = con.cursor()

cur.execute("""CREATE TABLE git(id INTEGER PRIMARY KEY AUTOINCREMENT, repositories TEXT, main_lan TEXT , stars INTEGER, )""")
con.commit()
print('保存が完了しました')
con.close()
