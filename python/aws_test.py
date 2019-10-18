from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
 
# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient("myTestClient")
myMQTTClient.configureEndpoint("a376p1vo77mjsi-ats.iot.us-east-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/certs/Amazon_Root_CA_1.pem", "/home/pi/certs/0b8296d0dd-private.pem.key", "/home/pi/certs/0b8296d0dd-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
 
#connect and publish test packet
myMQTTClient.connect()
myMQTTClient.publish("Rpi_thing/info", "connected", 0)
myMQTTClient.publish("Rpi_thing/data", "Test Data", 0)
