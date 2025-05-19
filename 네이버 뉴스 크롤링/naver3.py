# 필요한 라이브러리 import
from selenium import webdriver  # 웹 자동화를 위한 셀레니움 라이브러리
from selenium.webdriver.chrome.service import Service  # 크롬 드라이버 서비스 설정
from selenium.webdriver.common.by import By  # 요소를 찾기 위한 By 클래스
from bs4 import BeautifulSoup  # HTML 파싱을 위한 뷰티풀수프
from datetime import datetime  # 현재 시간을 저장하기 위한 datetime 모듈
import time  # 대기 시간 설정을 위한 time 모듈
import pandas as pd  # 데이터프레임으로 저장하기 위한 pandas

# --- 사용자 입력 ---
# 검색 키워드, 시작/종료 날짜, 크롤링할 페이지 수를 사용자에게 입력받음
search = input("검색할 키워드를 입력하세요 (예: 캠핑): ").strip()
start_date = input("시작 날짜를 입력하세요 (예: 2016.08.19): ").strip()
end_date = input("종료 날짜를 입력하세요 (예: 2016.08.21): ").strip()
num_pages = int(input("크롤링할 총 페이지 수를 입력하세요 (1페이지당 10개 기사): "))

# --- 검색어 및 날짜 포맷 가공 ---
# 검색어의 공백을 '+'로 변경하여 URL 인코딩 형식에 맞춤
query = search.replace(" ", "+")
# 날짜 포맷 유지 (추후 확장 가능성 고려해 변수로 유지)
start_date_fmt = start_date.replace(".", ".")
end_date_fmt = end_date.replace(".", ".")

# --- Chrome 드라이버 설정 ---
# 크롬 드라이버 실행 경로를 설정하고 옵션 추가
service = Service(executable_path="chromedriver.exe")  # chromedriver.exe의 경로 설정
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 브라우저 UI 없이 실행 (백그라운드 실행)
options.add_argument("--no-sandbox")  # 샌드박스 사용 안함 (리눅스 환경에서 유용)
options.add_argument("--disable-dev-shm-usage")  # 메모리 공유 제한 해제

# 위 설정을 기반으로 Chrome 웹드라이버 실행
driver = webdriver.Chrome(service=service, options=options)

# --- 데이터 저장용 리스트 초기화 ---
titles = []  # 기사 제목 저장 리스트
links = []   # 기사 링크 저장 리스트

# --- 페이지 루프 ---
# 지정한 페이지 수만큼 반복하며 URL 생성 및 크롤링 수행
for page in range(1, num_pages + 1):
    # 네이버 뉴스 검색 결과에서 시작 번호(start) 계산
    # 한 페이지당 10개 기사이므로 1페이지는 start=1, 2페이지는 start=11 ...
    start = 1 + (page - 1) * 10

    # 페이지별 검색 URL 구성
    url = (
        f"https://search.naver.com/search.naver?where=news&query={query}"
        f"&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={start_date_fmt}&de={end_date_fmt}"
        f"&start={start}"
    )

    # 해당 URL로 이동
    driver.get(url)
    time.sleep(2)  # 페이지가 완전히 로딩될 때까지 2초 대기

    # 페이지 HTML 파싱
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # 뉴스 제목과 링크가 포함된 a 태그를 선택 (네이버 뉴스 구조에 따라 클래스명은 변경될 수 있음)
    articles = soup.select("a.X0fMYp2dHd0TCUS2hjww")

    # 뉴스 기사가 하나도 없는 경우 경고 출력 후 다음 페이지로 넘어감
    if not articles:
        print(f"[{page}페이지] 기사를 찾을 수 없습니다.")
        continue

    # 기사 제목과 링크를 리스트에 저장
    for a in articles:
        titles.append(a.text.strip())        # 텍스트(제목) 저장
        links.append(a['href'].strip())      # 링크(href 속성) 저장

    print(f"[{page}페이지] 기사 {len(articles)}건 수집 완료")  # 현재 페이지의 수집 결과 출력

# --- 드라이버 종료 ---
driver.quit()  # 크롬 드라이버 종료

# --- 결과 저장 ---
# 수집한 데이터를 데이터프레임으로 변환
df = pd.DataFrame({'title': titles, 'link': links})

# 저장 시점의 날짜와 시간을 파일명에 포함
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# CSV 파일로 저장 (한글 깨짐 방지를 위해 'utf-8-sig' 인코딩 사용)
df.to_csv(f"naver_news_{search}_{timestamp}.csv", index=False, encoding='utf-8-sig')

# 수집 완료 메시지 출력
print(f"\n✅ 총 {len(df)}개의 기사 제목을 수집하고 CSV로 저장했습니다.")
