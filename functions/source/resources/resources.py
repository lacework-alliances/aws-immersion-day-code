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
import json

import boto3
import logging
import os

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
  logger.info("resources.lambda_handler called.")
  try:
    if "RequestType" in event: helper(event, context)
  except Exception as e:
    helper.init_failure(e)


@helper.create
@helper.update
def create(event, context):
  logger.info("resources.create called and does nothing right now.")
  send_cfn_response(event, context, SUCCESS, {})
  # add honeycomb telemetry


@helper.delete
def delete(event, context):
  logger.info("resources.delete called.")

  s3 = boto3.resource('s3')
  try:
    ransomware_bucket_name = os.environ['ransomware_bucket']
    logger.info("Deleting ransomware s3 bucket {}".format(ransomware_bucket_name))
    ransomware_bucket = s3.Bucket(ransomware_bucket_name)
    ransomware_bucket.objects.delete()
    ransomware_bucket.object_versions.delete()
    logger.info(ransomware_bucket.delete())
  except Exception as delete_ransomware_bucket_exception:
    logger.warning("Problem occurred while deleting s3 bucket: {}".format(delete_ransomware_bucket_exception))

  try:
    lambda_bucket_name = os.environ['lambda_bucket']
    logger.info("Deleting lambda s3 bucket {}".format(lambda_bucket_name))
    lambda_bucket = s3.Bucket(lambda_bucket_name)
    lambda_bucket.objects.delete()
    lambda_bucket.object_versions.delete()
    logger.info(lambda_bucket.delete())
  except Exception as delete_lambda_bucket_exception:
    logger.warning("Problem occurred while deleting s3 bucket: {}".format(delete_lambda_bucket_exception))

  try:
    app_bucket_name = os.environ['app_bucket']
    logger.info("Deleting app s3 bucket {}".format(app_bucket_name))
    app_bucket = s3.Bucket(app_bucket_name)
    app_bucket.objects.delete()
    app_bucket.object_versions.delete()
    logger.info(app_bucket.delete())
  except Exception as delete_app_bucket_exception:
    logger.warning("Problem occurred while deleting s3 bucket: {}".format(delete_app_bucket_exception))

  try:
    lacework_bucket_name = os.environ['lacework_bucket']
    logger.info("Deleting lacework s3 bucket {}".format(lacework_bucket_name))
    lacework_bucket = s3.Bucket(lacework_bucket_name)
    lacework_bucket.objects.delete()
    lacework_bucket.object_versions.delete()
    logger.info(lacework_bucket.delete())
  except Exception as delete_lacework_bucket_exception:
    logger.warning("Problem occurred while deleting s3 bucket: {}".format(delete_lacework_bucket_exception))

  try:
    artifact_bucket_name = os.environ['artifact_bucket']
    logger.info("Deleting artifact s3 bucket {}".format(artifact_bucket_name))
    artifact_bucket = s3.Bucket(artifact_bucket_name)
    artifact_bucket.objects.delete()
    artifact_bucket.object_versions.delete()
    logger.info(artifact_bucket.delete())
  except Exception as delete_artifact_bucket_exception:
    logger.warning("Problem occurred while deleting s3 bucket: {}".format(delete_artifact_bucket_exception))

  try:
    eks_audit_bucket_name = os.environ['eks_audit_bucket']
    logger.info("Deleting eks audit s3 bucket {}".format(eks_audit_bucket_name))
    eks_audit_bucket = s3.Bucket(eks_audit_bucket_name)
    eks_audit_bucket.objects.delete()
    eks_audit_bucket.object_versions.delete()
    logger.info(eks_audit_bucket.delete())
  except Exception as eks_audit_bucket_exception:
    logger.warning("Problem occurred while deleting s3 bucket: {}".format(eks_audit_bucket_exception))

  try:
    code_guru_bucket_name = os.environ['code_guru_bucket']
    logger.info("Deleting code guru s3 bucket {}".format(code_guru_bucket_name))
    code_guru_bucket = s3.Bucket(code_guru_bucket_name)
    code_guru_bucket.objects.delete()
    code_guru_bucket.object_versions.delete()
    logger.info(code_guru_bucket.delete())
  except Exception as code_guru_bucket_exception:
    logger.warning("Problem occurred while deleting s3 bucket: {}".format(code_guru_bucket_exception))

  try:
    staging_ecr_repo = os.environ['staging_ecr_repo']
    logger.info("Deleting repositories")
    ecr_client = session.client("ecr")
    aws_account_id = context.invoked_function_arn.split(":")[4]
    logger.info(ecr_client.delete_repository(
      registryId=aws_account_id,
      repositoryName=staging_ecr_repo,
      force=True
    ))
  except Exception as delete_repo_exception:
    logger.warning("Problem occurred while deleting repository: {}".format(delete_repo_exception))

  try:
    prod_ecr_repo = os.environ['prod_ecr_repo']
    logger.info(ecr_client.delete_repository(
      registryId=aws_account_id,
      repositoryName=prod_ecr_repo,
      force=True
    ))
  except Exception as delete_repo_exception:
    logger.warning("Problem occurred while deleting repository: {}".format(delete_repo_exception))

  send_cfn_response(event, context, SUCCESS, {})


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
    logger.info("send_cfn_response: {}".format(response.status))

  except Exception as e:
    logger.error("send_cfn_response error {}".format(e))
