from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

missing_in_bid_data = {2, 11, 26, 33, 35, 38, 42, 46, 47, 48, 49, 72, 85, 139, 143, 179, 228, 252, 253, 311, 371, 379,
                       433, 437, 453,
                       455, 464, 472, 489, 506, 513, 514, 523, 528, 534, 535, 546, 553, 556, 561, 564, 569, 594, 622}
missing_in_nouns_transaction = {384, 259, 261, 134, 135, 136, 263, 267, 395, 144, 405, 407, 538, 155, 539, 161, 34, 37,
                                558, 559, 563, 55, 447, 581, 456, 457, 332, 207, 599, 217, 602, 219, 476, 608, 231, 236,
                                111, 368, 113, 623, 115, 372, 118, 631, 507, 383}
csv_data = []

for noun in missing_in_bid_data.union(missing_in_nouns_transaction):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    url = 'https://nouns.wtf/noun/' + str(noun)
    driver.get(url)
    try:
        element = WebDriverWait(driver, 80).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/div[2]/h2'))
        )
    finally:
        winner_bid_eth_element = driver.find_element("xpath",
                                                     '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/div[2]/h2')
        winner_bid_eth = winner_bid_eth_element.get_attribute("innerHTML").split()[-1]

    try:
        element = WebDriverWait(driver, 80).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div/span[3]/a'))
        )
    finally:
        winner_address_element = driver.find_element("xpath",
                                                     '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div/span[3]/a')
        winner_address = winner_address_element.get_property("href").split('/')[-1]
        driver.close()

    row = {
        "noun_id": noun,
        "winner_address": winner_address,
        "winning_bid_eth": winner_bid_eth
    }

    csv_data.append(row)
    print(csv_data)

df = pd.DataFrame(csv_data)
df.to_csv("final_data/scraped_missing_data2.csv", index=False)
