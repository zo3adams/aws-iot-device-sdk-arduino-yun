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

import sys
sys.path.append("./lib/")
sys.path.append("../lib/")
import ssl
import time
import threading
import protocol.paho.client as mqtt
import util.offlinePublishQueue as offlinePublishQueue
from threading import Lock
from exception.AWSIoTExceptions import connectError
from exception.AWSIoTExceptions import connectTimeoutException
from exception.AWSIoTExceptions import disconnectError
from exception.AWSIoTExceptions import disconnectTimeoutException
from exception.AWSIoTExceptions import publishError
from exception.AWSIoTExceptions import publishQueueFullException
from exception.AWSIoTExceptions import subscribeError
from exception.AWSIoTExceptions import subscribeTimeoutException
from exception.AWSIoTExceptions import unsubscribeError
from exception.AWSIoTExceptions import unsubscribeTimeoutException


# Class that holds queued publish request details
class _publishRequest:
    def __init__(self, srcTopic, srcPayload, srcQos, srcRetain):
        self.topic = srcTopic
        self.payload = srcPayload
        self.qos = srcQos
        self.retain = srcRetain


class mqttCore:

    def getClientID(self):
        return self._clientID

    def setConnectDisconnectTimeoutSecond(self, srcConnectDisconnectTimeout):
        self._connectdisconnectTimeout = srcConnectDisconnectTimeout
        self._log.writeLog("Set maximum connect/disconnect timeout to be " + str(self._connectdisconnectTimeout) + " second.")

    def getConnectDisconnectTimeoutSecond(self):
        return self._connectdisconnectTimeout

    def setMQTTOperationTimeoutSecond(self, srcMQTTOperationTimeout):
        self._mqttOperationTimeout = srcMQTTOperationTimeout
        self._log.writeLog("Set maximum MQTT operation timeout to be " + str(self._mqttOperationTimeout) + " second")

    def getMQTTOperationTimeoutSecond(self):
        return self._mqttOperationTimeout

    def setUserData(self, srcUserData):
        self._pahoClient.user_data_set(srcUserData)

    def createPahoClient(self, clientID, cleanSession, userdata, protocol, useWebsocket):
        return mqtt.Client(clientID, cleanSession, userdata, protocol, useWebsocket)  # Throw exception when error happens

    def _doResubscribe(self):
        if self._subscribePool:
            self._resubscribeCount = len(self._subscribePool)
            for key in self._subscribePool.keys():
                qos, callback = self._subscribePool.get(key)
                try:
                    self.subscribe(key, qos, callback)
                    time.sleep(self._drainingIntervalSecond)  # Subscribe requests should also be sent out using the draining interval
                except (subscribeError, subscribeTimeoutException):
                    pass  # Subscribe error resulted from network error, will redo subscription in the next re-connect

    # Performed in a seperate thread, draining the offlinePublishQueue at a given draining rate
    # Publish theses queued messages to Paho
    # Should always pop the queue since Paho has its own queueing and retry logic
    # Should exit immediately when there is an error in republishing queued message
    # Should leave it to the next round of reconnect/resubscribe/republish logic at mqttCore
    def _doPublishDraining(self):
        while True:
            self._offlinePublishQueueLock.acquire()
            # This should be a complete publish requests containing topic, payload, qos, retain information
            # This is the only thread that pops the offlinePublishQueue
            if self._offlinePublishQueue:
                queuedPublishRequest = self._offlinePublishQueue.pop(0)
                # Publish it (call paho API directly)
                (rc, mid) = self._pahoClient.publish(queuedPublishRequest.topic, queuedPublishRequest.payload, queuedPublishRequest.qos, queuedPublishRequest.retain)
                if rc != 0:
                    self._offlinePublishQueueLock.release()
                    break
            else:
                self._drainingComplete = True
                self._offlinePublishQueueLock.release()
                break
            self._offlinePublishQueueLock.release()
            time.sleep(self._drainingIntervalSecond)

    # Callbacks
    def on_connect(self, client, userdata, flags, rc):
        self._disconnectResultCode = sys.maxint
        self._connectResultCode = rc
        if self._connectResultCode == 0:
            processResubscription = threading.Thread(target=self._doResubscribe)
            processResubscription.start()
        # If we do not have any topics to resubscribe to, still start a new thread to process queued publish requests
        if not self._subscribePool:
            offlinePublishQueueDraining = threading.Thread(target=self._doPublishDraining)
            offlinePublishQueueDraining.start()
        self._log.writeLog("Connect result code " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        self._connectResultCode = sys.maxint
        self._disconnectResultCode = rc
        self._drainingComplete = False  # Draining status should be reset when disconnect happens
        self._log.writeLog("Disconnect result code " + str(rc))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        # Execution of this callback is atomic, guaranteed by Paho
        # Check if we have got all SUBACKs for all resubscriptions
        if self._resubscribeCount > 0:
            self._resubscribeCount -= 1
            if self._resubscribeCount == 0:
                # start a thread draining the offline publish queue
                offlinePublishQueueDraining = threading.Thread(target=self._doPublishDraining)
                offlinePublishQueueDraining.start()
                self._resubscribeCount = -1
        self._subscribeSent = True
        self._log.writeLog("Subscribe request " + str(mid) + " sent.")

    def on_unsubscribe(self, client, userdata, mid):
        self._unsubscribeSent = True
        self._log.writeLog("Unsubscribe request sent.")

    def on_message(self, client, userdata, message):
        # Generic message callback
        self._log.writeLog("Received (No custom callback registered) : message: " + str(message.payload) + " from topic: " + str(message.topic))

    ####### API starts here #######
    def __init__(self, clientID, cleanSession, protocol, srcLogManager, srcUseWebsocket=False):
        if clientID is None or cleanSession is None or protocol is None or srcLogManager is None:
            raise TypeError("None type inputs detected.")
        # All internal data member should be unique per mqttCore intance
        # Tool handler
        self._log = srcLogManager
        self._clientID = clientID
        self._pahoClient = self.createPahoClient(clientID, cleanSession, None, protocol, srcUseWebsocket)  # User data is set to None as default
        self._log.writeLog("Paho MQTT Client init.")
        self._pahoClient.on_connect = self.on_connect
        self._pahoClient.on_disconnect = self.on_disconnect
        self._pahoClient.on_message = self.on_message
        self._pahoClient.on_subscribe = self.on_subscribe
        self._pahoClient.on_unsubscribe = self.on_unsubscribe
        self._log.writeLog("Register Paho MQTT Client callbacks.")
        # Tool data structure
        self._connectResultCode = sys.maxint
        self._disconnectResultCode = sys.maxint
        self._subscribeSent = False
        self._unsubscribeSent = False
        self._connectdisconnectTimeout = 0  # Default connect/disconnect timeout set to 0 second
        self._mqttOperationTimeout = 0  # Default MQTT operation timeout set to 0 second
        # Use Websocket
        self._useWebsocket = srcUseWebsocket
        # Subscribe record
        self._subscribePool = dict()
        self._resubscribeCount = -1
        # Broker information
        self._host = ""
        self._port = -1
        self._cafile = ""
        self._key = ""
        self._cert = ""
        # Operation mutex
        self._publishLock = Lock()
        self._subscribeLock = Lock()
        self._unsubscribeLock = Lock()
        # OfflinePublishQueue
        self._offlinePublishQueueLock = Lock()
        self._offlinePublishQueue = offlinePublishQueue.offlinePublishQueue(20, 1)
        # Draining interval in seconds
        self._drainingIntervalSecond = 0.5
        # Is Draining complete
        self._drainingComplete = True
        self._log.writeLog("mqttCore init.")

    def config(self, srcHost, srcPort, srcCAFile, srcKey, srcCert):
        if srcHost is None or srcPort is None or srcCAFile is None or srcKey is None or srcCert is None:
            raise TypeError("None type inputs detected.")
        self._host = srcHost
        self._port = srcPort
        self._cafile = srcCAFile
        self._key = srcKey
        self._cert = srcCert
        self._log.writeLog("Load CAFile, Key, Cert configuration.")

    def setBackoffTime(self, srcBaseReconnectTimeSecond, srcMaximumReconnectTimeSecond, srcMinimumConnectTimeSecond):
        if srcBaseReconnectTimeSecond is None or srcMaximumReconnectTimeSecond is None or srcMinimumConnectTimeSecond is None:
            raise TypeError("None type inputs detected.")
        # Below line could raise ValueError if input params are not properly selected
        self._pahoClient.setBackoffTiming(srcBaseReconnectTimeSecond, srcMaximumReconnectTimeSecond, srcMinimumConnectTimeSecond)
        self._log.writeLog("Custom setting for backoff timing.")

    def setOfflinePublishQueueing(self, srcQueueSize, srcDropBehavior=mqtt.MSG_QUEUEING_DROP_NEWEST):
        if srcQueueSize is None or srcDropBehavior is None:
            raise TypeError("None type inputs detected.")
        self._offlinePublishQueue = offlinePublishQueue.offlinePublishQueue(srcQueueSize, srcDropBehavior)
        self._log.writeLog("Custom setting for publish queueing.")

    def setDrainingIntervalSecond(self, srcDrainingIntervalSecond):
        if srcDrainingIntervalSecond is None:
            raise TypeError("None type inputs detected.")
        if srcDrainingIntervalSecond < 0:
            raise ValueError("Draining interval should not be negative.")
        self._drainingIntervalSecond = srcDrainingIntervalSecond

    # MQTT connection
    def connect(self, keepAliveInterval=60):
        if(keepAliveInterval is None):
            raise TypeError("None type inputs detected.")
        # Return connect succeeded/failed
        ret = False
        # TLS configuration
        if self._useWebsocket:
            self._pahoClient.tls_set(ca_certs=self._cafile, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_SSLv23)
        else:
            self._pahoClient.tls_set(self._cafile, self._cert, self._key, ssl.CERT_REQUIRED, ssl.PROTOCOL_SSLv23)  # Throw exception...
        # Connect
        self._pahoClient.connect(self._host, self._port, keepAliveInterval)  # Throw exception...
        self._pahoClient.loop_start()
        TenmsCount = 0
        while(TenmsCount != self._connectdisconnectTimeout * 100 and self._connectResultCode == sys.maxint):
            TenmsCount += 1
            time.sleep(0.01)
        if(self._connectResultCode == sys.maxint):
            self._log.writeLog("Connect timeout.")
            self._pahoClient.loop_stop()
            raise connectTimeoutException()
        elif(self._connectResultCode == 0):
            ret = True
            self._log.writeLog("Connect time consumption: " + str(float(TenmsCount) * 10) + "ms.")
        else:
            self._log.writeLog("A connect error happened.")
            self._pahoClient.loop_stop()
            raise connectError(self._connectResultCode)
        return ret

    def disconnect(self):
        # Return disconnect succeeded/failed
        ret = False
        # Disconnect
        self._pahoClient.disconnect()  # Throw exception...
        TenmsCount = 0
        while(TenmsCount != self._connectdisconnectTimeout * 100 and self._disconnectResultCode == sys.maxint):
            TenmsCount += 1
            time.sleep(0.01)
        if(self._disconnectResultCode == sys.maxint):
            self._log.writeLog("Disconnect timeout.")
            raise disconnectTimeoutException()
        elif(self._disconnectResultCode == 0):
            ret = True
            self._log.writeLog("Disconnect time consumption: " + str(float(TenmsCount) * 10) + "ms.")
            self._pahoClient.loop_stop()  # Do NOT maintain a background thread for socket communication since it is a successful disconnect
        else:
            self._log.writeLog("A disconnect error happened.")
            raise disconnectError(self._disconnectResultCode)
        return ret

    def publish(self, topic, payload, qos, retain):
        if(topic is None or payload is None or qos is None or retain is None):
            raise TypeError("None type inputs detected.")
        # Return publish succeeded/failed
        ret = False
        # Queueing should happen when disconnected or draining is in progress
        self._offlinePublishQueueLock.acquire()
        queuedPublishCondition = not self._drainingComplete or self._connectResultCode == sys.maxint
        if queuedPublishCondition:
            # Publish to the queue and report error (raise Exception)
            currentQueuedPublishRequest = _publishRequest(topic, payload, qos, retain)
            if not self._offlinePublishQueue.append(currentQueuedPublishRequest):
                self._offlinePublishQueueLock.release()
                raise publishQueueFullException()
            self._offlinePublishQueueLock.release()
        # Publish to Paho
        else:
            self._offlinePublishQueueLock.release()
            self._publishLock.acquire()
            # Publish
            (rc, mid) = self._pahoClient.publish(topic, payload, qos, retain)  # Throw exception...
            self._log.writeLog("Try to put a publish request " + str(mid) + " in the TCP stack.")
            ret = rc == 0
            if(ret):
                self._log.writeLog("Publish request " + str(mid) + " succeeded.")
            else:
                self._log.writeLog("Publish request " + str(mid) + " failed with code: " + str(rc))
                self._publishLock.release()  # Release the lock when exception is raised
                raise publishError(rc)
            self._publishLock.release()
        return ret

    def subscribe(self, topic, qos, callback):
        if(topic is None or qos is None):
            raise TypeError("None type inputs detected.")
        # Return subscribe succeeded/failed
        ret = False
        self._subscribeLock.acquire()
        # Subscribe
        # Register callback
        if(callback is not None):
            self._pahoClient.message_callback_add(topic, callback)
        (rc, mid) = self._pahoClient.subscribe(topic, qos)  # Throw exception...
        self._log.writeLog("Started a subscribe request " + str(mid))
        TenmsCount = 0
        while(TenmsCount != self._mqttOperationTimeout * 100 and not self._subscribeSent):
            TenmsCount += 1
            time.sleep(0.01)
        if(self._subscribeSent):
            ret = rc == 0
            if(ret):
                self._subscribePool[topic] = (qos, callback)
                self._log.writeLog("Subscribe request " + str(mid) + " succeeded. Time consumption: " + str(float(TenmsCount) * 10) + "ms.")
            else:
                if(callback is not None):
                    self._pahoClient.message_callback_remove(topic)
                self._log.writeLog("Subscribe request " + str(mid) + " failed with code: " + str(rc))
                self._log.writeLog("Callback cleaned up.")
                self._subscribeLock.release()  # Release the lock when exception is raised
                raise subscribeError(rc)
        else:
            # Subscribe timeout
            if(callback is not None):
                self._pahoClient.message_callback_remove(topic)
            self._log.writeLog("No feedback detected for subscribe request " + str(mid) + ". Timeout and failed.")
            self._log.writeLog("Callback cleaned up.")
            self._subscribeLock.release()  # Release the lock when exception is raised
            raise subscribeTimeoutException()
        self._subscribeSent = False
        self._log.writeLog("Recover subscribe context for the next request: subscribeSent: " + str(self._subscribeSent))
        self._subscribeLock.release()
        return ret

    def unsubscribe(self, topic):
        if(topic is None):
            raise TypeError("None type inputs detected.")
        # Return unsubscribe succeeded/failed
        ret = False
        self._unsubscribeLock.acquire()
        # Unsubscribe
        (rc, mid) = self._pahoClient.unsubscribe(topic)  # Throw exception...
        self._log.writeLog("Started an unsubscribe request " + str(mid))
        TenmsCount = 0
        while(TenmsCount != self._mqttOperationTimeout * 100 and not self._unsubscribeSent):
            TenmsCount += 1
            time.sleep(0.01)
        if(self._unsubscribeSent):
            ret = rc == 0
            if(ret):
                try:
                    del self._subscribePool[topic]
                except KeyError:
                    pass  # Ignore topics that are never subscribed to
                self._log.writeLog("Unsubscribe request " + str(mid) + " succeeded. Time consumption: " + str(float(TenmsCount) * 10) + "ms.")
                self._pahoClient.message_callback_remove(topic)
                self._log.writeLog("Remove the callback.")
            else:
                self._log.writeLog("Unsubscribe request " + str(mid) + " failed with code: " + str(rc))
                self._unsubscribeLock.release()  # Release the lock when exception is raised
                raise unsubscribeError(rc)
        else:
            # Unsubscribe timeout
            self._log.writeLog("No feedback detected for unsubscribe request " + str(mid) + ". Timeout and failed.")
            self._unsubscribeLock.release()  # Release the lock when exception is raised
            raise unsubscribeTimeoutException()
        self._unsubscribeSent = False
        self._log.writeLog("Recover unsubscribe context for the next request: unsubscribeSent: " + str(self._unsubscribeSent))
        self._unsubscribeLock.release()
        return ret
