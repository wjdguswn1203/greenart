import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

# 기사 내용 요약 함수 (2~3줄 기준, 줄당 약 50자)
def summarize_article(text, max_chars=150, line_length=50):
    summary = text.strip().replace('\n', ' ').replace('\xa0', ' ')[:max_chars]
    lines = [summary[i:i+line_length] for i in range(0, len(summary), line_length)]
    return "\n".join(lines[:3])  # 최대 3줄

# 오늘 날짜 기반 파일명
today = datetime.today().strftime('%Y-%m-%d')
filename = f"news_titles_{today}.csv"

# 메인 뉴스 페이지 요청
url = "https://news.naver.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# 뉴스 제목과 링크 추출
news_items = soup.select('.cnf_news_area._cds_link._editn_link')
results = []

for item in news_items:
    title_tag = item.select_one('.cnf_news_title')
    if not title_tag:
        continue

    title = title_tag.get_text(strip=True)
    link = item.get('href')

    # 기사 본문 크롤링
    try:
        article_resp = requests.get(link, headers=headers, timeout=5)
        article_resp.raise_for_status()
        article_soup = BeautifulSoup(article_resp.text, 'html.parser')
        content_tag = article_soup.select_one('.go_trans._article_content')
        if content_tag:
            full_text = content_tag.get_text(strip=True)
            summary = summarize_article(full_text)
        else:
            summary = "본문 없음"
    except Exception as e:
        summary = f"오류: {e}"

    results.append((title, link, summary))
    print(f"✔ {title} - 요약 완료")
    time.sleep(0.5)

# CSV 저장
with open(filename, mode='w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['번호', '뉴스 제목', '링크', '기사 요약'])

    for idx, (title, link, summary) in enumerate(results, start=1):
        writer.writerow([idx, title, link, summary])

print(f"\n✅ 총 {len(results)}개의 뉴스가 '{filename}' 파일로 저장되었습니다.")
