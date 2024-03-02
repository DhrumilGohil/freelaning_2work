import json
import urllib.request
import os

def lambda_handler(event, context):
    accountNumber = event['account']
    userName = event['detail']['userIdentity']['userName']
    instanceId = event['detail']['responseElements']['instancesSet']['items'][0]['instanceId']
    region = event['detail']['awsRegion']
    tagSet = event['detail']['requestParameters']['tagSpecificationSet']['items'][0]['tags']
    for tag in tagSet:
        if tag['key'] == 'Name':
            instance_name = tag['value']
            break
  
    slack_message = {
     "attachments": [
        {
            "color": "#36a64f",
            "pretext": "New EC2 instance created",  # A brief description before the main content
            "fields": [
                {
                    "title": "User Name",
                    "value": f":information_source: {userName}",
                    "short": True
                },
                {
                    "title": "Region",
                    "value": region,
                    "short": True
                },
                {
                    "title": "Account Number",
                    "value": accountNumber,
                    "short": True
                },
                {
                    "title": "Instance ID",
                    "value": instanceId,
                    "short": True
                },
                {
                    "title": "Instance Name",
                    "value": instance_name,
                    "short": True
                }
            ]
        }
    ]
    }

    # Send message to Slack
    send_slack_message(slack_message)
      
    return {
      'statusCode': 200,
      'body': json.dumps('Hello from Lambda!')
    }

def send_slack_message(message):
    slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']  # Replace with your Slack webhook URL
    print(slack_webhook_url)
    # Convert message to JSON
    message_json = json.dumps(message).encode('utf-8')

    # Send message to Slack
    req = urllib.request.Request(slack_webhook_url, data=message_json, headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(req)
    print(response.read().decode('utf-8'))