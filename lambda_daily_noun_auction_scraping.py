from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import boto3
import logging

table_name = 'nouns-nft-auction-inventory'
table = boto3.resource('dynamodb').Table(table_name)


def lambda_handler(event, context):
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome('/opt/chromedriver', chrome_options=options)

    driver.get('https://www.nouns.wtf/')
    title = driver.title
    logging.info(title)

    try:
        element = WebDriverWait(driver, 80).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div[2]/div/h1'))
        )
    finally:
        current_noun_number_element = driver.find_element_by_xpath(
            '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[1]/div[1]/div[2]/div/h1')
        current_noun = current_noun_number_element.get_attribute("innerHTML").split()[-1]
        previous_noun = int(current_noun) - 1

    if previous_noun % 10 == 0:
        table.put_item(
            Item={
                "noun_id": previous_noun,
                "winner_address": "nounders.eth",
                "winning_bid_eth": Decimal(0)
            }
        )
    else:

        url = 'https://www.nouns.wtf/' + 'noun/' + str(previous_noun)

        driver.get(url)

        try:
            element = WebDriverWait(driver, 80).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/div[2]/h2'))
            )
        finally:
            winner_bid_eth_element = driver.find_element_by_xpath(
                '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div[1]/div/div[2]/h2')
            winner_bid_eth = winner_bid_eth_element.get_attribute("innerHTML").split()[-1]

        try:
            element = WebDriverWait(driver, 80).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div/span[3]/a'))
            )
        finally:
            winner_address_element = driver.find_element_by_xpath(
                '//*[@id="root"]/div/div[1]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div/span[3]/a')
            winner_address = winner_address_element.get_property("href").split('/')[-1]

        table.put_item(
            Item={
                "noun_id": str(previous_noun),
                "winner_address": winner_address,
                "winning_bid_eth": winner_bid_eth
            }
        )

    driver.close();
    driver.quit();

    response = {
        "statusCode": 200,
        "body": title,
        "url": url,
        "winner_address": winner_address,
        "winner_bid_eth_element": winner_bid_eth,
        "previous_noun": previous_noun
    }

    return response
