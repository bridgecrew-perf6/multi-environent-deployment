import json
import logging
import os
import random
from time import sleep


def lambda_handler(event, context):
    global LOGGER
    LOGGER = logging.getLogger()
    LOGGER.setLevel(level=os.getenv('LOG_LEVEL', 'DEBUG'))
    LOGGER.info(f"received event: {event}")

    fmt_log_msg = {f"third_party_api_error": False}

    # Add error logs, if
    r = call_third_party_api()

    if r:
        fmt_log_msg['third_party_api_error'] = True
        fmt_log_msg['remaining_time_in_millis'] = context.get_remaining_time_in_millis()

    LOGGER.info(json.dumps(fmt_log_msg))

    return {
        'statusCode': 200,
        'body': json.dumps({"message": fmt_log_msg})
    }


def call_third_party_api():
    return random_error_generator(n=os.getenv("PERCENTAGE_ERRORS", 75))


def random_error_generator(n):
    """ Generate error for given e """
    r = False
    if random.randint(1, 100) <= int(n):
        sleep(1)
        r = True
    return r
