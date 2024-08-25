from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from time import sleep

# Path to the file containing zpids
zpids_file_path = 'zpids.txt'

# Path to save the Excel file
excel_file_path = 'price_history.csv'

# Path to save the failed_zpid_list file
failed_zpid_file_path = 'failed_zpids.txt'

no_button_file_path = 'no_button.txt'

# Base url for update
base_url = 'https://www.zillow.com/homedetails/743-Pinetree-Rd-Pittsburgh-PA-15243/{}_zpid/'

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options=options)

# timeout value(in seconds), small value MAY decrease success rate,
# while big value WILL lead to longer time
timeout_value = 20

no_button_list = []

def scrape_zpid(zpid):
    # Construct the URL with the zpid correctly placed
    url = base_url.format(zpid)
    print(f"----- Accessing {url} -----")

    # Load the page
    driver.get(url)

    # click the 'Show more' button
    try:
        Price_history_text = WebDriverWait(driver, timeout_value).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Price history')]"))
        )
        # From the 'Price History' text, find the nearest 'Show more' button
        Show_more_button = Price_history_text.find_element(By.XPATH, "following::button[contains(., 'Show more')][1]")
        Show_more_button.click()
        print("----- SHOW_MORE BUTTON CLICKED. GOOD. -----")
    except:
        no_button_list.append(zpid)
        print("----- NO SHOW_MORE BUTTON FOUND. NEED TO VERIFY. -----")

    # Extract dates, events, and prices using WebDriverWait
    dates = [element.text for element in WebDriverWait(driver, timeout_value).until(
        EC.visibility_of_all_elements_located((By.XPATH, "//span[@data-testid='date-info']"))
    )]

    events = [element.text for element in WebDriverWait(driver, timeout_value).until(
        EC.visibility_of_all_elements_located((By.XPATH, "//span[contains(@class, 'styles__StyledEventText')]"))
    )]

    prices = [element.text for element in WebDriverWait(driver, timeout_value).until(
        EC.visibility_of_all_elements_located((By.XPATH, "//td[@data-testid='price-money-cell']//span[contains(@class, 'styles__StyledPriceText')]"))
    )]

    try:
        walk_score_value = WebDriverWait(driver, timeout_value).until(
            EC.visibility_of_element_located((By.XPATH, "//a[@aria-describedby='walk-score-text']"))
        ).text
    except:
        walk_score_value = "NA"
    
    try:
        transit_score_value = WebDriverWait(driver, timeout_value).until(
            EC.visibility_of_element_located((By.XPATH, "//a[@aria-describedby='transit-score-text']"))
        ).text
    except:
        transit_score_value = "NA"

    try:
        bike_score_value = WebDriverWait(driver, timeout_value).until(
            EC.visibility_of_element_located((By.XPATH, "//a[@aria-describedby='bike-score-text']"))
        ).text
    except:
        bike_score_value = "NA"

    rating_heading = WebDriverWait(driver, timeout_value).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'GreatSchools rating')]"))
    )

    # Use the 'following' axis to find all '/10' elements that appear after the 'GreatSchools rating' heading
    rating_elements = rating_heading.find_elements(By.XPATH, "following::span[contains(text(), '/10')]")

    # List to store the school ratings
    school_ratings = []

    # Extract the rating number just before each '/10'
    for rating_element in rating_elements:
        score = rating_element.find_element(By.XPATH, "preceding-sibling::span[1]").text
        school_ratings.append(score)

    # Check if the list length is less than 3
    if len(school_ratings) < 3:
        while len(school_ratings) < 3:
            school_ratings.append('NULL')

    return_list = []

    # Append data for each date-event-price triplet with scores
    for date, event, price in zip(dates, events, prices):
        price_int = price.replace('$', '').replace(',', '')
        entry = [zpid, date, event, price_int, walk_score_value, transit_score_value, bike_score_value] + school_ratings
        return_list.append(entry)
    
    return return_list

