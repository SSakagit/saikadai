import sqlite3

#データベースに接続
con = sqlite3.connect('./sai_git.sqlite')
cur = con.cursor()

#保存されている合計件数を表示
count = cur.execute('SELECT COUNT(*) FROM git').fetchone()[0]
print(f'保存されているリポジトリ合計件数: {count} 件')

#SELECT文で全データを取得して表示
cur.execute('SELECT repositories, main_lan, stars FROM git')
rows = cur.fetchall()

#enumerateを使って1から2945までの連番で表示
for idx, row in enumerate(rows, 1):
    print(f'No.{idx} | リポジトリ: {row[0]} | 言語: {row[1]} | スター数: {row[2]}')

#接続を閉じる
con.close()