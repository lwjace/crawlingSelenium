from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urlparse, unquote

visited_urls = set()

def is_valid_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ["http", "https"]

def decode_url(url):
    return unquote(url)

def crawl_with_selenium(url, depth, driver, file):
    if depth == 0 or url in visited_urls:
        return
    visited_urls.add(url)
    
    driver.get(url)
    time.sleep(4)  # 페이지 로드 대기
    
    links = driver.find_elements(By.TAG_NAME, 'a')
    hrefs = [link.get_attribute('href') for link in links]
    
    for href in hrefs:
        if href:
            href = decode_url(href)
            if is_valid_url(href) and href not in visited_urls:
                file.write(href + '\n')  # 수집한 URL을 파일에 기록
                print(href)  # 수집한 URL 출력
                visited_urls.add(href)  # URL을 방문한 URL 집합에 추가
                crawl_with_selenium(href, depth-1, driver, file)

# Selenium 웹 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 시작 URL과 크롤링 깊이 설정
start_url = 'https://www.lguplus.com/'
crawl_depth = 4

with open('collected_urls.txt', 'w') as file:
    crawl_with_selenium(start_url, crawl_depth, driver, file)

driver.quit()
