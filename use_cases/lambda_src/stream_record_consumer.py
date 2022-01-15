import base64
import logging
import os
import base64
import boto3
import time
import json


class global_args:
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


def lambda_handler(event, context):
    global LOGGER
    LOGGER = set_logger(logging.INFO)
    resp = {"status": False, "records": ""}
    LOGGER.info("Received event: " + str(event))
    bucket_name = os.getenv("BUCKET_NAME")

    try:
        if event.get("Records"):
            for record in event["Records"]:
                # Kinesis data is base64 encoded so decode here
                payload = base64.b64decode(record["kinesis"]["data"])
                write_data_to_s3(bucket_name, payload)
                LOGGER.info(f"Decoded payload: {payload}")
            LOGGER.info(
                f'{{"records_processed": {len(event.get("""Records"""))}}}')
            resp["status"] = True
    except Exception as e:
        LOGGER.error(f"Error: {e}")
        resp["error_message"] = str(e)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": resp})
    }


def set_logger(lv=global_args.LOG_LEVEL):
    logging.basicConfig(level=lv)
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(lv)
    return LOGGER


def write_data_to_s3(bucket_name, payload):
    s3 = boto3.resource('s3')
    object = s3.Object(bucket_name, f"{int(time.time()*1000)}.json")
    resp = object.put(Body=payload)
    LOGGER.info(json.dumps(resp))


if __name__ == "__main__":
    lambda_handler({}, {})
