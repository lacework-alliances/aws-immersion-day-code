#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import random
import string

import boto3
import json
import logging
import os
import time

import requests
import urllib3
from crhelper import CfnResource

SUCCESS = "SUCCESS"
FAILED = "FAILED"

LOG_NAME_PREFIX = "Lacework-Control-Tower-CloudTrail-Log-Account-"
AUDIT_NAME_PREFIX = "Lacework-Control-Tower-CloudTrail-Audit-Account-"
CONTROL_TOWER_CLOUDTRAIL_STACK = "aws-controltower-BaselineCloudTrail"

STACK_SET_SUCCESS_STATES = ["SUCCEEDED"]
STACK_SET_RUNNING_STATES = ["RUNNING", "STOPPING"]

DESCRIPTION = "Lacework's cloud-native threat detection, compliance, behavioral anomaly detection, "
"and automated AWS security monitoring."

http = urllib3.PoolManager()

LOGLEVEL = os.environ.get('LOGLEVEL', logging.INFO)
logger = logging.getLogger()
logger.setLevel(LOGLEVEL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
session = boto3.Session()

helper = CfnResource(json_logging=False, log_level="INFO", boto_level="CRITICAL", sleep_on_delete=15)


def lambda_handler(event, context):
  logger.info("s3ransomware.lambda_handler called.")
  logger.info(json.dumps(event))
  try:
    if "RequestType" in event: helper(event, context)
  except Exception as e:
    helper.init_failure(e)


@helper.create
@helper.update
def create(event, context):
  logger.info("setup.create called.")
  logger.info(json.dumps(event))

  bucket_name = os.environ['bucket_name']
  kms_key_arn = os.environ['kms_key_arn']

  s3_client = session.client('s3')

  objects = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=100)['Contents']

  client = session.resource('s3')

  for obj in objects:
    client.meta.client.copy({'Bucket': bucket_name, 'Key': obj['Key']}, bucket_name, obj['Key'], ExtraArgs={'ServerSideEncryption': 'aws:kms', 'SSEKMSKeyId': kms_key_arn})

  send_cfn_response(event, context, SUCCESS, {})
  return None


@helper.delete  # crhelper method to delete stack set and stack instances
def delete(event, context):
  logger.info("setup.delete called.")

  send_cfn_response(event, context, SUCCESS, {})
  return None


def send_cfn_response(event, context, response_status, response_data, physical_resource_id=None, no_echo=False,
                      reason=None):
  response_url = event['ResponseURL']

  logger.info(response_url)

  response_body = {
    'Status': response_status,
    'Reason': reason or "See the details in CloudWatch Log Stream: {}".format(context.log_stream_name),
    'PhysicalResourceId': physical_resource_id or context.log_stream_name,
    'StackId': event['StackId'],
    'RequestId': event['RequestId'],
    'LogicalResourceId': event['LogicalResourceId'],
    'NoEcho': no_echo,
    'Data': response_data
  }

  json_response_body = json.dumps(response_body)

  logger.info("Response body: {}".format(json_response_body))

  headers = {
    'content-type': '',
    'content-length': str(len(json_response_body))
  }

  try:
    response = http.request('PUT', response_url, headers=headers, body=json_response_body)
    logger.info("Status code: {}".format(response.status))

  except Exception as e:
    logger.error("send_cfn_response error {}".format(e))
