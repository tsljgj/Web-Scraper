from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options=options)

# Path to the file containing zpids
zpids_file_path = 'zpids.txt'

# Path to save the Excel file
excel_file_path = 'price_history.csv'

# base url for update
base_url = 'https://www.zillow.com/homedetails/743-Pinetree-Rd-Pittsburgh-PA-15243/{}_zpid/'

# List to store zpids
zpid_list = []

# Open the file and read the contents
with open(zpids_file_path, 'r') as file:
    for line in file:
        zpids = line.strip().split()
        zpid_list.extend(zpids)

# raw list containing final result
final_result = []

def scrape_zpid(zpid):
    # Construct the URL with the zpid correctly placed
    url = base_url.format(zpid)
    print(f"Accessing {url}")

    # Load the page
    driver.get(url)

    # Navigate to the price history section and click "Show more"
    price_history_section = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[h5[@data-testid='price-section-header']]"))
    )

    # Exception handling if "Show more" button is not found
    try:
        show_more_button = price_history_section.find_element(By.XPATH, ".//button[contains(@class, 'StyledTextButton') and contains(@class, 'expando-icon')]")
        show_more_button.click()
    except:
        print("No 'Show more' button found.")

    # dates
    date_elements = driver.find_elements(By.XPATH, "//table[@class='StyledTableComponents__StyledTable-sc-f00yqe-2 kNXiqz']//span[@data-testid='date-info']")
    dates = [element.text for element in date_elements]

    # events
    event_elements = driver.find_elements(By.XPATH, "//table[@class='StyledTableComponents__StyledTable-sc-f00yqe-2 kNXiqz']//span[contains(@class, 'styles__StyledEventText')]")
    events = [element.text for element in event_elements]

    # prices
    price_elements = driver.find_elements(By.XPATH, "//td[@data-testid='price-money-cell']//span[@class='styles__StyledLabelText-sc-reo5z7-1 styles__StyledPriceText-sc-reo5z7-5 gKRjvj icpHlR']")
    prices = [element.text for element in price_elements]

    # walk
    walk_score = driver.find_element(By.XPATH, "//a[@aria-describedby='walk-score-text']")
    walk_score_value = walk_score.text

    # transit
    transit_score = driver.find_element(By.XPATH, "//a[@aria-describedby='transit-score-text']")
    transit_score_value = transit_score.text

    # bike
    bike_score = driver.find_element(By.XPATH, "//a[@aria-describedby='bike-score-text']")
    bike_score_value = bike_score.text

    # Wait for the school ratings to be visible in the DOM
    school_ratings = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.XPATH, "//div[@data-testid='school-rating']/span[contains(@class, 'Text-c11n-8-99-3__sc-aiai24-0 dFhjAe')]"))
    )
    school_rating_values = [rating.text for rating in school_ratings]

    for date, event, price in zip(dates, events, prices):
        price_int = price.replace('$', '').replace(',', '')
        entry = [zpid, date, event, price_int, walk_score_value, transit_score_value, bike_score_value] + school_rating_values
        final_result.append(entry)

for zpid in zpid_list:
    scrape_zpid(zpid)

driver.quit()

# Create DataFrame
df = pd.DataFrame(final_result, columns=['zpid', 'Time', 'Event', 'Price', 'Walk', 'Transit', 'Bike', 'EI', 'Middle', 'SeniorHigh'])

# Write the DataFrame to an Excel file
df.to_csv(excel_file_path, index=False)

print(f'Excel file saved to {excel_file_path}')