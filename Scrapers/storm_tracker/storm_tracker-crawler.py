import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import csv
import string
from turquoise_logger import Logger

log = Logger().logging()
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

first_level_links = set()
second_level_links = set()
third_level_links = set()

alphabet = string.ascii_uppercase

regions = {
    'Europe': 'europe',
    'South America': 'south-america',
    'North America': 'north-america',
    'Poland': 'poland',
    'Asia': 'asia',
    'United Kingdom': 'united-kingdom',
    'Australia': 'australia-oceania',
    'Africa': 'africa',
    'Poles': 'poles'
    }

patterns = {
    'first_level': re.compile(r'^(https:\/\/worldcam\.eu\/webcams\/)[a-z-\-?]$'),
    'second_level': re.compile(r'^(https:\/\/worldcam\.eu\/webcams\/)[a-z-\-?]+\/[a-z-\-?]+$'),
    'third_level': re.compile(r'^(https:\/\/worldcam\.eu\/webcams\/)[a-z-\-?]+\/[a-z-\-?]+\/[0-9-a-z\-?]+$')
}   #https://worldcam.eu/webcams/europe/austria/32126-eisenerz-erzberg-arena

def plus_one_item_in_list(list):
    try:
        if not list[1:]:
            r = False
        else:
            r = True
    except Exception as e:
        log.debug("Error: %s", e)

    return r

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def move_page(url, status_code):
    '''Moves pages'''
    done_flag = False

    if status_code == 200:
        url_last_part = url.split('/')[-1]
        following_page = int(url_last_part)+25
        following_page = url.replace(url_last_part, str(following_page))

    elif status_code != 200:
        url_last_part = url.split('/')[-1]
        following_page = url.remove(url_last_part) + 0
        letter_index = alphabet.index(url.split('/')[-3])

        if letter_index is not alphabet.index('Z'):
            following_page = re.sub(following_page, r'[A-Z]', alphabet.split()[letter_index + 1])

        elif alphabet.index('Z'):
            done_flag = True
    
    return following_page, done_flag

def get_all_website_links(url, pattern_level='third_level', links_level=third_level_links):
    '''Returns all URLs that is found on `url` in which it belongs to the same website'''
    url = url + '/list/A/4/0'

    while True:
        log.debug(f"{GRAY}[*] Crawling: {url}{RESET}")
        response = requests.get(url)
        sc = response.status_code

        if sc == 200:
            soup = BeautifulSoup(response.content, "html.parser")
        else:
            if url.endswith('/list/A/4/0'):
                raise AssertionError('URL not found')
            elif url.split('/')[-3] == 'Z':
                log.debug(f'Stopped @ {url}')
                break

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href != "" or href is not None:
                href = urljoin(url, href)
                parsed_href = urlparse(href)

                ## Remove URL GET parameters, URL fragments, etc.
                href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

                if is_valid(href):
                    if re.match(patterns[pattern_level], href):
                        log.debug(f"{GREEN}[*] Internal link: {href}{RESET}")
                        links_level.add(href)
                else:
                    continue
            else:
                continue

        url, done_flag = move_page(url, sc)
        
        if done_flag is True:
            log.debug(f'Stopped @ {url}')
            break

    add_to_csv(list(links_level))
    
    
total_urls_visited = 0
urls_max_depth = 2
regions_max_depth = 1
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
                data['region'] = split_url[0]
                data['country'] = split_url[1]

                # if len(split_url) > 2:
                if not plus_one_item_in_list(split_url):
                    loc_name_and_ref = split_url[2]
                    data['zone'] = loc_name_and_ref
                    data['ref'] = loc_name_and_ref
                else:
                    loc_name_and_ref = split_url[2].split('-')
                    data['zone'] = ' '.join(loc_name_and_ref[1:])
                    data['ref'] = loc_name_and_ref[0]

                data['url'] = url
                datalist.append(data)

def add_region_to_urls(url, regions_list):
    '''Append regions to URL'''
    urls = []

    if plus_one_item_in_list(regions_list):
        for region in regions_list:
            urls.append(url + regions[region])
    else:
        urls.append(url + regions[''.join(regions_list)])

    return urls

def crawl(url='https://worldcam.eu/webcams/', regions_list=['Europe'],
                 urls_max_depth=countries_max_depth):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        urls_max_depth (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1

    urls = add_region_to_urls(url, regions_list)

    if plus_one_item_in_list(urls):
        for u in list(urls)[:urls_max_depth]:
            get_all_website_links(urls, 'third_level', third_level_links)

    elif not plus_one_item_in_list(urls):
        u = ''.join(urls)
        get_all_website_links(u, 'third_level', third_level_links)
        
    else:
        log.error(f'urls List is empty: {urls}')


try:
    if __name__ == "__main__":
        crawl()
        log.debug(f"[+] Third Level links: {len(third_level_links)}")
        log.debug(f"[+] Total crawled URLs: {urls_max_depth}")

except Exception:
    keys = datalist[0].keys()

    with open('./worldcam_eu2.csv', 'w', encoding='utf_8_sig', newline='') as f:
        dict_writer = csv.DictWriter(f, keys, dialect='excel', delimiter=';')
        dict_writer.writeheader()
        dict_writer.writerows(datalist)

finally:
    if plus_one_item_in_list(datalist):
        keys = datalist[0].keys()

        with open('./worldcam_eu2.csv', 'w', encoding='utf_8_sig', newline='') as f:
            dict_writer = csv.DictWriter(f, keys, dialect='excel', delimiter=';')
            dict_writer.writeheader()
            dict_writer.writerows(datalist)