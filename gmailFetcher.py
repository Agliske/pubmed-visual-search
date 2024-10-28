import os.path
import base64
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
import lxml
from bs4 import BeautifulSoup
import url64

import numpy as np
from html import unescape




scopes = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():

    if os.path.exists(r'C:\Users\aglis\Documents\Python_Projects\DaveArticleScraper\auth\token.json'):
        credentials = Credentials.from_authorized_user_file(r'C:\Users\aglis\Documents\Python_Projects\DaveArticleScraper\auth\token.json', scopes)
    
    
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            r'C:\Users\aglis\Documents\Python_Projects\DaveArticleScraper\auth\client_secrets.json',
            scopes=scopes)

        credentials = flow.run_local_server(port=0)


    with open(r'C:\Users\aglis\Documents\Python_Projects\DaveArticleScraper\auth\token.json', 'w') as token:
            token.write(credentials.to_json())

    service = build('gmail', 'v1', credentials=credentials)

    print('we got to the service')

    return service

def extractUrl(html_content):
    


    soup = BeautifulSoup(html_content, "lxml")

    links = [a['href'] for a in soup.find_all('a', href=True)]

    # print(links)
    filtered_links = [link for link in links if "https://www.google.com/url?rct=j&" in link]
    for link in filtered_links: unescape(link)
    
    return filtered_links

def fetchNewsAlerts(service):
    """Searches for an email with the subject 'Google Alert' and returns the raw HTML content."""
    # Define the search query to find emails with the subject 'Google Alert'
    query = 'subject:Google Alert'

    # List emails matching the query
    results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
    messages = results.get('messages', [])
     
    

    if not messages:
        print('No messages found.')
        return None
    
    return messages

def extract_html(gmail_message,service):

    # Get the first message that matches the query
    msg_id = gmail_message['id']
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

    mhtml = ''

    # The raw message is Base64 encoded, so we need to decode it
    for p in message["payload"]["parts"]:
            if p["mimeType"] in ["text/html"]:
                
                data = url64.decode(p["body"]["data"])
                mhtml = mhtml + data
                # print(mhtml)
    
    return mhtml



# service = authenticate()
# messages = fetchNewsAlerts(service)
# html = extract_html(messages[0])
# # print(html)
# links = extractUrl(html)
# print(np.array(links))
# output_html_path = r"C:\Users\aglis\Documents\Python_Projects\DaveArticleScraper\examples"
# with open(output_html_path, 'w', encoding='utf-8') as html_file:
#                 html_file.write(html)


