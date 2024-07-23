import requests
from bs4 import BeautifulSoup

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

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTP 에러가 있는 경우 예외 발생

            soup = BeautifulSoup(response.content, 'html.parser')
            input_elements = soup.find_all(['input', 'select', 'textarea'])

            # hidden 타입이 아닌 input 요소만 찾기
            valid_inputs = [el for el in input_elements if el.name != 'input' or el.get('type') != 'hidden']

            if valid_inputs:
                input_urls.append(url)

                # 상위 N개 요소를 포함한 HTML 부분 추출
                input_html_parts = []
                for index, el in enumerate(valid_inputs, start=1):
                    current_el = el
                    for _ in range(parent_levels):
                        parent = current_el.find_parent()
                        if parent:
                            current_el = parent
                        else:
                            break
                    part_html = str(current_el)

                    # input 요소의 ID와 타입 가져오기
                    input_id = el.get('id', 'N/A')
                    input_type = el.get('type', 'N/A')

                    # 조건 파악을 위한 기본 논리 (여기서는 간단한 패턴 매칭)
                    condition = ''
                    if 'modal' in part_html.lower():
                        condition = 'This input appears within a modal dialog.'
                    else:
                        condition = 'This input does not have specific conditional visibility.'

                    # 번호 매기기 및 조건 추가
                    part_html = (f"<!-- Input {index}: {condition} -->\n"
                                 f"<div class='input-container'>\n"
                                 f"<p><strong>ID:</strong> {input_id} | <strong>Type:</strong> {input_type}</p>\n"
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
parent_levels = 2  # 원하는 상위 요소의 개수 설정

analyze_html(file_path, parent_levels)
