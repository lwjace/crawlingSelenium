from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def get_input_elements_with_parents(driver, parent_levels):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    input_elements = soup.find_all(['input', 'select', 'textarea'])

    # 추가로 blind 클래스의 부모 요소 안의 input 요소도 찾기
    blind_parents = soup.find_all(class_='blind')
    for blind_parent in blind_parents:
        input_elements.extend(blind_parent.find_all(['input', 'select', 'textarea']))

    # hidden 타입이 아닌 input 요소만 찾기
    valid_inputs = [el for el in input_elements if el.name != 'input' or el.get('type') != 'hidden']
    
    # 각 input 요소와 상위 N개의 HTML 부분을 수집
    input_with_parents = []
    for el in valid_inputs:
        current_el = el
        for _ in range(parent_levels):
            parent = current_el.find_parent()
            if parent:
                current_el = parent
            else:
                break
        input_with_parents.append((el, current_el))
    
    return input_with_parents

def get_label_text(element):
    # 먼저 for 속성을 사용하여 label을 찾습니다.
    label = element.find_parent().find('label', {'for': element.get('id')})
    if label:
        return label.get_text(strip=True)
    # 이전 형제 요소로 label을 찾기
    sibling_label = element.find_previous_sibling('label')
    if sibling_label:
        return sibling_label.get_text(strip=True)
    # 부모 요소의 텍스트를 사용합니다.
    parent = element.find_parent()
    if parent:
        return parent.get_text(strip=True)
    return 'N/A'

