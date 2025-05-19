import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

query = "캠핑"
encoded_query = requests.utils.quote(query)
base_url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}&sm=tab_pge&sort=0&photo=0&field=0&pd=3&ds=2016.08.19&de=2016.08.21&start="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

titles = []
start = 1

while True:
    url = base_url + str(start)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 현재 페이지에서 제목 추출
    title_tags = soup.select('span.sds-comps-text-type-headline1')
    page_titles = [tag.text.strip() for tag in title_tags]

    if not page_titles:
        break  # 제목이 없으면 마지막 페이지

    titles.extend(page_titles)
    print(f"{start}번부터 {start+9}번까지 수집 완료 (누적: {len(titles)}개)")
    start += 10
    time.sleep(1)  # 네이버 서버에 부담 주지 않기 위해 1초 쉬기

# 엑셀 저장
df = pd.DataFrame(titles, columns=["제목"])
df.to_excel("naver_news_all_titles_캠핑.xlsx", index=False)

print("전체 저장 완료: naver_news_all_titles_캠핑.xlsx")
