import boto3
import csv

table_name = 'nouns-nft-auction-inventory'
table = boto3.resource('dynamodb').Table(table_name)
files_to_insert = ["final_data/etherscan_processed.csv", "final_data/scraped_missing_data.csv"]
for file in files_to_insert:
    with open(file) as etherscan_data:
        reader = csv.DictReader(etherscan_data)
        for record in reader:
            print("Inserting record into the dynamodb table: ", record)
            table.put_item(Item={
                "noun_id": record["noun_id"],
                "winner_address": record["winner_address"],
                "winning_bid_eth": record["winning_bid_eth"]
            }
            )
