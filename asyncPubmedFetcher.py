from bs4 import BeautifulSoup
import lxml
import requests
import time
import re
import asyncio
import aiohttp
from aiohttp import ClientSession
import random

import selenium
import selenium.webdriver
import selenium.webdriver.firefox
import selenium.webdriver.firefox.options

semaphore = asyncio.BoundedSemaphore(50)

url = r"https://pubmed.ncbi.nlm.nih.gov/?term=whale+antibodies"

user_agents = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]

def make_header():
    '''
    Chooses a random agent from user_agents with which to construct headers
    :return headers: dict: HTTP headers to use to get HTML from article URL
    '''
    # Make a header for the ClientSession to use with one of our agents chosen at random
    headers = {
            'User-Agent':random.choice(user_agents),
            }
    return headers

async def fetch_html(session, url):
    """Fetches the HTML content of a URL asynchronously."""
    async with semaphore:
        async with session.get(url) as response:
            
            return await response.text()

async def parse_article_data(session, url):
    """Fetches and parses article data for a single URL."""
    resultData = {
        "url": url,
        "title": None,
        "date": None,
        "content": ""
    }

    try:
        
        result_html = await fetch_html(session, url)
        result_soup = BeautifulSoup(result_html,"lxml")

        #filling in URL
        resultData["url"] = url
        
        #finding and adding abstract to "content" dict field
        # try:
        # abstract_element = result_soup.find("div", class_ = "abstract-content selected")
        abstract_raw = result_soup.find_all('p')
        paragraphs = []
        for p in abstract_raw:
            paragraphs.append(p.text.strip())
        
        
        
        abstract = ''.join(paragraphs)
        print(abstract)
        resultData["content"] = abstract
        
        # except:
        #     abstract = 'No abstract'
        #     resultData["content"] = abstract
            
        #finding and adding article title to "title" field
        try:

            title_element = result_soup.find('h1', class_ = "heading-title")
            title = title_element.text.strip()
            resultData["title"] = title


        except:
            resultData["title"] = "title not found"
        
        #adding pub date, extracted from the citation using re library
        try:
            cit = result_soup.find('span', class_ = "cit")
            cit_text = cit.text
            year = re.search(r"(\d{4})", cit_text) #search for a group of 4 numbers (looks like a year)
            year = year.group()
            month = re.search(r"([A-Za-z]{3})",cit_text) #search for a group of 3 letters that look like month abbreviations (Jan, Feb, Mar)
            month = month.group()
            resultData["date"] = month + ", " + year
           
        except:
            resultData["date"] = "Date not found"

        print("Article Parsed at url: ", url)
    except Exception as e:
        print(f"Error fetching data for URL {url}: {e}")

    
    return resultData

async def fetch_all_article_data(links):
    
    articleData = []
    headers = make_header()
    async with ClientSession(headers = headers) as session:
        tasks = []
        for url in links:
            task = parse_article_data(session,url)
            tasks.append(task)
        
        articleData = await asyncio.gather(*tasks)
        
    return articleData

def pubmedResultsAsync(search_url,num_results_requested = 200):
    """
    pubmedResults retrieves url links from Pubmed (https://pubmed.ncbi.nlm.nih.gov/) search results

    Args:
        search_url (str): url of the search results
        num_results_requested (int, optional): how many results links user wants returned. Defaults to 200.

    Returns:
        articleData (list of dict): list of dict containing all information relevant to the search result

        {"title": (str) research paper title
        "url": url of entry
        "date:" date of publication
        "content": abstract extracted from pubmed}
    """
    ######################################################################################################################
    #first we get the links
    ######################################################################################################################

    if num_results_requested <= 200: # use requests lib
        
        response = requests.get(search_url)
        html_content = response.text

    else: #use selenium lib and press "show more results" button until all results are shown (not done yet)

        options = selenium.webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = selenium.webdriver.Firefox(options=options)
        driver.get(search_url)

        time.sleep(3)

        html_content = driver.page_source

    soup = BeautifulSoup(html_content,'lxml')
    search_result_tags = soup.find_all('a', class_ = 'docsum-title')
    
    #building list of each link in the html of the search query
    links = []
    iterator = 0
    for result in search_result_tags:
        
        iterator += 1
        if iterator > num_results_requested:
            break

        href_val = result['href']
        result_url = "https://pubmed.ncbi.nlm.nih.gov" + href_val
        links.append(result_url)
        
    try:
        
        articleData = asyncio.run(fetch_all_article_data(links))
        
    except RuntimeError:
        loop = asyncio.get_event_loop()
        articleData = loop.run_until_complete(fetch_all_article_data(links))
    return articleData
    
