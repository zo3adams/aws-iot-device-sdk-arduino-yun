'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

# Thermostat App side control program

import sys
sys.path.append("./lib/protocol/")
sys.path.append("./lib/util/")
sys.path.append("./lib/exception/")
import getopt
from ssl import *
import time
import json
import thread
import glob

# Check dependency
libraryCheck = True
try:
    import paho.mqtt.client as mqtt
    import logManager
    import mqttCore
    import AWSIoTExceptions
except ImportError:
    libraryCheck = False
    print "paho-mqtt python package missing. Please install/reinstall it."
try:
    import Tkinter as tk
except ImportError:
    libraryCheck = False
    print "Tkinter python package missing. Please install/reinstall it."

# Tool functions
def customCallback(client, userdata, message):
    # print "ThermostatApp received a new message: " + str(message.payload) + " from topic: " + str(message.topic)
    if str(message.topic) == "$aws/things/room/shadow/get/accepted" and userdata is not None:
        recvJSONString = message.payload
        reportedData = None
        try:
            recvJSONDict = json.loads(recvJSONString)
            reportedData = recvJSONDict[u'state'][u'reported'][u'Temp']
            userdata.set(str(reportedData) + " F") # Update the reported data in GUI
        except Exception:
            print "Invalid JSON or missing attribute"
    else:
        pass

def getLatestReported(srcPythonMQTTCore):
    while(True):
        try:
            srcPythonMQTTCore.publish("$aws/things/room/shadow/get", "", 0, False) # Start a shadow get request per 0.5 seconds, QoS 0
            time.sleep(0.5)
        except AWSIoTExceptions.publishTimeoutException:
            print "Syncing reported data: A Publish Timeout Exception happened."
        except AWSIoTExceptions.publishError:
            print "Syncing reported data: A Publish Error happened."
        except:
            print "Syncing reported data: Unknown Error in Publish. Connected to WiFi?"

def buttonAction(srcEntry, srcPythonMQTTCore, srcDesiredData):
    desiredData = None
    try:
        desiredData = "{:.1f}".format((float)(srcEntry.get())) # .1f
        if float(desiredData) >= 100.0:
            print "Cannot set temperature higher than 100 F."
        elif float(desiredData) <= -100.0:
            print "Cannot set temperature lower than -100 F."
        else:
            JSONString = '{"state":{"desired":{"Temp":' + str(desiredData) + '}}}'
            # Update shadow desired state attribute
            srcDesiredData.set(str(desiredData) + " F")
            srcPythonMQTTCore.publish("$aws/things/room/shadow/update", JSONString, 0, False)
            print "Set Temp: " + str(desiredData) + " F"
    except AWSIoTExceptions.publishTimeoutException:
        print "Setting desired data: A Publish Timeout Exception happened."
    except AWSIoTExceptions.publishError:
        print "Setting desired data: A Publish Error happened."
    except ValueError:
        print "Setting desired data: Set Temp value error!"

# Check host
checkHost = True
host = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "h:", ["host="])
    if len(opts) == 0:
        raise getopt.GetoptError("No input parameters")
    for opt, arg in opts:
        if opt in ("-h", "--host"):
            host = arg
except getopt.GetoptError:
    print "usage: python ThermostatSimulatorApp.py -h <host_address>"
    checkHost = False

# Get credentials
rootCA = glob.glob("./certs/*CA.crt")
certificate = glob.glob("./certs/*.pem.crt")
privateKey = glob.glob("./certs/*.pem.key")
credentialCheck = len(rootCA) > 0 and len(certificate) > 0 and len(privateKey) > 0

# Main
setupSuccess = True
if not libraryCheck:
    pass
elif not checkHost:
    pass
elif not credentialCheck:
    print "Missing credentials. Have you put in any credentials in certs/?"
else:
    try:
        # MQTT connection setup
        myLog = logManager.logManager("ThermostatSimulatorApp.py", "./log/") # Enabled by default
        # Switch to enableFileOutput if you need detailed debug info written to a file
        myLog.disableFileOutput()
        # Switch to enableConsolePrint if you need detailed debug info
        # myLog.enableConsolePrint()
        myLog.disableConsolePrint()
        myPythonMQTTCore = mqttCore.mqttCore("ThermostatSimulatorApp", True, mqtt.MQTTv311, myLog)
        myPythonMQTTCore.setConnectDisconnectTimeout(10)
        myPythonMQTTCore.setMQTTOperationTimeout(5)
        myPythonMQTTCore.config(host, 8883, rootCA[0], privateKey[0], certificate[0])
        myPythonMQTTCore.connect()
        # Shadow topic subscription
        myPythonMQTTCore.subscribe("$aws/things/room/shadow/get/accepted", 0, customCallback)
    except AWSIoTExceptions.connectTimeoutException:
        setupSuccess = False
        print "A Connect Timeout Exception happened."
    except AWSIoTExceptions.connectError:
        setupSuccess = False
        print "A Connect Error happened."
    except AWSIoTExceptions.subscribeTimeoutException:
        setupSuccess = False
        print "A Subscribe Timeout Exception happened."
    except AWSIoTExceptions.subscribeError:
        setupSuccess = False
        print "A Subscribe Error happened."
    except SSLError:
        setupSuccess = False
        print "An SSL Error happened. Please check your host address and credentials."
    except Exception as e:
        setupSuccess = False
        print "Unknown Error in setup. Disconnected from WiFi? Wrong host address?"
    finally:
        if not setupSuccess:
            print "Setup failed. Halt."

    if setupSuccess:
        print "Connected."
        print "Generating GUI..."
        # LAYOUT
        root = tk.Tk()
        root.title("ThermostatSimulatorApp")
        root.geometry("500x250")
        root.resizable(width=False, height=False)
        frm = tk.Frame(root)
        # Temp display
        frm_T = tk.Frame(frm)
        frm_T.pack(side="top")
        # Control panel
        frm_B = tk.Frame(frm)
        frm_B.pack(side="bottom")
        frm.pack()
        
        # MODULE
        # frm_T
        reportedData = tk.StringVar()
        reportedData.set("XX.X F")
        #
        myPythonMQTTCore.setUserData(reportedData) # Set the string variable as the private user data in mqttCore
        thread.start_new_thread(getLatestReported, (myPythonMQTTCore,)) # Start a background thread to continuously getting latest reported temp.
        #
        reportedTag = tk.Label(frm_T, text="Reported Temperature:", justify="left")
        reportedLabel = tk.Label(frm_T, textvariable=reportedData, font=("Arial", 55), justify="left")
        
        desiredData = tk.StringVar()
        desiredData.set("XX.X F")
        desiredTag = tk.Label(frm_T, text="Desired Temperature:", justify="left")
        desiredLabel = tk.Label(frm_T, textvariable=desiredData, font=("Arial", 55), justify="left")
        
        reportedTag.pack()
        reportedLabel.pack()
        desiredTag.pack()
        desiredLabel.pack()
        
        # frm_B
        inputTempValEntry = tk.Entry(frm_B)
        inputTempValEntry.pack(side="left")
        setButton = tk.Button(frm_B, text="SET", command=lambda: buttonAction(inputTempValEntry, myPythonMQTTCore, desiredData))
        setButton.pack()
        
        root.mainloop()
        
        
