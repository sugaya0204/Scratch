import sys
import os
import logging
import traceback
import boto3
import json


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def return_validator():
    # Function to return validation to Meraki
    logger.info("Start of " +
                sys._getframe().f_code.co_name + "------------")
    logger.info("Validator: %s", os.environ.get("Validator"))
    logger.info("End of " + sys._getframe().f_code.co_name + "--------------")
    logger.info("End of " + "lambda_handler" + "--------------")
    try:
        return {
            "statusCode": '200',
            "body": os.environ.get("Validator"),
            "headers": {
                'Content-Type': 'text/plain',
            }
        }
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def create_userdata(lambda_event):
    # Function to extract the contents of lambda_event
    logger.info("Start of " +
                sys._getframe().f_code.co_name + "------------")
    try:
        body_dict = json.loads(lambda_event['body'])
        logger.debug("Body_dict: %s", body_dict)
        client_list = body_dict["data"]["observations"]
        logger.debug("Client_list: %s", client_list)
        logger.debug(type(client_list))
        logger.debug(client_list[0])
        user_data_dict = {}
        i = 1
        for user_data in client_list:
            logger.debug(user_data)
            user_data_dict["user" + str(i)] = [user_data["seenTime"]]
            user_data_dict["user" + str(i)].append(user_data["clientMac"])
            user_data_dict["user" + str(i)].append(user_data["location"]["x"])
            user_data_dict["user" + str(i)].append(user_data["location"]["y"])
            i += 1
        logger.debug("User_data_dict: %s", user_data_dict)
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
        return(user_data_dict)
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def put_record_to_kinesis(user_data_dict):
    # Function to send usedata to Kinesis
    try:
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        user_data_str = json.dumps(user_data_dict)
        user_data_byte = user_data_str.encode()
        logger.debug("User_data_byte: %s", user_data_byte)
        res = boto3.client('kinesis').put_records(
            Records=[
                {
                    "Data": user_data_byte,
                    "PartitionKey": "userdata"
                },
            ],
            StreamName="cmxdata-stream"
        )
        logger.info("put records respons-------------------------")
        logger.info(res)
        logger.info("End of " +
                    sys._getframe().f_code.co_name + "--------------")
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def get_response(status_code):
    # Function to return statusCode to Meraki
    try:
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        logger.info("End of " +
                    sys._getframe().f_code.co_name + "--------------")
        logger.info("End of " + "lambda_handler" + "--------------")
        return {
                "statusCode": status_code,
                "body": "received",
                "headers": {
                        'Content-Type': 'text/plain'
                }
            }
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def lambda_handler(event, context):
    # Start lambda function
    logger.info("Start of " +
                sys._getframe().f_code.co_name + "------------")
    try:
        logger.info("Event: %s", event)
        if event["httpMethod"] == "GET":
            return return_validator()
        else:
            user_data_dict = create_userdata(event)
            put_record_to_kinesis(user_data_dict)
            return get_response(200)
    except Exception:
        logger.error(traceback.format_exc())
        get_response(500)
