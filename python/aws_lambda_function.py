from __future__ import print_function

import json
import urllib
import boto3

print('Loading message function...')


def handle_rpi_record(message, context):
    # Based on what message type is received from AWS IoT, pass along to 
    # appropriate AWS App (SQS Queue or SNS)
    if(message['recordType'] == "alert"){
        send_to_sqs(message)
    } else if (message['recordType'] == "data"){
        send_to_sns(message)
    } else {
       print('Received AWS message unrecognized')
       return -1
    }
    
    return 0

def send_to_sqs(message, context):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='test-messages') # TODO: Update
    
    # Push received msg onto queue
    response = queue.send_message(MessageBody=json.dumps(message))
    

def send_to_sns(message, context):

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

    return ('Sent a message to an Amazon SNS topic.')