def analyze_html(file_path, parent_levels):
    input_urls = []
    error_urls = []
    input_data = []

    # 파일에서 URL 읽기
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file.readlines()]
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 셀레니움 드라이버 설정
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 같은 폴더에 있는 웹 드라이버 사용
    driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')  # .exe 확장자 확인
    driver = webdriver.Chrome(service=Service(driver_path), options=options)

    for url in urls:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'body')))

            # (필수) 또는 필수가 포함된 체크박스 클릭
            checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
            for checkbox in checkboxes:
                try:
                    label = checkbox.find_element(By.XPATH, './following-sibling::label')
                    if '(필수)' in label.text or '필수' in label.text:
                        driver.execute_script("arguments[0].click();", checkbox)
                        time.sleep(0.5)  # 각 체크박스 클릭 후 약간의 시간을 줌
                except Exception as e:
                    print(f"Error processing checkbox: {e}")

            # JavaScript로 모든 모달을 열기
            driver.execute_script("""
                var modals = document.querySelectorAll('[data-toggle="modal"], [data-bs-toggle="modal"]');
                modals.forEach(function(modal) {
                    modal.click();
                });
            """)
            time.sleep(2)  # 모달이 열릴 시간을 줌

            # 페이지 로드 후 초기 input 요소 수집
            initial_inputs_with_parents = get_input_elements_with_parents(driver, parent_levels)
            initial_input_set = set((el.get('id'), el.get('type')) for el, _ in initial_inputs_with_parents)
            
            # 초기 input 요소 HTML 저장
            initial_container_dict = {}
            for el, parent in initial_inputs_with_parents:
                part_html = str(parent)

                if part_html not in initial_container_dict:
                    initial_container_dict[part_html] = []

                # input 요소의 ID와 타입 가져오기
                input_id = el.get('id', 'N/A')
                input_type = el.get('type', 'N/A')
                input_label = get_label_text(el)
                placeholder = el.get('placeholder', 'N/A')
                parent_text = parent.get_text(strip=True)
                initial_container_dict[part_html].append((input_id, input_type, input_label, placeholder, parent_text, "Initial Load"))

            # 모든 button 요소 클릭
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            new_inputs_with_parents = []
            for button in buttons:
                try:
                    button_text = (button.text.strip() if button.text else None) or (button.get_attribute("aria-label").strip() if button.get_attribute("aria-label") else None) or (button.get_attribute("title").strip() if button.get_attribute("title") else None) or "Unknown Button"
                    button_id = button.get_attribute('id')
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(1)  # 각 버튼 클릭 후 약간의 시간을 줌

                    # 버튼 클릭 후 새롭게 발견된 input 요소 수집
                    current_inputs_with_parents = get_input_elements_with_parents(driver, parent_levels)
                    current_input_set = set((el.get('id'), el.get('type')) for el, _ in current_inputs_with_parents)
                    new_input_elements_with_parents = [(el, parent) for el, parent in current_inputs_with_parents if (el.get('id'), el.get('type')) not in initial_input_set]
                    new_inputs_with_parents.extend(new_input_elements_with_parents)

                    # 발견된 새 input 요소를 초기 input 집합에 추가
                    initial_input_set.update(current_input_set)
                    
                    # 버튼 클릭 후 추가된 input 요소 기록
                    for el, parent in new_input_elements_with_parents:
                        input_id = el.get('id', 'N/A')
                        input_type = el.get('type', 'N/A')
                        input_label = get_label_text(el)
                        placeholder = el.get('placeholder', 'N/A')
                        parent_text = parent.get_text(strip=True)
                        if input_label != '오늘 하루 그만보기':  # '오늘 하루 그만보기'를 제외
                            interaction = f"Button Click: {button_text}, ID: {button_id}"
                            input_data.append([url, input_id, input_type, input_label, placeholder, parent_text, "This input does not have specific conditional visibility.", interaction])

                except Exception as e:
                    print(f"Error clicking button: {e}")

            time.sleep(2)  # 모든 버튼 클릭 후 페이지가 업데이트 될 시간을 줌

            if initial_inputs_with_parents or new_inputs_with_parents:
                input_urls.append(url)

                # 상위 N개 요소를 포함한 HTML 부분 추출
                container_dict = initial_container_dict.copy()
                for el, parent in new_inputs_with_parents:
                    part_html = str(parent)

                    if part_html not in container_dict:
                        container_dict[part_html] = []

                    # input 요소의 ID와 타입 가져오기
                    input_id = el.get('id', 'N/A')
                    input_type = el.get('type', 'N/A')
                    input_label = get_label_text(el)
                    placeholder = el.get('placeholder', 'N/A')
                    parent_text = parent.get_text(strip=True)
                    container_dict[part_html].append((input_id, input_type, input_label, placeholder, parent_text, f"Button Click: {button_text}, ID: {button_id}"))

                # 중복된 상위 요소를 포함한 HTML 부분에서 ID와 타입 정보를 추가
                input_html_parts = []
                for part_html, inputs in container_dict.items():
                    inputs_info = "\n".join([f"<p><strong>ID:</strong> {input_id} | <strong>Type:</strong> {input_type} | <strong>Label:</strong> {input_label} | <strong>Placeholder:</strong> {placeholder} | <strong>Parent Text:</strong> {parent_text}</p>"
                                             for input_id, input_type, input_label, placeholder, parent_text, _ in inputs if input_label != '오늘 하루 그만보기'])

                    # 조건 파악을 위한 기본 논리 (여기서는 간단한 패턴 매칭)
                    condition = ''
                    if 'modal' in part_html.lower():
                        condition = 'This input appears within a modal dialog.'
                    else:
                        condition = 'This input does not have specific conditional visibility.'

                    # 번호 매기기 및 조건 추가
                    part_html = (f"<!-- Inputs Info: {inputs_info} -->\n"
                                 f"<div class='input-container'>\n"
                                 f"<p><strong>Condition:</strong> {condition}</p>\n"
                                 f"{inputs_info}\n"
                                 f"{part_html}\n"
                                 f"</div>")
                    input_html_parts.append(part_html)
                    
                    # 엑셀에 저장할 데이터 추가
                    for input_id, input_type, input_label, placeholder, parent_text, interaction in inputs:
                        if input_label != '오늘 하루 그만보기':  # '오늘 하루 그만보기'를 제외
                            input_data.append([url, input_id, input_type, input_label, placeholder, parent_text, condition, interaction])

                input_html = '\n'.join(input_html_parts)
                
                # HTML 파일에 CSS 추가
                html_content = f"""
                <html>
                <head>
                    <style>
                        .input-container {{
                            border: 1px solid #000;
                            padding: 10px;
                            margin: 10px 0;
                        }}
                    </style>
                </head>
                <body>
                    {input_html}
                </body>
                </html>
                """
                
                # 해당 URL의 HTML 파일로 저장
                filename = url.replace('http://', '').replace('https://', '').replace('/', '_') + '.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
        except Exception as e:
            error_urls.append((url, str(e)))

    driver.quit()

    # 입력 요소가 있는 사이트들의 URL을 파일에 저장
    with open('input_urls.txt', 'w') as f:
        for url in input_urls:
            f.write(f"{url}\n")

    # 에러가 발생한 사이트들의 URL과 에러 메시지를 파일에 저장
    with open('error_urls.txt', 'w') as f:
        for url, error in error_urls:
            f.write(f"{url} - {error}\n")

    # 수집한 데이터를 엑셀 파일로 저장
    df = pd.DataFrame(input_data, columns=['URL', 'Input ID', 'Input Type', 'Label', 'Placeholder', 'Parent Text', 'Condition', 'Interaction'])
    df.to_excel('input_data.xlsx', index=False)

# URL을 포함하는 파일 경로와 상위 요소 개수 변수 설정
file_path = 'collected_urls.txt'
parent_levels = 2  # 원하는 상위 요소의 개수 설정

analyze_html(file_path, parent_levels)
