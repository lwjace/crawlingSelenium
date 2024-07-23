from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urlparse, unquote, urljoin
import re

visited_urls = set()

def is_valid_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ["http", "https"]

def decode_url(url):
    return unquote(url)

def extract_url_from_onclick(onclick_value):
    url_match = re.search(r"location\.href=['\"](.*?)['\"]", onclick_value)
    if url_match:
        return url_match.group(1)
    return None

def extract_menu_link_urls(driver, base_url):
    script_content = driver.page_source
    urls = re.findall(r'\bmenuLinkUrl\s*=\s*[\'"](/[^\'"]+)[\'"]', script_content)
    for url in urls:
        print("Extracted menuLinkUrl:", url)
    return [urljoin(base_url, url) for url in urls]

def crawl_with_selenium(url, depth, driver, file):
    if depth == 0 or url in visited_urls:
        return
    visited_urls.add(url)
    
    driver.get(url)
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # 페이지 로드 대기
    
    elements = driver.find_elements(By.XPATH, "//a[@href] | //button[@onclick] | //*[@onclick]")
    hrefs = []
    for element in elements:
        if element.tag_name == 'a':
            href = element.get_attribute('href')
        else:
            onclick_value = element.get_attribute('onclick')
            href = extract_url_from_onclick(onclick_value)
        
        if href:
            hrefs.append(href)

    # Extract menuLinkUrls from page source and combine with base URL
    menu_link_urls = extract_menu_link_urls(driver, url)
    hrefs.extend(menu_link_urls)

    for href in hrefs:
        href = decode_url(href)
        if is_valid_url(href) and href not in visited_urls:
            file.write(href + '\n')  # 수집한 URL을 파일에 기록
            print(href)  # 수집한 URL 출력
            visited_urls.add(href)  # URL을 방문한 URL 집합에 추가
            crawl_with_selenium(href, depth-1, driver, file)  # 재귀 호출로 깊이를 줄여서 다음 URL을 방문

# Selenium 웹 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 시작 URL과 크롤링 깊이 설정
start_url = 'https://www.lguplus.com/login'
crawl_depth = 5

with open('ab_collected_urls.txt', 'w') as file:
    crawl_with_selenium(start_url, crawl_depth, driver, file)

driver.quit()
