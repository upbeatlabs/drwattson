# *************************************************** 
#   This is a example program for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
#   --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

#   This example demonstrates the use of Dr. Wattson with AWS IoT to publish energy
#   data read from Dr. Wattson to the AWS Cloud. It is based on the example
#   from AWS IoT - please refer to AWS IoT for the necessary setup steps.
#   You will need to provide the following information from your setup:
#   endpoint, rootCA file, certificate file, private key file
#   You can also provide the following optional arguments that have defaults:
#   whether to use websockets for communication, thing name, client id

#   The communication happens over I2C. 2 pins are required to interface. 
#   There are 4 selectable I2C address possibilities per board (selectable
#   via two solder jumpers (that select each pin to be high or low). Based 
#   on this, there are 4 possible addresses:

#   I2C address  SJ1   SJ2
#   0x74         LOW   LOW
#   0x75         LOW   HIGH
#   0x76         HIGH  LOW
#   0x77         HIGH  HIGH

#   There are also 2 output pins - ZCD and EVENT that can be used for
#   external interrupts on Zero Cross Detection and certain
#   configured events. In this example, they are not used
 
#   Written by Sridhar Rajagopal for Upbeat Labs LLC.
#   BSD license. All text above must be included in any redistribution
# *

'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import json
import argparse

import UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521 as UpbeatLabs_MCP39F521


# Shadow JSON schema:
#
# Name: Bot
# {
#	"state": {
#		"desired":{
#			"property":<INT VALUE>
#		}
#	}
# }

# Custom Shadow callback
def customShadowCallback_Update(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("property: " + str(payloadDict["state"]["desired"]["property"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

def customShadowCallback_Delete(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")
    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowUpdater", help="Targeted client id")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
thingName = args.thingName
clientId = args.clientId

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
if useWebsocket:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, 443)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
    myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)

# Delete shadow JSON doc
deviceShadowHandler.shadowDelete(customShadowCallback_Delete, 5)

# Update shadow in a loop
loopCount = 0
wattson = UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521()

while True:
    (ret, result) = wattson.readEnergyData()

    JSONPayload = '{{"state":{{"reported":{{"voltageRMS":{0}, "currentRMS":{1}, "lineFrequency":{2}, "powerFactor":{3}, "activePower":{4}, "reactivePower":{5}, "apparentPower":{6} }} }} }}'.format(result.voltageRMS, result.currentRMS, result.lineFrequency, result.powerFactor, result.activePower, result.reactivePower, result.apparentPower)
    print JSONPayload
    deviceShadowHandler.shadowUpdate(JSONPayload, None, 5)
    loopCount += 1
    time.sleep(1)
