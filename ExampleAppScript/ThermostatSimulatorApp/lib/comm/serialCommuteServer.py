'''
/*
 * Copyright 2010-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
sys.path.append("../util/")
sys.path.append("../exception/")
import commuteServer
import logManager
import AWSIoTExceptions
import Queue
import signal

class serialCommuteServer(commuteServer.commuteServer):
    _messageQueue = None
    _txBuf = None
    _log = None
    _acceptTimeout = 0 # Never timeout
    _chunkSize = 50 # Biggest chunk of data that can be sent over serial
    _returnList = []

    def __init__(self, srcLogManager):
        self._log = srcLogManager
        self._messageQueue = Queue.Queue(0)
        self._txBuf = ""
        # Register timeout signal handler
        signal.signal(signal.SIGALRM, self._timeoutHandler)
        signal.alarm(0) # disable SIGALRM
        self._log.writeLog("Register timeout signal handler.")
        self._log.writeLog("serialCommuteServer init.")
        

    def _timeoutHandler(self, signal, frame):
        self._log.writeLog("Raise a custom exception for accept timeout.")
        raise AWSIoTExceptions.acceptTimeoutException()

    def _basicInput(self):
        return raw_input()

    def _basicOutput(self, srcContent):
        print(srcContent)

    def setAcceptTimeout(self, srcTimeout):
        self._acceptTimeout = srcTimeout
        self._log.writeLog("serialCommuteServer set accept timeout to " + str(self._acceptTimeout))

    def setChunkSize(self, srcChunkSize):
        self._chunkSize = srcChunkSize
        self._log.writeLog("serialCommuteServer set chunk size to " + str(self._chunkSize))

    def accept(self):
        # Messages are passed from remote client to server line by line
        # A number representing the number of lines to receive will be passed first
        # Then serialCommuteServer should loop the exact time to receive the following lines
        # All these reads add up tp ONE timeout: acceptTimeout. Once exceeded, this timeout will trigger a callback raising an exception
        # Throw acceptTimeoutException, ValueError
        # Store the incoming parameters into an internal data structure
        self._returnList = []
        self._log.writeLog("Clear internal list. Size: " + str(len(self._returnList)))
        signal.alarm(self._acceptTimeout) # Enable SIGALRM
        self._log.writeLog("Accept-timer starts, with acceptTimeout: " + str(self._acceptTimeout) + " second(s).")
        numLines = int(self._basicInput()) # Get number of lines to receive
        self._log.writeLog(str(numLines) + " lines to be received. Loop begins.")
        loopCount = 1
        while(loopCount <= numLines):
            currElementIn = self._basicInput()
            self._returnList.append(currElementIn)
            self._log.writeLog("Received: " + str(loopCount) + "/" + str(numLines) + " Message is: " + currElementIn)
            loopCount += 1
        signal.alarm(0) # Finish reading from remote client, disable SIGALRM
        self._log.writeLog("Finish reading from remote client. Accept-timer ends.")
        return self._returnList

    def writeToInternal(self, srcContent):
        self._messageQueue.put(srcContent)
        self._log.writeLog("Updated serialCommuteServer internal messageQueue by inserting a new message. Size: " + str(self._messageQueue.qsize()))

    def writeToExternal(self):
        # Pick one complete message from the internal messageQueue and write to the remote client in chunks
        # Messages in the internal messageQueue should be well-formated for yield messages, serialCommuteServer will do nothing to format it
        while(not self._messageQueue.empty()):
            currElementOut = self._messageQueue.get()
            self._log.writeLog("Start sending message to remote client: " + currElementOut)
            while(len(currElementOut) != 0):
                self._txBuf = currElementOut[0:self._chunkSize]
                self._basicOutput(self._txBuf)
                self._log.writeLog("Send through serial to remote client. Chunk: " + self._txBuf + " Size: " + str(len(self._txBuf)))
                currElementOut = currElementOut[self._chunkSize:]
            self._log.writeLog("End sending this message.")
        self._log.writeLog("No more messages. Exiting writeToExternal.")
