import logging
import traceback
import json
import boto3
import base64
import os
import sys
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def obtain_userdata(lambda_event):
    # Function to extract the content of lambda_event
    try:
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        userdata_str_base64 = lambda_event["Records"][0]["kinesis"]["data"]
        logger.debug("Userdata_str_base64: %s", userdata_str_base64)
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
        return userdata_str_base64
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def decord_userdata(userdata_extracted):
    # Function to change userdate from base64 to utf-8
    try:
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        userdata_bytes = base64.b64decode(userdata_extracted)
        logger.debug("Userdata_bytes: %s", userdata_bytes)
        userdata_str = userdata_bytes.decode('utf-8')
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
        return userdata_str
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def transform_userdata(userdata_decorded):
    # Function to extract necessary keys from userdate
    try:
        t1 = time.time()
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        userdata_dict = json.loads(userdata_decorded)
        for key in userdata_dict:
            user_list = userdata_dict[key]
            logger.debug("User_list: %s", user_list)
            seen_Time = user_list[0]
            mac_address = user_list[1]
            location_x = str(user_list[2][0])
            location_y = str(user_list[3][0])
            put_dynamodb(seen_Time, mac_address, location_x, location_y)
        t2 = time.time()
        elapsed_time = t1-t2
        logger.info("Elapsed_time for proceesssing from\
                    transform_usedata to put_dynamodb:%s", elapsed_time)
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def put_dynamodb(seen_Time, mac_address, location_x, location_y):
    # Function to send necessary keys to DynamoDB
    try:
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        dynamoDB = boto3.client("dynamodb")
        dynamoDB.put_item(
            TableName=os.environ.get("TABLE_NAME"),
            Item={
                "seen_Time": {
                    "S": seen_Time
                },
                "mac_address": {
                    "S": mac_address
                },
                "location_x": {
                   "N": location_x
                },
                "location_y": {
                    "N": location_y
                }
            }
            )
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def get_response(status_code):
    # Function to return statusCode
    try:
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
        logger.info("End of "
                    + "lambda_handler" + "--------------")
        return {
                "statusCode": status_code,
                "body": "I Received userdata from cmxdata-stream!",
                "headers": {
                        'Content-Type': 'text/plain'
                }
            }
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def lambda_handler(event, context):
    t1 = time.time()
    # Start lambda function
    logger.info("Start of " +
                sys._getframe().f_code.co_name + "------------")
    logger.info("Event: %s", event)
    try:
        extracted_userdata = obtain_userdata(event)
        decorded_userdata = decord_userdata(extracted_userdata)
        transform_userdata(decorded_userdata)
        response = get_response(200)
        t2 = time.time()
        elapsed_time = t2-t1
        logger.info("Elapsed_time for all functions:%s", elapsed_time)
        return response
    except Exception:
        logger.error(traceback.format_exc())
        return get_response(500)
