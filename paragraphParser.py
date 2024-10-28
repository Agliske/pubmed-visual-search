# Import the necessary libraries
from bs4 import BeautifulSoup
from bs4 import Comment
import requests
import lxml
import selenium
import time

import selenium.webdriver
import selenium.webdriver.firefox
import selenium.webdriver.firefox.options

# Fetch the HTML content from a webpage
# url = 'https://www.nationalacademies.org/news/2024/10/workshop-explores-the-opportunity-and-perils-of-using-ai-in-medical-diagnosis'

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def articleParse(url, method = 0):
    if method == 0:
        response = requests.get(url)
        html_content = response.text
        print("using request lib")
        soup = BeautifulSoup(html_content, 'lxml')
        paragraphs = soup.find_all(['p','strong'])

    if method == 1:
        print("using selenium lib")
        options = selenium.webdriver.FirefoxOptions()
        options.add_argument("--headless")
        driver = selenium.webdriver.Firefox(options=options)
        driver.get(url)

        time.sleep(10)

        html_content = driver.page_source

        soup = BeautifulSoup(html_content, 'lxml')
        paragraphs = soup.find_all(string=True)


    # print("we got past pagegen")

    articleData = {
        "url": url,
        "title": None,
        "date": None,
        "content": ""
    }

    # Parse the HTML content with Beautiful Soup
      # You can also use 'html.parser'

    # mainTag = soup.find(["main"])
    

    # titleTag = mainTag.find(["h1"])
    # title = titleTag.get_text()
    # articleData["title"] = title
    
    
    # timeTag = soup.find(['time'])
    # time = timeTag["datetime"]
    # articleData["date"] = time
    
    # 
    
    paragraphs = filter(tag_visible, paragraphs)
    
    
    content = ""
    # Extract and the text from each <p> tag, and add it to content
    for p in paragraphs:
        text = p.get_text()
        
        if len(text) >= 100:
            content = content + text
            if method == 0: print('we assigned content var with')
        
        # print(text)

    articleData["content"] = content

    if articleData['content'] == "":
        articleData = articleParse(url, method = 1 )
        if articleData["content"] == "":
            print("Failure to parse article at URL:  ", articleData["url"])
            return 


    return articleData


# article = articleParse(url)
# print(article["content"])



