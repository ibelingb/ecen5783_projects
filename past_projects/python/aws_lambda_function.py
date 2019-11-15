# ECEN5783
# Author: Brian Ibeling
# 10/19/2019
#
"""
    The project3RecordHandler handle_rpi_record lambda function receives JSON 
    Data and Alert packets from the connected AWS IoT instance. These records
    are then passed over to Connor Shapiro's SNS and SQS AWS components as shown
    in the respective TopicArn and QueueUrl parameters.

    + Resources and Citations +
    The following resources were used to assist with development of this SW.
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.get_queue_url
    - https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html
    - https://docs.aws.amazon.com/lambda/latest/dg/with-sns-example.html
    - https://startupnextdoor.com/adding-to-sqs-queue-using-aws-lambda-and-a-serverless-apiendpoint/
"""

from __future__ import print_function
import json
import urllib
import boto3

#-----------------------------------------------------------------------
print('Initializing project3RecordHandler Lambda function...')

#-----------------------------------------------------------------------
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

#-----------------------------------------------------------------------
def send_to_sqs(message):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='project3Queue', QueueOwnerAWSAccountId="582548553336")
    
    # Print the received data message from the Project1 GUI
    print(message)
    
    # Push received msg onto queue and print the response for debugging
    response = queue.send_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/582548553336/project3Queue", MessageBody=json.dumps(message))
    print(response)
    
    return 0

#-----------------------------------------------------------------------
def send_to_sns(message):
    # This function receives JSON input with three fields: the ARN of an SNS topic,
    # a string with the subject of the message, and a string with the body of the message.
    # The message is then sent to the SNS topic.
    
    sns = boto3.client('sns')
    
    # Print the received Alert message from the Project1 GUI
    print(message)
    
    # Push received msg onto queue and print the response for debugging
    response = sns.publish(
        TopicArn="arn:aws:sns:us-east-1:582548553336:projectThreeAlerts",
        Subject="Project3 Sensor Alert Message",
        Message=str(message)
    )
    print(response)

    return 0
#-----------------------------------------------------------------------
