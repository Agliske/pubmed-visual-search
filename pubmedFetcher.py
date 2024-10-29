from bs4 import BeautifulSoup
import lxml
import requests
import time

import selenium
import selenium.webdriver
import selenium.webdriver.firefox
import selenium.webdriver.firefox.options


url = r"https://pubmed.ncbi.nlm.nih.gov/?term=whale+antibodies"


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

        response = requests.get(url)
        html_content = response.text

    else: #use selenium lib and press "show more results" button until all results are shown

        options = selenium.webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = selenium.webdriver.Firefox(options=options)
        driver.get(url)

        time.sleep(3)

        html_content = driver.page_source

    soup = BeautifulSoup(html_content,'lxml')
    search_result_tags = soup.find_all('a', class_ = 'docsum-title')
    
   
    links = []
    

    for result in search_result_tags:
        href_val = result['href']
        result_url = "https://pubmed.ncbi.nlm.nih.gov" + href_val
        links.append(result_url)
    

    
    ######################################################################################################################
    #now we go to each link and extract the content (abstract), article title, publication date, and fill in url.
    ######################################################################################################################

    resultData = {
            "url": None,
            "title": None,
            "date": None,
            "content": ""
    }

    articleData = []
    for url in links:
        resultResponse = requests.get(url)
        result_html = resultResponse.text

        resultData["url"] = url

        try:
            abstract_raw = soup.find('div', {'class': 'abstract-content selected'}).find_all('p')
            # Some articles are in a split background/objectives/method/results style, we need to join these paragraphs
            abstract = ' '.join([paragraph.text.strip() for paragraph in abstract_raw])
        except:
            abstract = 'NO_ABSTRACT'

        



links = pubmedResults(url)
print(links)
