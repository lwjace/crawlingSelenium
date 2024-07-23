import requests
from bs4 import BeautifulSoup

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

# 사용 예시
url = "https://www.lguplus.com/benefit-event/ongoing/387"
file_name = "example3.html"
save_html(url, file_name)
