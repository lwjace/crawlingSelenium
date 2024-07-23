import requests
from bs4 import BeautifulSoup
import json

def save_html(url, file_name):
    try:
        # 웹 페이지 요청
        response = requests.get(url)
        response.raise_for_status()  # 요청이 성공했는지 확인

        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')

        # HTML을 파일로 저장
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(soup.prettify())

        print(f"HTML content saved to {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")

def parse_html_and_save_to_json(html_file, json_file):
    try:
        # 저장된 HTML 파일을 읽기
        with open(html_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # data-gtm-click-text와 data-gtm-click-url 속성을 가진 요소 찾기
        elements = soup.find_all(attrs={"data-gtm-click-text": True, "data-gtm-click-url": True})
        
        # 결과를 저장할 딕셔너리
        data = {}
        
        for element in elements:
            click_text = element.get("data-gtm-click-text")
            click_url = element.get("data-gtm-click-url")
            if click_text and click_url:
                data[click_text] = click_url
        
        # 딕셔너리를 JSON 파일로 저장
        with open(json_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        
        print(f"Data saved to {json_file}")
    except Exception as e:
        print(f"Error parsing the HTML file: {e}")

# 사용 예시
url = "https://www.lguplus.com/login"
html_file = "example1.html"
json_file = "result1.json"

save_html(url, html_file)
parse_html_and_save_to_json(html_file, json_file)
