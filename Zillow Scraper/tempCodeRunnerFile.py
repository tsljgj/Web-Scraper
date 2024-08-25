Price_history_text = WebDriverWait(driver, timeout_value).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Price history')]"))
    )
    # From the 'Price History' text, find the nearest 'Show more' button
    Show_more_button = Price_history_text.find_element(By.XPATH, "following::button[contains(., 'Show more')][1]")
    Show_more_button.click()