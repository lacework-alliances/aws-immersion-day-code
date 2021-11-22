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
import logging
import os

import urllib3

SUCCESS = "SUCCESS"
FAILED = "FAILED"

http = urllib3.PoolManager()

LOGLEVEL = os.environ.get('LOGLEVEL', logging.INFO)
logger = logging.getLogger()
logger.setLevel(LOGLEVEL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
session = boto3.Session()


def lambda_handler(event, context):
  logger.info("deleteeks.lambda_handler called.")
  eks_client = session.client("eks")
  aws_account_id = context.invoked_function_arn.split(":")[4]

  cluster = "{}-eks".format(aws_account_id)
  ngdict = eks_client.list_nodegroups(
    clusterName=cluster
  )
  for ng in ngdict['nodegroups']:
    logger.info(eks_client.delete_nodegroup(
      clusterName=cluster,
      nodegroupName=ng
    ))

  response = eks_client.delete_cluster(
    name=cluster
  )
  logger.info("Deleted cluster {} {}".format(cluster, response))

  logger.info("Completing lifecycle hook")
  as_client = session.client('autoscaling')
  logger.info(as_client.complete_lifecycle_action(LifecycleHookName=event['detail']['LifecycleHookName'],
                                                  LifecycleActionToken=event['detail']['LifecycleActionToken'],
                                                  AutoScalingGroupName=event['detail']['AutoScalingGroupName'],
                                                  LifecycleActionResult='CONTINUE',
                                                  InstanceId=event['detail']['EC2InstanceId']))
  logger.info("Delete last resources")
  logger.info("Deleting Lambda s3 bucket")
  bucket = os.environ['lambda_zips_bucket']
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(bucket)
  bucket.objects.delete()
  logger.info(bucket.delete())

  logger.info("Deleting Lambda function")
  function_name = context.function_name
  lambda_client = session.client("lambda")
  logger.info(lambda_client.delete_function(
    FunctionName=function_name
  ))

  logger.info("Deleting Lambda function role")
  role_name = os.environ['eks_delete_function_role']
  iam_client = session.client("iam")
  logger.info(iam_client.delete_role(
    RoleName=role_name
  ))

  logger.info("Deleting asg lifecycle event rule")
  events_client = session.client("events")
  rulesdict = events_client.list_rule_names_by_target(
    TargetArn=context.invoked_function_arn
  )

  for rule in rulesdict['RuleNames']:
    logger.info(events_client.delete_rule(
      Name=rule
    ))

  logger.info("Deleting lifecycle hook")
  hook_name = os.environ['bastion_asg_lifecycle_hook']
  asg_name = os.environ['bastion_asg']
  asg_client = session.client("autoscaling")
  logger.info(asg_client.delete_role(
    LifecycleHookName=hook_name,
    AutoScalingGroupName=asg_name
  ))
