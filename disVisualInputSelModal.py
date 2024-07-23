from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def analyze_html(file_path, parent_levels):
    input_urls = []
    error_urls = []

    # 파일에서 URL 읽기
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file.readlines()]
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 셀레니움 드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for url in urls:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'body')))

            # JavaScript로 모든 모달을 열기
            driver.execute_script("""
                var modals = document.querySelectorAll('[data-toggle="modal"], [data-bs-toggle="modal"]');
                modals.forEach(function(modal) {
                    modal.click();
                });
            """)
            time.sleep(2)  # 모달이 열릴 시간을 줌

            # 특정 속성을 가진 버튼 클릭
            buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-gtm-event-name="button_click"]')
            for button in buttons:
                try:
                    button.click()
                    time.sleep(1)  # 각 버튼 클릭 후 약간의 시간을 줌
                except Exception as e:
                    print(f"Error clicking button: {e}")

            time.sleep(2)  # 모든 버튼 클릭 후 페이지가 업데이트 될 시간을 줌

            # 열려 있는 모든 모달의 내용을 포함하여 페이지 소스 가져오기
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            input_elements = soup.find_all(['input', 'select', 'textarea'])

            # 추가로 blind 클래스의 부모 요소 안의 input 요소도 찾기
            blind_parents = soup.find_all(class_='blind')
            for blind_parent in blind_parents:
                input_elements.extend(blind_parent.find_all(['input', 'select', 'textarea']))

            # hidden 타입이 아닌 input 요소만 찾기
            valid_inputs = [el for el in input_elements if el.name != 'input' or el.get('type') != 'hidden']

            if valid_inputs:
                input_urls.append(url)

                # 상위 N개 요소를 포함한 HTML 부분 추출
                container_dict = {}
                for el in valid_inputs:
                    current_el = el
                    for _ in range(parent_levels):
                        parent = current_el.find_parent()
                        if parent:
                            current_el = parent
                        else:
                            break
                    part_html = str(current_el)

                    if part_html not in container_dict:
                        container_dict[part_html] = []

                    # input 요소의 ID와 타입 가져오기
                    input_id = el.get('id', 'N/A')
                    input_type = el.get('type', 'N/A')
                    container_dict[part_html].append((input_id, input_type))

                # 중복된 상위 요소를 포함한 HTML 부분에서 ID와 타입 정보를 추가
                input_html_parts = []
                for part_html, inputs in container_dict.items():
                    inputs_info = "\n".join([f"<p><strong>ID:</strong> {input_id} | <strong>Type:</strong> {input_type}</p>"
                                             for input_id, input_type in inputs])

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

# URL을 포함하는 파일 경로와 상위 요소 개수 변수 설정
file_path = 'collected_urls.txt'
parent_levels = 3  # 원하는 상위 요소의 개수 설정

analyze_html(file_path, parent_levels)
