from playwright.sync_api import sync_playwright
import sqlite3
import time
#スター数順、更新日順、名前順の5パターンで取得する（全てのリポジトリを取得するため）
urls = [
    'https://github.com/orgs/google/repositories?sort=stargazers',
    'https://github.com/orgs/google/repositories?sort=updated&order=desc',
    'https://github.com/orgs/google/repositories?sort=updated&order=asc',
    'https://github.com/orgs/google/repositories?sort=name&order=asc', 
    'https://github.com/orgs/google/repositories?sort=name&order=desc', 
]
con = sqlite3.connect('./sai_git.sqlite')

cur = con.cursor()
#SQLを作成
cur.execute("""
CREATE TABLE IF NOT EXISTS git (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    repositories TEXT UNIQUE, 
    main_lan TEXT, 
    stars TEXT
)
""")
con.commit()

MAX_PAGES = None

page_num = 1

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for target_url in urls:
        print(f'\n==========================================')
        print(f'取得開始: {target_url}')
        print(f'==========================================')

        page.goto(target_url)
        page_num = 1  #パターンごとにページ数をリセット


    for target_url in urls:
        print(f'\n==========================================')
        print(f'取得開始: {target_url}')
        print(f'==========================================')

        page.goto(target_url)
        page_num = 1  #言語ごとにページ数をリセット


        while True:
            #ページ内の h4 要素が画面上に現れるまで待機
            try:
                page.wait_for_selector('h4', timeout=15000)
            except Exception:
                print('h4要素の読み込みに失敗したため、このパターンを終了します')
                break

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

                cur.execute(
                        'INSERT OR IGNORE INTO git (repositories, main_lan,'
                        ' stars) VALUES (?, ?, ?)',
                        (repositories, main_lan, stars),
                    )
                time.sleep(1)
            con.commit()

            #指定ページに達したら終了
            if MAX_PAGES and page_num >= MAX_PAGES:
                break
            next_button = page.query_selector('a.next_page, a[rel="next"]')
            if next_button and next_button.is_visible():
                    # ボタンが無効化（disabled）されていないか確認
                    is_disabled = next_button.get_attribute(
                        'aria-disabled'
                    ) == 'true' or 'disabled' in (
                        next_button.get_attribute('class') or ''
                    )
                    if is_disabled:
                        print('この言語の最終ページに到達しました')
                        break

                    next_button.click()
                    page_num += 1
                    time.sleep(2)
                
            else:
                print("次のページが見つからないので終了します")
                break

    browser.close()

count = cur.execute("SELECT COUNT(*) FROM git").fetchone()[0]
print(f'\n【全処理完了】 重複を除いた保存合計件数: {count} 件')
print("保存されたデータ")
cur.execute("SELECT * FROM git")
rows = cur.fetchall()
for row in rows:
    print(row)  

con.close()
print("保存が完了しました")
