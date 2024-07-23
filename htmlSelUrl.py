from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def save_html_and_extract_urls(url, html_file_name, urls_file_name):
    # Chrome 옵션 설정 (백그라운드 실행)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 헤드리스 모드로 실행 (브라우저 창을 띄우지 않음)
    chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (헤드리스 모드에서 권장)
    chrome_options.add_argument("--no-sandbox")  # 보안 옵션 비활성화 (Linux 환경에서 필요할 수 있음)

    # WebDriverManager를 사용하여 ChromeDriver 설치 및 설정
    service = Service(ChromeDriverManager().install())

    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 웹 페이지 요청
        driver.get(url)

        # 페이지 로드 대기 (필요에 따라 조정)
        time.sleep(3)  # JavaScript 로드 시간 대기

        # HTML 저장
        html_content = driver.page_source

        with open(html_file_name, 'w', encoding='utf-8') as file:
            file.write(html_content)

        # URL 추출
        soup = BeautifulSoup(html_content, 'html.parser')
        urls = set()
        for tag in soup.find_all(['a', 'link', 'img', 'script']):
            href = tag.get('href')
            src = tag.get('src')
            if href and href.startswith('http'):
                urls.add(href)
            if src and src.startswith('http'):
                urls.add(src)

        # URL 저장
        with open(urls_file_name, 'w', encoding='utf-8') as file:
            for url in urls:
                file.write(url + '\n')

        print(f"HTML content saved to {html_file_name}")
        print(f"URLs saved to {urls_file_name}")
    finally:
        # WebDriver 종료
        driver.quit()

# 사용 예시
url = "https://www.lguplus.com/"
html_file_name = "example.html"
urls_file_name = "urls.txt"
save_html_and_extract_urls(url, html_file_name, urls_file_name)
