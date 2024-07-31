from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import re
import os

# 무시할 파일 확장자 목록
ignored_extensions = ('.png', '.jpg', '.jpeg', '.css', '.gif', '.svg', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.js', '.pdf', '.woff2')

def get_all_urls(base_url, driver_path, visited_urls):
    # Selenium WebDriver 초기화
    chrome_options = Options()
    chrome_options.page_load_strategy = 'normal'  # Page load strategy
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = ChromeService(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)  # 페이지 로딩 타임아웃을 30초로 설정
    
    def extract_urls():
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
        except TimeoutException:
            print(f"Timeout while extracting page source from {driver.current_url}")
            error_urls.add(driver.current_url)
            return set()
        except WebDriverException as e:
            print(f"WebDriverException while extracting page source from {driver.current_url}: {e}")
            error_urls.add(driver.current_url)
            return set()

        page_urls = set()
        
        # a 태그에서 URL 추출
        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])
            if re.match(r'^https?://', full_url) and base_url in full_url and not full_url.endswith(ignored_extensions):
                page_urls.add(full_url)

        # 특정 속성에서 URL 추출 (예: data-gtm-click-url, src, data-src 등)
        for tag in soup.find_all(attrs={"data-gtm-click-url": True}):
            full_url = urljoin(base_url, tag['data-gtm-click-url'])
            if re.match(r'^https?://', full_url) and base_url in full_url and not full_url.endswith(ignored_extensions):
                page_urls.add(full_url)
        
        # img 태그의 src 속성에서 URL 추출
        for img in soup.find_all('img', src=True):
            full_url = urljoin(base_url, img['src'])
            if re.match(r'^https?://', full_url) and base_url in full_url and not full_url.endswith(ignored_extensions):
                page_urls.add(full_url)

        # iframe 태그의 src 속성에서 URL 추출
        for iframe in soup.find_all('iframe', src=True):
            full_url = urljoin(base_url, iframe['src'])
            if re.match(r'^https?://', full_url) and base_url in full_url and not full_url.endswith(ignored_extensions):
                page_urls.add(full_url)

        # script 태그의 src 속성에서 URL 추출
        for script in soup.find_all('script', src=True):
            full_url = urljoin(base_url, script['src'])
            if re.match(r'^https?://', full_url) and base_url in full_url and not full_url.endswith(ignored_extensions):
                page_urls.add(full_url)

        # link 태그의 href 속성에서 URL 추출 (예: 스타일시트 링크)
        for link in soup.find_all('link', href=True):
            full_url = urljoin(base_url, link['href'])
            if re.match(r'^https?://', full_url) and base_url in full_url and not full_url.endswith(ignored_extensions):
                page_urls.add(full_url)
        
        return page_urls

    def process_url(url):
        if url in visited_urls or url.endswith(ignored_extensions):
            return set()
        visited_urls.add(url)
        
        try:
            driver.get(url)
            time.sleep(3)  # 페이지 로딩 대기
        except TimeoutException:
            print(f"Timeout loading {url}")
            error_urls.add(url)
            return set()
        except WebDriverException as e:
            print(f"WebDriverException loading {url}: {e}")
            error_urls.add(url)
            return set()
        
        return extract_urls()

    # 초기 페이지에서 URL 추출
    all_urls = process_url(base_url)
    new_urls = all_urls.copy()

    # 사용자 상호작용을 통해 URL 수집 및 반복적으로 모든 URL을 탐색
    while new_urls:
        current_url = new_urls.pop()
        found_urls = process_url(current_url)
        new_urls.update(found_urls - visited_urls)
        all_urls.update(found_urls)

    driver.quit()
    return all_urls

def save_urls_to_file(urls, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(url + '\n')

base_url = "https://www.lguplus.com/"  # 크롤링할 사이트의 URL을 입력하세요
driver_path = os.path.join(os.getcwd(), "chromedriver.exe")  # 현재 디렉토리의 ChromeDriver 경로 (Windows의 경우 .exe)

# 경로가 올바른지 확인
if not os.path.isfile(driver_path):
    raise FileNotFoundError(f"Chromedriver not found at {driver_path}")

visited_urls = set()
error_urls = set()
all_urls = get_all_urls(base_url, driver_path, visited_urls)

# 결과를 파일에 저장
output_file = os.path.join(os.getcwd(), "found_urls.txt")
error_file = os.path.join(os.getcwd(), "error_urls.txt")

save_urls_to_file(all_urls, output_file)
save_urls_to_file(error_urls, error_file)

print(f"Found URLs have been saved to {output_file}")
print(f"Error URLs have been saved to {error_file}")
