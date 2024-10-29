import gmailFetcher
import paragraphParser
import numpy as np
scopes = ['https://www.googleapis.com/auth/gmail.readonly']

service = gmailFetcher.authenticate()
messages = gmailFetcher.fetchNewsAlerts(service)
# print(len(messages))
html = gmailFetcher.extract_html(messages[0],service)
links = gmailFetcher.extractUrl(html)
# print(np.array(links))
# print(links)


articleData = []
iterator = 0
for link in links:
    artDataDict = paragraphParser.articleParse(link)
    articleData.append(artDataDict)
    iterator+=1
    print("articles Processed = ", iterator)
    print("appended article length = ", len(artDataDict["content"]))

print(articleData[0]["content"])
