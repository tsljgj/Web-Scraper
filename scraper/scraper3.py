# pip install requests
# pip install beautifulsoup4
# pip install requests_html (pip3 if default pip location is python 2)
# pip install capsolver
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import capsolver

# fill in these information--------------
PAGE_URL = 'https://www.zillow.com/homedetails/743-Pinetree-Rd-Pittsburgh-PA-15243/11256984_zpid/'
PAGE_KEY = '6LfW6wATAAAAAHLqO2pb8bDBahxlMxNdo9g947u9'
capsolver.api_key = "CAP-3A102E19D65C7301513F430535C0DA7E"
# ---------------------------------------

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}

def solve_recaptcha_v2(url, key):
    solution = capsolver.solve({
        "type": "ReCaptchaV2TaskProxyless",
        "websiteURL": url,
        "websiteKey": key,
    })
    return solution

# solution = solve_recaptcha_v2(PAGE_URL, PAGE_KEY)

proxy = "http://487827493a465e94fdaa1e6dbc25c40c7732292f:js_render=true&json_response=true&premium_proxy=true&proxy_country=us@proxy.zenrows.com:8001"
proxies = {"http": proxy, "https": proxy}

session = HTMLSession() # requests_html

r = session.get(PAGE_URL, proxies=proxies, verify=False) # requests.get(...) for requests
wait = r.html.render(timeout=30)
# r.html.render() # requests_html

soup = BeautifulSoup(r.html.html, 'html.parser') # r.html for requests

print(soup)