def pubmedResults(search_url,num_results_requested = 200):
    """
    pubmedResults retrieves url links from Pubmed (https://pubmed.ncbi.nlm.nih.gov/) search results

    Args:
        search_url (str): url of the search results
        num_results_requested (int, optional): how many results links user wants returned. Defaults to 200.

    Returns:
        articleData (list of dict): list of dict containing all information relevant to the search result

        {"title": (str) research paper title
        "url": url of entry
        "date:" date of publication
        "content": abstract extracted from pubmed}
    """
    ######################################################################################################################
    #first we get the links
    ######################################################################################################################

    if num_results_requested <= 200: # use requests lib
        
        response = requests.get(search_url)
        html_content = response.text

    else: #use selenium lib and press "show more results" button until all results are shown (not done yet)

        options = selenium.webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = selenium.webdriver.Firefox(options=options)
        driver.get(search_url)

        time.sleep(3)

        html_content = driver.page_source

    soup = BeautifulSoup(html_content,'lxml')
    search_result_tags = soup.find_all('a', class_ = 'docsum-title')
    
    #building list of each link in the html of the search query
    links = []
    iterator = 0
    for result in search_result_tags:
        
        iterator += 1
        if iterator > num_results_requested:
            break

        href_val = result['href']
        result_url = "https://pubmed.ncbi.nlm.nih.gov" + href_val
        links.append(result_url)
        
    
    ######################################################################################################################
    #now we go to each link and extract the content (abstract), article title, publication date, and fill in url.
    ######################################################################################################################


    articleData = []
    iterator = 0
    for url in links:

        resultData = {
            "url": None,
            "title": None,
            "date": None,
            "content": ""
    }
        #parsing with BeautifulSoup
        resultResponse = requests.get(url)
        result_html = resultResponse.text
        result_soup = BeautifulSoup(result_html,'lxml')

        #filling in URL
        resultData["url"] = url
        
        #finding and adding abstract to "content" dict field
        try:
            abstract_element = result_soup.find("div", class_ = "abstract-content selected")
            abstract_raw = abstract_element.find_all('p')
            paragraphs = []
            for p in abstract_raw:
                paragraphs.append(p.text.strip())
            
            abstract = ''.join(paragraphs)
            resultData["content"] = abstract
        except:
            abstract = 'No abstract'
            resultData["content"] = abstract
            
        #finding and adding article title to "title" field
        try:

            title_element = result_soup.find('h1', class_ = "heading-title")
            title = title_element.text.strip()
            resultData["title"] = title


        except:
            resultData["title"] = "title not found"
        
        #adding pub date, extracted from the citation using re library
        try:
            cit = result_soup.find('span', class_ = "cit")
            cit_text = cit.text
            year = re.search(r"(\d{4})", cit_text) #search for a group of 4 numbers (looks like a year)
            year = year.group()
            month = re.search(r"([A-Za-z]{3})",cit_text) #search for a group of 3 letters that look like month abbreviations (Jan, Feb, Mar)
            month = month.group()
            resultData["date"] = month + ", " + year
           

        except:
            resultData["date"] = "Date not found"
            
        articleData.append(resultData)
        iterator = iterator + 1
        print("Articles Processed: ", iterator, "/",len(links))
        
    return articleData

        



# articleData = pubmedResults(url,10)
# print(type(articleData))
# for i in articleData:
#     print(articleData[i]["content"])
