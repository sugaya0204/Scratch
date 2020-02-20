import logging
import traceback
import boto3
import os
import requests
import sys
from boto3.dynamodb.types import TypeDeserializer
from requests_aws4auth import AWS4Auth


class StreamTypeDeserializer(TypeDeserializer):
    # Class that deserializes DynamoDB type to python type
    def _deserialize_n(self, value):
        return float(value)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

host = os.environ.get("ES_ENDPOINT")
index = os.environ.get("INDEX")
type = os.environ.get("TYPE")
url = host + "/" + index + "/" + type + "/"
headers = {"Content-Type": "application/json"}


def create_awsauth():
    '''
    Function to obtain authentication information
    necessary for HTTP communication
    '''
    logger.info("Start of " +
                sys._getframe().f_code.co_name + "------------")
    try:
        service = "es"
        region = os.environ.get("REGION_NAME")
        credentials = boto3.Session().get_credentials()
        logger.debug("Region: %s", region)
        logger.debug("Credentials: %s", credentials)
        logger.debug("Access_key: %s", credentials.access_key)
        logger.debug("Secret_key: %s", credentials.secret_key)
        logger.debug("Token: %s", credentials.token)
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                           region, service, session_token=credentials.token)
        logger.debug("Awsauth: %s", awsauth)
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
        return awsauth
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def delete_to_es(lambda_event, awsauth):
    # Function to delete data in Amazon ES
    try:
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        mac_address =\
            lambda_event["Records"][0]["dynamodb"]["Keys"]["mac_address"]["S"]
        logger.debug("Host: %s", host)
        logger.debug("Url: %s", url)
        res = requests.delete(url + mac_address, auth=awsauth)
        logger.info("contents of res-----------------------")
        logger.info(res.status_code)
        logger.info(res.text)
        # 処理のリターンをログで見れる様にする
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def obtain_userdata(lambda_event):
    '''
    Function that extracts and processes
    the contents of lambda_event
    '''
    try:
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        ddb_deserializer = StreamTypeDeserializer()
        doc_fields = ddb_deserializer.deserialize(
            {
                "M": lambda_event["Records"][0]["dynamodb"]["NewImage"]
            })
        logger.debug("Doc_fields: %s", doc_fields)
        mac_address = doc_fields["mac_address"]
        logger.debug("Mac_address: %s", mac_address)
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
        return doc_fields, mac_address
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def put_to_es(doc_fields, mac_address, awsauth):
    # Function to send userdata to  cmxdata index in AmazonES
    try:
        logger.info("Start of " +
                    sys._getframe().f_code.co_name + "------------")
        logger.debug("Host: %s", host)
        logger.debug("Url: %s", url)
        res = requests.put(url + mac_address, auth=awsauth,
                           json=doc_fields, headers=headers)
        logger.info("Status_code:%s", res.status_code)
        logger.info("Text:%s", res.text)
        logger.info("End of "
                    + sys._getframe().f_code.co_name + "--------------")
    except Exception as e:
        raise Exception(e.args, "Exception occurred in "
                        + sys._getframe().f_code.co_name)


def get_response(status_code):
    # Function to response statuscode to DynamoDB
    logger.info("Start of " +
                sys._getframe().f_code.co_name + "------------")
    logger.info("End of "
                + sys._getframe().f_code.co_name + "--------------")
    logger.info("End of "
                + "lambda_handler" + "--------------")
    return {
            "statusCode": status_code,
            "body": "I Received userdata from dynamoDB and put to amazonES",
            "headers": {
                    'Content-Type': 'text/plain'
            }
        }


def lambda_handler(event, context):
    # Start lambda function
    logger.info("Start of " +
                sys._getframe().f_code.co_name + "------------")
    try:
        logger.info("Event: %s", event)
        awsauth = create_awsauth()
        logger.debug("Awsauth: %s", awsauth)
        if event["Records"][0]["eventName"] == "REMOVE":
            delete_to_es(event, awsauth)
        else:
            doc_fields, mac_address = obtain_userdata(event)
            put_to_es(doc_fields, mac_address, awsauth)
        return get_response(200)
    except Exception:
        logger.error(traceback.format_exc())
        return get_response(500)
