import json
import logging
import os
import boto3


def lambda_handler(event: dict, context):
    try:
        elbv2_client = boto3.client('elbv2')
        ecs_client = boto3.client('ecs')
        taskArn = event['detail']['taskArn']  # From event
        clusterArn = event['detail']['clusterArn']  # From event

        taskDescription = ecs_client.describe_tasks(
            cluster=clusterArn,
            tasks=[taskArn],
            include=['TAGS']
        )

        taskTags = taskDescription['tasks'][0]['tags']

        for taskTag in taskTags:
            key = taskTag['key']
            value = taskTag['value']

            if 'RuleArn' in key:
                deleteListenerRule(elbv2_client, value)
        for taskTag in taskTags:
            key = taskTag['key']
            value = taskTag['value']

            if 'TargetGroupArn' in key:
                deleteTargetGroup(elbv2_client, value)

        return {
            "statusCode": 200,
            "statusDescription": "200 OK",
            "isBase64Encoded": False,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": "Pipeline deleted !"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "statusDescription": "500 NOT OK",
            "isBase64Encoded": False,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": "Task removal failed: " + str(e)
        }


def deleteListenerRule(elbv2_client, ruleArn):
    response = elbv2_client.delete_rule(RuleArn=ruleArn)


def deleteTargetGroup(elbv2_client, targetGroupArn):
    response = elbv2_client.delete_target_group(TargetGroupArn=targetGroupArn)
