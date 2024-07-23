from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import urllib.parse
import time

# 웹 드라이버 설정 (webdriver_manager 사용)
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.lguplus.com/")

# 웹페이지 로드 대기 (최대 10초)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# 페이지 소스 가져오기
page_source = driver.page_source

# BeautifulSoup을 사용하여 페이지 파싱
soup = BeautifulSoup(page_source, 'lxml')

# 모든 링크 추출 (href와 id 속성 모두 포함)
links = soup.find_all('a', href=True)
ids = soup.find_all(id=True)
urls = [link['href'] for link in links]

# id 속성에서 URL 추출 및 실제 URL로 변환
for element in ids:
    element_id = element['id']
    try:
        element_to_click = driver.find_element(By.ID, element_id)
        driver.execute_script("arguments[0].click();", element_to_click)
        time.sleep(1)  # 페이지 로드 대기
        current_url = driver.current_url
        if current_url != "https://www.lguplus.com/":
            urls.append(current_url)
        driver.back()  # 원래 페이지로 돌아가기
        time.sleep(1)  # 페이지 로드 대기
    except Exception as e:
        print(f"Error clicking element with id {element_id}: {e}")

# 중복 제거 및 절대 경로로 변환
base_url = "https://www.lguplus.com"
unique_urls = list(set(urls))
absolute_urls = [urllib.parse.urljoin(base_url, url) for url in unique_urls]

# 웹 드라이버 종료
driver.quit()

# 결과를 텍스트 파일에 저장
with open('collected_urls.txt', 'w') as file:
    for url in absolute_urls:
        file.write(url + '\n')

print(f"총 {len(absolute_urls)}개의 URL이 수집되어 'collected_urls.txt' 파일에 저장되었습니다.")
