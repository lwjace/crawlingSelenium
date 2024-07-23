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
