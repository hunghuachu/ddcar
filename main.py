import requests
import pymysql
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

font_path = r'C:\Windows\Fonts\msjh.ttc' 

brands = ['Tesla', 'Hyundai', 'Bmw', 'Lexus', 'Nissan', 'Skoda', 'Volvo', 'Luxgen', 'Mercedes-Benz',
          'Toyota', 'Volkswagen', 'Ford', 'Hyundai', 'Jaguar', 'Kia', 'Mazda', 'Porsche', 'Audi']

db = pymysql.connect(
    host='localhost',
    user='root',
    password='c910910910',
    database='ddcar_news',
    charset='utf8mb4'
)
cursor = db.cursor()

headers = {
    'User-Agent': 'Mozilla/5.0'
}

def article_exists(title, posted_at):
    sql = "SELECT COUNT(*) FROM news WHERE title=%s AND posted_at=%s"
    cursor.execute(sql, (title, posted_at))
    return cursor.fetchone()[0] > 0

# 抓取分頁 page 1 ~ 10
max_page = 50
for page in range(1, max_page + 1):
    url = f'https://www.ddcar.com.tw/api/web/news/categories/articles/list/?cateId=0&page={page}'
    response = requests.get(url, headers=headers)
    data = response.json()
    articles = data.get('res', [])

    if not articles:
        print(f"Page {page} 無資料，停止抓取。")
        break

    print(f"處理 Page {page}...")

    for article in articles:
        title = article['title']
        posted_at = datetime.strptime(article['posted_at'], '%Y-%m-%d').date()
        content = article['summary']

        if article_exists(title, posted_at):
            print(f"已存在：{title}")
            continue

        cursor.execute(
            "INSERT INTO news (title, posted_at, content) VALUES (%s, %s, %s)",
            (title, posted_at, content)
        )
        db.commit()
        print(f"新增：{title}")

    page += 1

# 統計數量
cursor.execute("SELECT title, content FROM news")
all_texts = cursor.fetchall()

brand_counter = Counter()
for title, content in all_texts:
    text = (title or '') + ' ' + (content or '')
    text_lower = text.lower()
    for brand in brands:
        brand_lower = brand.lower()
        count = text_lower.count(brand_lower)
        brand_counter[brand] += count

print("\n品牌提及統計：")
for brand, count in brand_counter.items():
    print(f"{brand}: {count} 次")

cursor.close()
db.close()


brands_sorted = sorted(brand_counter.items(), key=lambda x: x[1], reverse=True)

names = [b for b, c in brands_sorted]
counts = [c for b, c in brands_sorted]

font_prop = FontProperties(fname=font_path)
plt.figure(figsize=(12, 6))
plt.bar(names, counts, color='skyblue')
plt.xlabel('品牌', fontproperties=font_prop)
plt.ylabel('提及次數', fontproperties=font_prop)
plt.title('品牌提及次數統計', fontproperties=font_prop)
plt.xticks(rotation=45, fontproperties=font_prop)
plt.tight_layout()
plt.show()
