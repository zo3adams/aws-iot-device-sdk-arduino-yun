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

# This class implements the offline Publish Queue, with configurable length and drop behaviors.
# This queue will be used as the offline Publish Queue for all message outside Paho as an option
# to publish to when the client is offline.
# DROP_OLDEST: Drop the head of the queue when the size limit is reached.
# DROP_NEWEST: Drop the new incoming elements when the size limit is reached.


class offlinePublishQueue(list):

    _DROPBEHAVIOR_OLDEST = 0
    _DROPBEHAVIOR_NEWEST = 1

    def __init__(self, srcMaximumSize, srcDropBehavior=1):
        if not isinstance(srcMaximumSize, int) or not isinstance(srcDropBehavior, int):
            raise TypeError("MaximumSize/DropBehavior must be integer.")
        if srcMaximumSize < 0:
            raise ValueError('MaximumSize must be greater than or equal to zero.')
        if srcDropBehavior != 0 and srcDropBehavior != 1:
            raise ValueError('Drop behavior not supported.')
        list.__init__([])
        self._dropBehavior = srcDropBehavior
        self._maximumSize = srcMaximumSize

    def _needDropMessages(self):
        isWholeQueueFull = len(self) >= self._maximumSize
        isQueueLimited = self._maximumSize > 0
        # Only if the whole queue is full and the queue section is limited will we need to do the dropping
        return isWholeQueueFull and isQueueLimited

    def setDropBehavior(self, srcDropBehavior):
        if not isinstance(srcDropBehavior, int):
            raise TypeError("Drop behavior must be an integer.")
        if srcDropBehavior != self._DROPBEHAVIOR_NEWEST or srcDropBehavior != self._DROPBEHAVIOR_OLDEST:
            raise ValueError('Drop behavior not supported, must be 0-drop_oldest or 1-drop-newest.')
        self._dropBehavior = srcDropBehavior

    # Override
    # Append to a queue with a limited size.
    # Return True if the append is successful
    # Return False if the queue is full
    def append(self, srcData):
        ret = True
        if self._needDropMessages():
            # We should drop the newest
            if self._dropBehavior == self._DROPBEHAVIOR_NEWEST:
                ret = False
            # We should drop the oldest
            else:
                super(offlinePublishQueue, self).pop(0)
                super(offlinePublishQueue, self).append(srcData)
                ret = False
        else:
            super(offlinePublishQueue, self).append(srcData)
        return ret
