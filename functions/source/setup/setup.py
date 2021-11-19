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


import boto3
import json
import logging
import os
import base64
import re
from botocore.signers import RequestSigner
from kubernetes import client, config

import urllib3
from crhelper import CfnResource

SUCCESS = "SUCCESS"
FAILED = "FAILED"

http = urllib3.PoolManager()

LOGLEVEL = os.environ.get('LOGLEVEL', logging.INFO)
logger = logging.getLogger()
logger.setLevel(LOGLEVEL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
session = boto3.Session()

helper = CfnResource(json_logging=False, log_level="INFO", boto_level="CRITICAL", sleep_on_delete=15)


def lambda_handler(event, context):
  logger.info("setup.lambda_handler called.")
  helper(event, context)


@helper.create
@helper.update
def create(event, context):
  logger.info("setup.create called.")
  list_pod_for_all_ns()
  send_cfn_response(event, context, SUCCESS, {"Message": "created"})


@helper.delete  # crhelper method to delete stack set and stack instances
def delete(event, context):
  logger.info("setup.delete called.")
  send_cfn_response(event, context, SUCCESS, {"Message": "deleted"})


def get_bearer_token(cluster_id, region):
  logger.info("setup.get_bearer_token called with {} and {}".format(cluster_id, region))
  STS_TOKEN_EXPIRES_IN = 60
  session = boto3.session.Session()

  client = session.client('sts', region_name=region)
  service_id = client.meta.service_model.service_id

  signer = RequestSigner(
    service_id,
    region,
    'sts',
    'v4',
    session.get_credentials(),
    session.events
  )

  params = {
    'method': 'GET',
    'url': 'https://sts.{}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15'.format(region),
    'body': {},
    'headers': {
      'x-k8s-aws-id': cluster_id
    },
    'context': {}
  }

  signed_url = signer.generate_presigned_url(
    params,
    region_name=region,
    expires_in=STS_TOKEN_EXPIRES_IN,
    operation_name=''
  )
  base64_url = base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8')
  # remove any base64 encoding padding:
  return 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)
  # If making a HTTP request you would create the authorization headers as follows:
  # headers = {'Authorization': 'Bearer ' + get_bearer_token('my_cluster', 'us-east-1')}


def list_pod_for_all_ns():
  logger.info("setup.list_pod_for_all_ns called.")
  eks_cluster_name = os.environ['eks_cluster_name']
  eks_cluster_region = os.environ['eks_cluster_region']
  eks_cluster_endpoint = os.environ['eks_cluster_endpoint']
  logger.info("environment variables eks_cluster_name={} eks_cluster_region={} eks_cluster_endpoint={}".format(eks_cluster_name, eks_cluster_region, eks_cluster_endpoint))
  ApiToken = get_bearer_token(eks_cluster_name, eks_cluster_region)
  configuration = client.Configuration()
  configuration.host = eks_cluster_endpoint
  configuration.verify_ssl = False
  configuration.debug = True
  configuration.api_key = {"authorization": "Bearer " + ApiToken}
  client.Configuration.set_default(configuration)
  v1 = client.CoreV1Api()
  logger.info("Getting pod names!")
  all_pods_names = [i.metadata.name for i in v1.list_pod_for_all_namespaces(watch=False).items]
  logger.info(all_pods_names)
  return all_pods_names

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


def get_agent_access_token(lacework_api_credentials):
  logger.info("setup.get_access_token called.")
