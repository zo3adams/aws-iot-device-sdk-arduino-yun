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

 # This class implements the progressive backoff logic for auto-reconnect.
 # It manages the reconnect wait time for the current reconnect, controling
 # when to increase it and when to reset it.

import time
import threading


class progressiveBackoffCore:
    # The base reconnection time in seconds, default 1
    _baseReconnectTimeSecond = 1
    # The maximum reconnection time in seconds, default 32
    _maximumReconnectTimeSecond = 32
    # The minimum time in milliseconds that a connection must be maintained in order to be considered stable
    # Default 20
    _minimumConnectTimeSecond = 20
    # Current backOff time in seconds, init to equal to 0
    # We do not want to backoff on the first attempt to connect
    _currentBackoffTimeSecond = 0
    # Handler for timer
    _resetBackoffTimer = None

    def __init__(self, srcBaseReconnectTimeSecond=1, srcMaximumReconnectTimeSecond=32, srcMinimumConnectTimeSecond=20):
        self._baseReconnectTimeSecond = srcBaseReconnectTimeSecond
        self._maximumReconnectTimeSecond = srcMaximumReconnectTimeSecond
        self._minimumConnectTimeSecond = srcMinimumConnectTimeSecond
        self._currentBackoffTimeSecond = 1

    # For custom progressiveBackoff timing configuration
    def configTime(self, srcBaseReconnectTimeSecond, srcMaximumReconnectTimeSecond, srcMinimumConnectTimeSecond):
        if srcBaseReconnectTimeSecond >= srcMinimumConnectTimeSecond:
            raise ValueError("Min connect time should be bigger than base reconnect time.")
        self._baseReconnectTimeSecond = srcBaseReconnectTimeSecond
        self._maximumReconnectTimeSecond = srcMaximumReconnectTimeSecond
        self._minimumConnectTimeSecond = srcMinimumConnectTimeSecond
        self._currentBackoffTimeSecond = 1

    # Block the reconnect logic for _currentBackoffTimeSecond
    # Update the currentBackoffTimeSecond for the next reconnect
    # Cancel the in-waiting timer for resetting backOff time
    # This should get called only when a disconnect/reconnect happens
    def backOff(self):
        if self._resetBackoffTimer is not None:
            # Cancel the timer
            self._resetBackoffTimer.cancel()
        # Block the reconnect logic
        time.sleep(self._currentBackoffTimeSecond)
        # Update the backoff time
        # r_cur = min(2^n*r_base, r_max)
        self._currentBackoffTimeSecond = min(self._maximumReconnectTimeSecond, self._currentBackoffTimeSecond * 2)

    # Start the timer for resetting _currentBackoffTimeSecond
    # Will be cancelled upon calling backOff
    def startStableConnectionTimer(self):
        self._resetBackoffTimer = threading.Timer(self._minimumConnectTimeSecond, self._connectionStableThenResetBackoffTime)
        self._resetBackoffTimer.start()

    # Timer callback to reset _currentBackoffTimeSecond
    # If the connection is stable for longer than _minimumConnectTimeSecond,
    # reset the currentBackoffTimeSecond to _baseReconnectTimeSecond
    def _connectionStableThenResetBackoffTime(self):
        self._currentBackoffTimeSecond = self._baseReconnectTimeSecond
