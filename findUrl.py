from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
import time
import urllib.parse

def get_all_links(driver, url):
    driver.get(url)
    time.sleep(3)  # 페이지 로딩 대기

    links = set()
    elements = driver.find_elements(By.TAG_NAME, 'a')
    for elem in elements:
        link = elem.get_attribute('href')
        if link:
            # 절대 URL로 변환
            link = urllib.parse.urljoin(url, link)
            links.add(link)
    return links

def crawl_links(start_url):
    # Chrome 웹드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
    service = ChromeService(executable_path="D:\\study\\python\\work\\chromedriver.exe")
    
    driver = webdriver.Chrome(service=service, options=options)
    all_links = set()
    
    # 초기 URL의 모든 링크 가져오기
    links_to_visit = get_all_links(driver, start_url)
    all_links.update(links_to_visit)
    
    # 방문할 링크 목록
    visited_links = set()
    
    while links_to_visit:
        current_link = links_to_visit.pop()
        if current_link not in visited_links:
            visited_links.add(current_link)
            try:
                new_links = get_all_links(driver, current_link)
                all_links.update(new_links)
                links_to_visit.update(new_links - visited_links)
            except Exception as e:
                print(f"Error visiting {current_link}: {e}")
    
    driver.quit()
    return all_links

def save_links_to_file(links, file_name):
    with open(file_name, 'w') as file:
        for link in links:
            file.write(link + '\n')

def main():
    url = input("Enter the main homepage URL: ")
    links = crawl_links(url)
    save_links_to_file(links, 'output_links.txt')
    print(f"Found {len(links)} links. Saved to 'output_links.txt'.")

if __name__ == "__main__":
    main()
