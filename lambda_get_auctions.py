import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = 'nouns-nft-auction-inventory'
table = boto3.resource('dynamodb').Table(table_name)


def respond(result=None, statusCode=None):
    return {
        'statusCode': statusCode if statusCode else '500',
        'body': json.dumps(result) if result else "Internal Server Error",
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, indent=2))
    if event.get("queryStringParameters"):
        id = event.get("queryStringParameters").get("id")
        if not id:
            return respond({
                "error": "Only 'id' corresponding to the noun's id is expected as query parameter."
            }, 400)
        auction = get_auction_with_noun_id(id)
        if auction:
            return respond(auction, 200)
        else:
            return respond({
                "error": f"Auction with id=[{id}] not found."
            }, 404)

    return respond(get_all_auctions(), 200)


def get_auction_with_noun_id(id):
    return table.get_item(
        Key={
            "noun_id": id
        }
    ).get("Item")


def get_all_auctions():
    return table.scan()["Items"]