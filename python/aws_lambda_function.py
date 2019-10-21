from __future__ import print_function

import json
import urllib
import boto3

print('Initializing project3RecordHandler Lambda function...')

def handle_rpi_record(message, context):
    # Based on what message type is received from AWS IoT, pass along to 
    # appropriate AWS App (SQS Queue or SNS)
    
    if(message['recordType'] == "data"):
        print("Data Record Received")
        send_to_sqs(message)
    if(message['recordType'] == "alert"):
        print("Alert Record Received")
        send_to_sns(message)
    else:
       print('Received AWS message unrecognized')
       return -1
    
    return 0

def send_to_sqs(message):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='project3Queue', QueueOwnerAWSAccountId="582548553336")
    
    print(message)
    
    # Push received msg onto queue
    response = queue.send_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/582548553336/project3Queue", MessageBody=json.dumps(message))
    print(response)
    

def send_to_sns(message):

    # This function receives JSON input with three fields: the ARN of an SNS topic,
    # a string with the subject of the message, and a string with the body of the message.
    # The message is then sent to the SNS topic.
    #
    # Example:
    #   {
    #       "topic": "arn:aws:sns:REGION:123456789012:MySNSTopic",
    #       "subject": "This is the subject of the message.",
    #       "message": "This is the body of the message."
    #   }

    
    #topic = "arn:aws:sns:REGION:123456789012:MySNSTopic"
    snsTopic = "TBD" # TODO
    snsSubject = "RPI Sensor Alert Message"
    
    sns = boto3.client('sns')
    sns.publish(
        TopicArn=snsTopic,
        Subject=snsSubject,
        Message=message
    )

    return 0
