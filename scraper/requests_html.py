import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}

url = 'google.com'

session = HTMLSession() # only for requests_html

r = session.get(url, headers=headers) # requests.get(...)

r.html.render() # js changes html

soup = BeautifulSoup(r.html.html, 'html.parser') # response.html if using requests

print(soup)

# Now, locate html elements to scrape!