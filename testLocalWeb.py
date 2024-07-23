from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 웹 드라이버 경로 (절대 경로 사용)
driver_path = 'D:/study/python/work/chromedriver.exe'  # 실제 존재하는 절대 경로로 변경 필요

# 웹 드라이버 서비스 설정
service = Service(driver_path)

# 웹 드라이버 옵션 설정
options = webdriver.ChromeOptions()

# 웹 드라이버 초기화
driver = webdriver.Chrome(service=service, options=options)
driver.get('https://www.lguplus.com/login/uplus-register/personal')  # 접근할 URL로 변경

# 모달이 열리는 버튼을 클릭
try:
    modal_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@onclick=\"$_openPopup('EventContent', ''); return false;\"]"))
    )
    modal_button.click()
except Exception as e:
    print("모달 버튼을 클릭하는 중 오류 발생:", e)

# 모달이 열리는 것을 기다림 (모달 내의 특정 요소를 대기)
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@id='EventContent']"))  # 모달의 특정 요소 ID로 변경
    )
except Exception as e:
    print("모달을 기다리는 중 오류 발생:", e)

# 모달 내의 모든 input 요소 찾기
inputs = driver.find_elements(By.TAG_NAME, 'input')

input_details = []

# input 요소들의 id와 type을 추출
for input_element in inputs:
    input_type = input_element.get_attribute('type')
    input_id = input_element.get_attribute('id')
    
    input_details.append({
        'id': input_id,
        'type': input_type
    })

# 웹 드라이버 종료
driver.quit()

# 결과 출력
for detail in input_details:
    print(f"ID: {detail['id']}, Type: {detail['type']}")
