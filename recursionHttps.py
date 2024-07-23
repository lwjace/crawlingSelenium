import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

def get_links(url, base_url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if not href.startswith('javascript:'):
            full_url = urljoin(base_url, href)
            # unquote를 사용하여 URL을 디코딩합니다.
            full_url = unquote(full_url)
            links.add(full_url)
    return links

def crawl(start_url, max_depth=5):
    visited = set()
    to_visit = {start_url}
    base_url = "{0.scheme}://{0.netloc}".format(urlparse(start_url))
    for depth in range(max_depth):
        new_links = set()
        for url in to_visit:
            if url not in visited:
                visited.add(url)
                try:
                    links = get_links(url, base_url)
                    new_links.update(links - visited)
                except requests.exceptions.RequestException as e:
                    print(f"Failed to request {url}: {e}")
        to_visit = new_links
    return visited

def save_links_to_file(links, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')

start_url = 'https://www.lguplus.com/'
all_links = crawl(start_url)
save_links_to_file(all_links, 'crawled_links.txt')
print(f"All links have been saved to 'crawled_links.txt'")