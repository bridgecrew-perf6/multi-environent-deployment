import logging
import os
import json
import boto3

_ddb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    global LOGGER
    LOGGER = logging.getLogger()
    LOGGER.setLevel(level=os.getenv('LOG_LEVEL', 'INFO'))
    LOGGER.info(f"Event: {event}")

    res = {
        "statusCode": 400,
        "body": json.dumps({"message": {}}),
    }

    try:
        if "Records" in event:
            item = {}
            item["_id"] = event["Records"][0]["s3"]["object"]["key"]
            item["_size"] = event["Records"][0]["s3"]["object"]["size"]
            item["_bucket"] = event["Records"][0]["s3"]["bucket"]["name"]
            item["_bucket_owner"] = event["Records"][0]["s3"]["bucket"]["ownerIdentity"]["principalId"]
            _put_resp = _ddb_put_item(item)
            res["statusCode"] = 200
            res["body"] = json.dumps({"message": _put_resp})
    except Exception as e:
        LOGGER.error(f"Error: {e}")
        res["body"] = json.dumps({"message": f"Error: {str(e)}"})


def _ddb_put_item(item):
    """ Insert Item into DynamoDB """
    if os.environ.get('DDB_TABLE_NAME'):
        _ddb_table = _ddb.Table(os.environ.get('DDB_TABLE_NAME'))
        try:
            return (_ddb_table.put_item(Item=item))
        except Exception as e:
            raise