def main():
    # List to store zpids
    zpid_list = []

    # Raw list containing final result
    final_result = []

    # List to store failed_zpid
    failed_zpid_list = []

    # record the success number
    success_num = 0

    # record the success number
    fail_num = 0

    # Open the zpids file
    with open(zpids_file_path, 'r') as file:
        for line in file:
            zpids = line.strip().split()
            zpid_list.extend(zpids)
    
    # Start the timer
    start_time = time.time()

    # final_result += scrape_zpid("11290629")
    # print("\n--------------------------------------------------")
    # print("zpid="  + " SUCCEEDED")
    # print("TOTAL ATTEMPT: %d" % (success_num + fail_num))
    # print("TOTAL SUCCESS: %d" % success_num)
    # print("TOTAL FAILURE: %d" % fail_num)
    # print("TIME USED: %ds" % (time.time() - start_time))
    # print("--------------------------------------------------\n")

    for zpid in zpid_list:
        print("\n------------------------------------------------------------------------------------------------------------------------------------------------------")
        try:
            final_result += scrape_zpid(zpid)
            success_num += 1
            print("zpid=" + zpid + " SUCCEEDED")
            print("TOTAL ATTEMPT: %d" % (success_num + fail_num))
            print("TOTAL SUCCESS: %d" % success_num)
            print("TOTAL FAILURE: %d" % fail_num)
            print("TOTAL TIME: %ds" % (time.time() - start_time))
        except:
            failed_zpid_list.append(zpid)
            fail_num += 1
            print("zpid=" + zpid + " FAILED")
            print("TOTAL ATTEMPT: %d" % (success_num + fail_num))
            print("TOTAL SUCCESS: %d" % success_num)
            print("TOTAL FAILURE: %d" % fail_num)
            print("TOTAL TIME: %ds" % (time.time() - start_time))
        
        if (success_num + fail_num) % 5 == 0:
            # Create DataFrame
            df = pd.DataFrame(final_result, columns=['zpid', 'Time', 'Event', 'Price', 'Walk', 'Transit', 'Bike', 'EI', 'Middle', 'SeniorHigh'])

            # Write the DataFrame to an Excel file
            df.to_csv(excel_file_path, index=False)

            # Writing failed zpid list to a text file, 10 zpids per line
            with open(failed_zpid_file_path, 'w') as file:
                for i in range(0, len(failed_zpid_list), 10):
                    line = ' '.join(failed_zpid_list[i:i+10])
                    file.write(line + '\n')

            # print(f'Failed zpid list saved to {failed_zpid_file_path}')
            with open(no_button_file_path, 'w') as file:
                for i in range(0, len(no_button_list), 10):
                    line = ' '.join(no_button_list[i:i+10])
                    file.write(line + '\n')
            
            print("DATA SAVED")
                
        print("------------------------------------------------------------------------------------------------------------------------------------------------------\n")


    driver.quit()

    # Create DataFrame
    df = pd.DataFrame(final_result, columns=['zpid', 'Time', 'Event', 'Price', 'Walk', 'Transit', 'Bike', 'EI', 'Middle', 'SeniorHigh'])

    # Write the DataFrame to an Excel file
    df.to_csv(excel_file_path, index=False)

    print(f'Excel file saved to {excel_file_path}')

    # Writing failed zpid list to a text file, 10 zpids per line
    with open(failed_zpid_file_path, 'w') as file:
        for i in range(0, len(failed_zpid_list), 10):
            line = ' '.join(failed_zpid_list[i:i+10])
            file.write(line + '\n')

    # print(f'Failed zpid list saved to {failed_zpid_file_path}')
    with open(no_button_file_path, 'w') as file:
        for i in range(0, len(no_button_list), 10):
            line = ' '.join(no_button_list[i:i+10])
            file.write(line + '\n')
    
    print("ALL DATA SAVED")

main()