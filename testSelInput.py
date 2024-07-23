from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

# Chrome 설치 경로 설정
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # 예시 경로

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.binary_location = chrome_path
chrome_options.add_argument("--headless")  # 브라우저를 숨김 모드로 실행

# ChromeDriver 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
chrome_driver_path = os.path.join(current_dir, "chrome-win64", "chromedriver.exe")

# Check if the ChromeDriver path is correct
if not os.path.exists(chrome_driver_path):
    raise FileNotFoundError(f"ChromeDriver not found at path: {chrome_driver_path}")

# 웹 드라이버 설정
webdriver_service = Service(executable_path=chrome_driver_path)

# 웹 드라이버 시작
try:
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
except Exception as e:
    print(f"An error occurred while initializing the Chrome driver: {e}")
    raise

# 특정 사이트로 이동
driver.get("https://www.lguplus.com/benefit-event/ongoing/387")  # 대상 웹사이트 URL로 변경

# 페이지 로드 대기
time.sleep(5)  # 필요한 경우 명시적으로 대기

# 모든 input 요소 가져오기
input_elements = driver.find_elements(By.TAG_NAME, "input")

# 유효한 input 요소 필터링 (hidden 제외)
valid_inputs = []
for element in input_elements:
    input_type = element.get_attribute("type")
    input_id = element.get_attribute("id")
    if input_type != "hidden":
        valid_inputs.append({"id": input_id, "type": input_type})

# 결과 출력
for input_info in valid_inputs:
    print(f"ID: {input_info['id']}, Type: {input_info['type']}")

# 웹 드라이버 종료
driver.quit()
