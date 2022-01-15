import logging
import json
import random
import os
import boto3

_ddb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    global LOGGER
    LOGGER = logging.getLogger()
    LOGGER.setLevel(level=os.getenv("LOG_LEVEL", "INFO").upper())

    LOGGER.info(f"received_event:{event}")
    resp = {
        "statusCode": 400,
        "body": json.dumps({"message": {}})
    }
    _random_user_name = ["Aarakocra", "Aasimar", "Beholder", "Bugbear", "Centaur", "Changeling", "Deep Gnome", "Deva", "Dragonborn", "Drow", "Dwarf", "Eladrin", "Elf", "Firbolg", "Genasi", "Githzerai", "Gnoll", "Gnome", "Goblin", "Goliath", "Hag", "Half-Elf",
                         "Half-Orc", "Halfling", "Hobgoblin", "Human", "Kalashtar", "Kenku", "Kobold", "Lizardfolk", "Loxodon", "Mind Flayer", "Minotaur", "Orc", "Shardmind", "Shifter", "Simic Hybrid", "Tabaxi", "Tiefling", "Tortle", "Triton", "Vedalken", "Warforged", "Wilden", "Yuan-Ti"]

    try:
        if event.get("pathParameters"):
            item = {}
            item["_id"] = event.get("pathParameters").get("user_name", random.choice(_random_user_name))
            item["likes"] =event.get("pathParameters").get("likes", random.randint(1, 100))
            _put_resp = _ddb_put_item(item)
            resp["statusCode"] = 200
            resp["body"] = json.dumps({"message": f"Successfully updated {item['_id']} with {item['likes']} likes"})
    except Exception as e:
        LOGGER.error(f"Exception:{e}")
        resp["statusCode"] = 500
        resp["body"] = json.dumps({"message": f"Exception:{e}"})
    
    return resp


def _ddb_put_item(item):
    """ Insert Item into DynamoDb Table """
    if os.environ.get('DDB_TABLE_NAME'):
        _ddb_table = _ddb.Table(os.environ.get('DDB_TABLE_NAME'))
        try:
            return(_ddb_table.put_item(Item=item))
        except Exception as e:
            raise