import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import csv

colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

first_level_links = set()
second_level_links = set()
third_level_links = set()

patterns = {
    'first_level': re.compile(r'^(https:\/\/worldcam\.eu\/webcams\/)[a-z-\-?]$'),
    'second_level': re.compile(r'^(https:\/\/worldcam\.eu\/webcams\/)[a-z-\-?]+\/[a-z-\-?]+$'),
    'third_level': re.compile(r'^(https:\/\/worldcam\.eu\/webcams\/)[a-z-\-?]+\/[a-z-\-?]+\/[0-9-a-z\-?]$')
}

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url, pattern_level, links_level):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    # domain name of the URL without the protocol
    # domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue

        href = urljoin(url, href)

        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if not is_valid(href):
            continue    

        # if href in internal_urls:
        #     continue

        if re.match(patterns[pattern_level], href):
            print(f"{GREEN}[*] Internal link: {href}{RESET}")
            links_level.add(href)

    if f'{links_level=}'.split('=')[0] == 'first_level_links':
        links_level.add([link for link in list(links_level) if 'category' not in link])

    elif f'{links_level=}'.split('=')[0] == 'third_level_links':
        add_to_csv(list(links_level))
    # urls = '\n'.join(list(links_level))

total_urls_visited = 0
urls_max_depth = 2
continents_max_depth = 1
countries_max_depth = 3
all_links = []
datalist = []

def add_to_csv(links):
    for url in links:
        data = {}
        if url.startswith('https://worldcam.eu/webcams/'):
            sub_folder = url.lstrip('https://worldcam.eu/webcams/')
            split_url = sub_folder.split('/')

            if not any(d['url'] == url for d in datalist) and split_url[2:]:
                data['continent'] = split_url[0]
                data['country'] = split_url[1]

                # if len(split_url) > 2:
                if not split_url[1:]:
                    loc_name_and_ref = split_url[2]
                    data['name'] = loc_name_and_ref
                    data['ref'] = loc_name_and_ref
                else:
                    loc_name_and_ref = split_url[2].split('-')
                    data['name'] = ' '.join(loc_name_and_ref[1:])
                    data['ref'] = loc_name_and_ref[0]

                # else:
                #     data['name'] = ''
                #     data['ref'] = ''
                    
                data['url'] = url
                datalist.append(data)

def crawl_level1(url, urls_max_depth=urls_max_depth):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        urls_max_depth (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    get_all_website_links(url, 'first_level', first_level_links)

def crawl_level2(urls, urls_max_depth=continents_max_depth):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        urls_max_depth (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    
    print(f"{YELLOW}[*] Crawling: {urls}{RESET}")
    for url in list(urls)[:urls_max_depth]:
        get_all_website_links(url, 'second_level', second_level_links)

def crawl_level3(urls, urls_max_depth=countries_max_depth):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        urls_max_depth (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    for url in list(urls)[:urls_max_depth]:
        print(f"{YELLOW}[*] Crawling: {url}{RESET}")
        get_all_website_links(urls, 'third_level', third_level_links)

try:
    if __name__ == "__main__":
        crawl_level1("https://worldcam.eu/")
        crawl_level2(first_level_links)
        crawl_level3(second_level_links)
        print("[+] First Level Internal links:", len(first_level_links))
        print("[+] Second Level links:", len(second_level_links))
        print("[+] Third Level links:", len(third_level_links))
        print("[+] Total URLs:", len(first_level_links) + len(second_level_links) + len(third_level_links))
        print("[+] Total crawled URLs:", urls_max_depth)

except Exception:
    keys = datalist[0].keys()

    with open('./worldcam_eu2.csv', 'w', encoding='utf_8_sig', newline='') as f:
        dict_writer = csv.DictWriter(f, keys, dialect='excel', delimiter=';')
        dict_writer.writeheader()
        dict_writer.writerows(datalist)

finally:
    keys = datalist[0].keys()

    with open('./worldcam_eu2.csv', 'w', encoding='utf_8_sig', newline='') as f:
        dict_writer = csv.DictWriter(f, keys, dialect='excel', delimiter=';')
        dict_writer.writeheader()
        dict_writer.writerows(datalist)
