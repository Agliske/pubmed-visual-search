from bs4 import BeautifulSoup
import lxml
import requests
import time
import re

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
