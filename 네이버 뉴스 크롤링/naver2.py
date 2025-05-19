import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 사용자 입력
query = input("검색할 키워드를 입력하세요: ").strip()
start_date = input("시작 날짜를 입력하세요 (예: 2016.08.19): ").strip()
end_date = input("종료 날짜를 입력하세요 (예: 2016.08.21): ").strip()
page_count = int(input("크롤링할 페이지 수를 입력하세요 (1페이지 = 10개 기사): ").strip())

# URL 구성
encoded_query = requests.utils.quote(query)
base_url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}&sm=tab_pge&sort=0&photo=0&field=0&pd=3&ds={start_date}&de={end_date}&start="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

titles = []

for i in range(page_count):
    start = 1 + i * 10
    url = base_url + str(start)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 뉴스 제목 크롤링 (현재 네이버 뉴스의 구조 기반)
    title_tags = soup.select('span.sds-comps-text-type-headline1')
    page_titles = [tag.text.strip() for tag in title_tags]

    if not page_titles:
        print(f"{i+1}페이지에서 더 이상 기사를 찾을 수 없습니다.")
        break

    titles.extend(page_titles)
    print(f"{i+1}페이지 수집 완료 (누적 {len(titles)}개)")
    time.sleep(1)  # 과도한 요청 방지

# 결과 저장
filename = f"naver_news_titles_{query}_{start_date}_to_{end_date}.xlsx"
df = pd.DataFrame(titles, columns=["제목"])
df.to_excel(filename, index=False)

print(f"\n✅ 저장 완료: {filename}")
