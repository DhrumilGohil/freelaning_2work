import boto3
import json
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
    iam_client = boto3.client('iam')
    role_name = 'EventBridgePutEventsRuleRole'
    createdeventBusArn = "<<CREATED_EVENT_BRIDGEBUS_ARN>>"
    eventBridgeRegion = "<<CREATED_REGION>>"
    
    # Define policy document
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "events:PutEvents"
                ],
                "Resource": [
                    createdeventBusArn
                ]
            }
        ]
    }
    
    # Create IAM role
    response = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                  "Effect": "Allow",
                  "Principal": {
                    "Service": "events.amazonaws.com"
                  },
                  "Action": "sts:AssumeRole"
                }
            ]
        })
    )
    
    # Get ARN of the created role
    role_arn = response['Role']['Arn']
    
    # Attach IAM policy to the role
    iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName='EventBridgeRulePutEventsPolicy',
        PolicyDocument=json.dumps(policy_document)
    )

    event_pattern = {
        "detail-type": ["AWS API Call via CloudTrail"],
        "detail": {
            "eventSource": ["ec2.amazonaws.com"],
            "eventName": ["RunInstances"]
        }
    }

# Convert the event pattern dictionary to a JSON string
    event_pattern_json = json.dumps(event_pattern)   
    for region in regions:
        if region != eventBridgeRegion:
            eventbridge = boto3.client('events', region_name=region)
            
            # Define EventBridge rule
            response = eventbridge.put_rule(
                Name='RestEc2SlackNotification',
                EventPattern=event_pattern_json,
                State='ENABLED',
                Description='This is the eventbridge rule for the ec2 creation.'
            )
        
            # Define the target - another EventBridge bus
            target = {
                'Arn': createdeventBusArn,
                'RoleArn': role_arn,
                'Id': 'MyEventBridgeBusTarget'
            }

            # Add target to the EventBridge rule
            response = eventbridge.put_targets(
                Rule='RestEc2SlackNotification',
                Targets=[target]
            )

    return {
        'statusCode': 200,
        'body': 'EventBridge rules created successfully in all regions.'
    }