import requests
from bs4 import BeautifulSoup

def analyze_html(file_path):
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

                # 상위 4개 요소를 포함한 HTML 부분 추출
                input_html_parts = []
                for el in valid_inputs:
                    parent1 = el.find_parent()
                    parent2 = parent1.find_parent() if parent1 else None
                    parent3 = parent2.find_parent() if parent2 else None
                    parent4 = parent3.find_parent() if parent3 else None
                    part_html = str(parent4) if parent4 else str(parent3) if parent3 else str(parent2) if parent2 else str(parent1) if parent1 else str(el)
                    input_html_parts.append(part_html)
                
                input_html = '\n'.join(input_html_parts)
                
                # 해당 URL의 HTML 파일로 저장
                filename = url.replace('http://', '').replace('https://', '').replace('/', '_') + '.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(input_html)
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

# URL을 포함하는 파일 경로
file_path = 'collected_urls.txt'

analyze_html(file_path)
