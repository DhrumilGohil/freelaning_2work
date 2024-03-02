import json
import boto3
import time

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
    tag_key = 'DeleteAtMidnight'
    tag_value = 'True'
    for region in regions:
        ec2_client = boto3.client('ec2', region_name=region)
        instances = ec2_client.describe_instances(            
            Filters=[
                    {
                        'Name': f'tag:{tag_key}',
                        'Values': [tag_value],
                    },
                ])
        
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                ec2_client.stop_instances(InstanceIds=[instance_id])
                time.sleep(30)
                for volume in instance['BlockDeviceMappings']:
                    volume_id = volume['Ebs']['VolumeId']
                    ec2_client.detach_volume(VolumeId=volume_id, InstanceId=instance_id)
                    time.sleep(10)
                    ec2_client.delete_volume(VolumeId=volume_id)
        
                ec2_client.terminate_instances(InstanceIds=[instance_id])
    
    return {
        'statusCode': 200,
        'body': json.dumps('EC2 instances terminated and attached volumes deleted successfully.')
    }
