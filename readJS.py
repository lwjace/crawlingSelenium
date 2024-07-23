import requests
from bs4 import BeautifulSoup
import jsbeautifier

# JavaScript beautify options
opts = jsbeautifier.default_options()
opts.indent_size = 4

def get_javascript_code(url):
    # 웹페이지 가져오기
    response = requests.get(url)
    
    # 페이지 파싱하기
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 모든 script 태그 찾기
    scripts = soup.find_all('script')
    
    js_code = ""
    for script in scripts:
        if script.string:
            # 각 script 태그의 내용을 추출하여 js_code에 추가
            js_code += script.string + "\n"
    
    # Unicode 이스케이프 시퀀스 변환
    js_code = js_code.replace("\\u002F", "/")
    
    # JavaScript 코드 정렬
    beautified_js = jsbeautifier.beautify(js_code, opts)
    
    return beautified_js


def save_javascript_to_file(js_code, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(js_code)

# 예제 URL (원하는 웹사이트로 변경)
url = "https://www.lguplus.com/login/uplus-register/personal"
js_code = get_javascript_code(url)


# JavaScript 코드 출력
#print(js_code)

# JavaScript 코드를 파일로 저장
file_name = "lgu+on.js"
save_javascript_to_file(js_code, file_name)

print(f"JavaScript code has been saved to {file_name}")
