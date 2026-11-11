from playwright.sync_api import sync_playwright
import sqlite3
import time

url = 'https://github.com/orgs/google/repositories'

#sqlの接続
path = './sai.db'

db_name = 'sai_git.sqlite'

con = sqlite3.connect(path + db_name)

cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS git(id INTEGER PRIMARY KEY AUTOINCREMENT, repositories TEXT, main_lan TEXT , stars TEXT)""")
con.commit()

MAX_PAGES = None

page_num = 1

with sync_playwright() as p:
    time.sleep(1)

    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    #h4が表示されるまで待つ
    page.wait_for_selector('h4')
    repo_elements = page.query_selector_all('li')


    while True:
        repo_elements = page.query_selector_all('li.public, li.private, #user-repositories-list li')
        repo_elements = page.query_selector_all('li')


        for repo in repo_elements:


            #リポジトリの取得
            repo_name = repo.query_selector('h4 a')

            #名前がない場合はスキップ
            if not repo_name:
                continue
            repositories = repo_name.inner_text().strip()
            #主要言語の取得
            lang_elem = repo.query_selector('span[class*="PrimaryLanguageName"]')
            main_lan = lang_elem.inner_text().strip() if lang_elem else "None"

            #スター数の取得
            star_elem = repo.query_selector('a:has(svg.octicon-star)')
            stars = star_elem.inner_text().strip() if star_elem else "0"

            print(f"リポジトリ:{repositories}, 主要言語: {main_lan}, スター数: {stars}")

            cur.execute("INSERT INTO git (repositories, main_lan, stars) VALUES (?, ?, ?)", (repositories, main_lan, stars))
            time.sleep(1)
        con.commit()

        #指定ページに達したら終了
        if MAX_PAGES and page_num >= MAX_PAGES:
            break
        next_button = page.query_selector('a[rel="next"]')
        if next_button and next_button.is_visible():
            next_button.click()
            page_num += 1
            time.sleep(2)
            
        else:
            print("次のページが見つからないので終了します")
            break

    browser.close()

count = cur.execute("SELECT COUNT(*) FROM git").fetchone()[0]
print("保存された件数:", count)
print("保存されたデータ")
cur.execute("SELECT * FROM git")
rows = cur.fetchall()
for row in rows:
    print(row)  

con.close()
print("保存が完了しました")
