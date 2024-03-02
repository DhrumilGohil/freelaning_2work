import json
import boto3
import urllib.request
import os

def lambda_handler(event, context):
    regions = [
    "ap-southeast-1",
    "ap-southeast-2",
    "ca-central-1",
    "eu-central-1",
    "eu-north-1",
    "eu-west-1",
    "eu-west-2",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2"
    ]

    for region in regions:
        ec2_client = boto3.client('ec2', region_name=region)
        instances = ec2_client.describe_instances()
        
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                user = ""
                instance_id = instance['InstanceId']
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'User':
                        user = tag['Value']
                # Send message to Slack
                slack_message = {
                  "text": f"Hello, {user}. Don't forget to check if you are still using the EC2 instance you created with instance_id {instance_id} in region {region}"
                }

                send_slack_message(slack_message)
        
    def send_slack_message(message):
        slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']  # Replace with your Slack webhook URL

        # Convert message to JSON
        message_json = json.dumps(message).encode('utf-8')

        # Send message to Slack
        req = urllib.request.Request(slack_webhook_url, data=message_json, headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req)
        print(response.read().decode('utf-8'))
                
    return {
        'statusCode': 200,
        'body': json.dumps('EC2 instances creation reminder send successfully.')
    }
