from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

# 현재 디렉터리의 chromedriver를 사용하여 웹드라이버 설정
current_directory = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = os.path.join(current_directory, 'chromedriver.exe')

options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 브라우저 창을 열지 않고 실행

# 최신 Selenium 버전에서는 아래와 같이 경로를 직접 설정합니다.
service = webdriver.chrome.service.Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

# URL로 이동
url = 'https://www.lguplus.com/benefit-event/ongoing/387'
driver.get(url)

# 페이지가 완전히 로드되도록 기다림
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)

# 페이지 소스를 BeautifulSoup으로 파싱
soup = BeautifulSoup(driver.page_source, 'html.parser')

# 사용자 입력 요소 찾기
input_elements = soup.find_all(['input', 'textarea', 'select'])
label_elements = soup.find_all('label')

# 각 요소의 속성 출력
for element in input_elements:
    element_type = element.get('type', 'textarea/select')
    if element_type in ['text', 'email', 'password', 'radio', 'checkbox', 'submit', 'tel']:
        print(f"Type: {element_type}, Name: {element.get('name')}, ID: {element.get('id')}, Value: {element.get('value')}, Placeholder: {element.get('placeholder')}")

for label in label_elements:
    print(f"Label For: {label.get('for')}, Text: {label.text.strip()}")

# 다양한 사용자 인터랙션 수행
try:
    # 모든 input, textarea, select 요소에 대해서 인터랙션 수행
    for element in input_elements:
        element_id = element.get('id')
        element_type = element.get('type', 'textarea/select')
        
        if element_type == 'text':
            input_field = driver.find_element(By.ID, element_id)
            input_field.clear()
            input_field.send_keys('Sample Text')

        elif element_type == 'tel':
            input_field = driver.find_element(By.ID, element_id)
            input_field.clear()
            input_field.send_keys('01012345678')

        elif element_type == 'radio' or element_type == 'checkbox':
            input_field = driver.find_element(By.ID, element_id)
            if not input_field.is_selected():
                input_field.click()

        elif element.name == 'select':
            select_element = Select(driver.find_element(By.ID, element_id))
            select_element.select_by_index(0)  # 첫 번째 옵션 선택 (예시)

    # 인터랙션 후 새로 나타난 페이지 소스를 다시 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    new_input_elements = soup.find_all(['input', 'textarea', 'select'])

    for element in new_input_elements:
        element_type = element.get('type', 'textarea/select')
        if element_type in ['text', 'email', 'password', 'radio', 'checkbox', 'submit', 'tel']:
            print(f"Type: {element_type}, Name: {element.get('name')}, ID: {element.get('id')}, Value: {element.get('value')}, Placeholder: {element.get('placeholder')}")

except Exception as e:
    print(f"인터랙션 요소를 찾을 수 없습니다: {e}")

# Selenium 드라이버 종료
driver.quit()
