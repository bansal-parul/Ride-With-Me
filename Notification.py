""""
Function to share rider details with the driver

""""


import json
import os
import boto3
from botocore.exceptions import ClientError

sns_client = boto3.client('sns', region_name='us-east-1')
ses_client = boto3.client('ses', region_name='us-east-1')
topic_arn = "arn:aws:sns:us-east-1:089450761590:DriverNotification"
def lambda_handler(event, context):
    # Get the phone number, email, and content from the event object
    body = json.loads(event['body'])
    phone_number = body['phone_number']
    email = body['email']
    content = body['content']
    subject = body['subject']
    #phone_number = event.get('phone_number')
    #email = event.get('email')
    #content = event.get('content')
    #subject = event.get('subject')
    message = {"Subject": {"Data": subject}, "Body": {"Html": {"Data": content}}}
    try:
        if phone_number:
            # Send an SMS message
            sns_client.publish(
                PhoneNumber=phone_number,
                Message=content,
                Subject= subject
            )
            
        if email:
            # Send an email message
            ses_client.send_email(
                Source = "parulbansal52@gmail.com",
                Destination={'ToAddresses': [email]},
                Message=message
            )

        return {
            'statusCode': 200,
            'body': 'Notification sent successfully.'
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': f'Error sending notification: {e.response["Error"]["Message"]}'
        }

