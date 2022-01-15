import boto3
import json
import logging
import os

s3_client = boto3.client('s3')
ddb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    global LOGGER
    LOGGER = logging.getLogger()
    LOGGER.setLevel(level=os.getenv('LOG_LEVEL', 'DEBUG').upper())
    LOGGER.info(f'Received Event: {event}')

    # Default Response
    res = {
        "statusCode": 400,
        "body": json.dumps({"message": f"Bad Request: {event}"})
    }

    try:
        bucket_inventory = get_bucket_inventory()
        res = {"statusCode": 200, "body": json.dumps(
            {"message": bucket_inventory})}
    except Exception as e:
        res['body'] = json.dumps({"message": f"Error: {str(e)}"})

    return res


def get_bucket_inventory():
    """ Generate List of S3 Buckets """
    try:
        res = s3_client.list_buckets()
        bucket_inventory = {"buckets": []}
        for bucket in res['Buckets']:
            bucket_inventory['buckets'].append(bucket['Name'])
            ddb_put_item({"_id": bucket['Name']})
    except Exception as e:
        raise


def ddb_put_item(item):
    """ Put Item in DynamoDB """
    if os.environ.get('DDB_TABLE_NAME'):
        table = ddb.Table(os.environ.get('DDB_TABLE_NAME'))
        try:
            table.put_item(Item=item)
        except Exception as e:
            raise
