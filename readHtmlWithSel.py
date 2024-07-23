from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def save_html(url, file_name):
    # Chrome 옵션 설정 (백그라운드 실행)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 헤드리스 모드로 실행 (브라우저 창을 띄우지 않음)
    chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (헤드리스 모드에서 권장)
    chrome_options.add_argument("--no-sandbox")  # 보안 옵션 비활성화 (Linux 환경에서 필요할 수 있음)
    chrome_options.add_argument("--disable-web-security")  # CORS 정책 비활성화
    chrome_options.add_argument("--disable-site-isolation-trials")  # 사이트 격리 비활성화

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

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_content)

        print(f"HTML content saved to {file_name}")
    finally:
        # WebDriver 종료
        driver.quit()

# 사용 예시
url = "https://www.lguplus.com/benefit-event/ongoing/387"
file_name = "example3.html"
save_html(url, file_name)
