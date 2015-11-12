<h1 align = "center">AWS IoT Arduino Yún SDK</h1>

## What is AWS IoT Arduino Yún SDK

The AWS-IoT-Arduino-Yún-SDK allows developers to connect their Arduino Yún compatible Board to AWS IoT. By connecting the device to the AWS IoT, users can securely work with the message broker, rules and the Thing Shadow provided by AWS IoT and with other AWS services like AWS Lambda, Amazon Kinesis, Amazon S3, etc.

* [Overview](#overview)
* [Installation](#installation)
* [API documentation](#api)
* [Using the SDK](#usingthesdk)  
* [Example](#example)
* [Error code](#errorcode)
* [Support](#support)

****

<a name="overview"></a>
## Overview
This document provides step by step instructions to install the Arduino Yún SDK and connect your device to the AWS IoT.  
The AWS-IoT-Arduino-Yún-SDK consists of two parts, which take use of the resources of the two chips on Arduino Yún, one for native Arduino IDE API access and the other for functionality and connections to the AWS IoT built on top of the [Eclipse Paho](https://eclipse.org/paho/clients/python/) paho-mqtt python package.
### MQTT connection
The AWS-IoT-Arduino-Yún-SDK provides APIs to let users publish messages to AWS IoT and subscribe to MQTT topics to receive messages transmitted by other devices or coming from the broker. This allows to interact with the standard MQTT PubSub functionality of AWS IoT. More information on MQTT protocol is available [here](http://docs.aws.amazon.com/iot/latest/developerguide/protocols.html).
### Thing shadow
The AWS-IoT-Arduino-Yún-SDK also provides APIs to provide access to thing shadows in AWS IoT. Using this SDK, users will be able to sync the data/status of their devices as JSON files to the cloud and respond to change of status requested by other applications. More information on Thing Shadow is available [here](http://docs.aws.amazon.com/iot/latest/developerguide/iot-thing-shadows.html).

****

<a name="installation"></a>
## Installation
### Download AWS-IoT-Arduino-Yún-SDK  
Click [here](https://s3.amazonaws.com/aws-iot-device-sdk-arduino-yun/AWS-IoT-Arduino-Yun-SDK-latest.zip) to download AWS-IoT-Arduino-Yún-SDK zip package and extract it to `AWS-IoT-Arduino-Yun-SDK` on your computer.
### Set up your Arduino Yún Board
Please follow the instructions from official website: [Arduino Yún Guide](https://www.arduino.cc/en/Guide/ArduinoYun).

### Installation on Mac OS/Linux
Before proceeding to the following steps, please make sure that you have `expect` installed on your computer and correctly installed the Arduino IDE.  
To install `expect`:  
For Ubuntu, simply run `sudo apt-get` install `expect`.  
For Mac, `expect` is installed as default.  
For Arduino IDE installation on Linux, please visit [here](http://playground.arduino.cc/Linux/All).

1. Setup the Arduino Yún board and connect it to WiFi. Obtain its IP address and password.  
2. Make sure your computer is connected to the same network (local IP address range).  
3. Download the AWS IoT CA file from [here](https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem).
4. Put your AWS IoT CA file, private key and certificate into `AWS-IoT-Arduino-Yun-SDK/certs`.  
5. Under `AWS-IoT-Arduino-Yun-SDK`, Modify `codebase_upload.sh` and `environment_setup.sh` and replace `[your_boards_IP]` with your board’s IP address and `[your_boards_IP]` with your password (default for Arduino Yún: “arduino”).  
6. Open a terminal, cd to `AWS-IoT-Arduino-Yun-SDK`. Do `chmod 755 codebase_upload.sh` and execute it as `./codebase_upload.sh`.  
	This will upload the python code and keys, CA files and certificates to openWRT running on the more powerful microcontroller on you Arduino Yún board.
7. In the same directory, do `chmod 755 environment_setup.sh` and execute it as `./environment_setup.sh`.  
	This will download and install libraries for openWRT to implement the necessary scripting environment as well as communication protocols.

  Step 7 can take 15-20 minutes for the device to download and install the required packages (distribute, python-openssl, pip, paho-mqtt).  

  NOTE: Do NOT close the terminal before the script finished, otherwise you have to start over with step 6. Make sure you are in your local terminal before repeating step 7.  

8. Copy and paste `AWS-IoT-Arduino-Yun-SDK/AWS-IoT-Arduino-Yun-Library` folder into Arduino libraries that was installed with your Arduino SDK installation. For Mac OS default, it should be under `Documents/Arduino/libraries`.
9. Restart the Arduino IDE if it was running during the installation. You should be able to see the AWS IoT examples in the Examples folder in your IDE. 

### Installation on Windows

Before proceeding to the following steps, please make sure that you have `Putty` and `WinSCP` installed on your PC. If you prefer to use other tools for SSH-ing into your Arduino Yún board and transferring files, you will have to adjust the steps below according to your tools.  
`Putty` can be downloaded from [here](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html).  
`WinSCP` can be downloaded from [here](http://winscp.net/eng/download.php).

1. Setup the Arduino Yún Cloud board and connect it to WiFi. Obtain its IP address and password.  
2. Make sure your PC is connected to the same network (local IP address range).  
3. Download the AWS IoT CA file from [here](https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem).  
4. Put your AWS IoT CA file, private key and certificate into `AWS-IoT-Arduino-Yun-SDK/certs`.  
5. Start WinSCP and upload `AWS-IoT-Arduino-Yun-SDK/certs` folder and `AWS-IoT-Arduino-Yun-SDK/aws_iot_mqtt_client.py` to `/root` on the board.  
6. Use Putty to ssh into OpenWRT on your board and execute the following commands to install the necessary libraries:

		opkg update
		opkg install distribute
		opkg install python-openssl
		easy_install pip
		pip install paho_mqtt
	
  Step 6 can take 15-20 minutes for the device to download and install the required packages.

7. Copy and paste `AWS-IoT-Arduino-Yun-SDK/AWS-IoT-Arduino-Yun-Library` folder into Arduino libraries that was installed with your Arduino SDK installation. For Windows default, it should be under `Documents/Arduino/libraries`.  
8. Restart the Arduino IDE if it was running during the installation. You should be able to see the AWS IoT examples in the Examples folder in your IDE.

****

<a name="api"></a>
## API documentation
Class Name:

	aws_iot_mqtt_client

API:

* MQTT connection  
[IoT\_Error\_t setup(char\* client\_id, bool clean\_session, MQTTv\_t MQTT\_version)](#setup)  
[IoT\_Error\_t config(char\* host, int port, char\* cafile_path, char\* keyfile\_path, char\* certfile\_path)](#config)  
[IoT\_Error\_t connect(int keepalive\_interval)](#connect)  
[IoT\_Error\_t publish(char\* topic, char\* payload, int payload\_len, int qos, bool retain)](#publish)  
[IoT\_Error\_t subscribe(char\* topic, int qos, message\_callback cb)](#subscribe)  
[IoT\_Error\_t unsubscribe(char\* topic)](#unsubscribe)  
[IoT\_Error\_t yield()](#yield)  
[IoT\_Error\_t disconnect()](#disconnect)  
* Thing shadow  
[IoT\_Error\_t shadow\_init(char\* thingName)](#shadow_init)  
[IoT\_Error\_t shadow\_update(char\* thingName, char\* payload, int payload_len, message\_callback cb, int timeout)](#shadow_update)  
[IoT\_Error\_t shadow\_get(char\* thingName, message\_callback cb, int timeout)](#shadow_get)  
[IoT\_Error\_t shadow\_delete(char\* thingName, message\_callback cb, int timeout)](#shadow_delete)  
[IoT\_Error\_t shadow\_register\_delta\_func(char\* thingName, message\_callback cb)](#shadow_register_delta_func)  
[IoT\_Error\_t shadow\_unregister\_delta\_func(char\* thingName)](#shadow_unregister_delta_func)

<a name="setup"></a>
### IoT\_Error\_t setup(char\* client\_id, bool clean\_session, MQTTv\_t MQTT\_version)
**Description**  
Start the Python runtime and set up connection for aws\_iot\_mqtt\_client object. Must be called before any of aws\_iot\_mqtt\_client API is called.

**Syntax**  

	object.setup("myClientID"); // setup a client with client_id set to "myClientID"

**Parameters**  
*client\_id* - The client id for this connection.  
*clean\_session* - Clear the previous connection with this id or not. Default value is true.  
*MQTT\_version* - Version of MQTT protocol for this connection, either MQTTv31 (MQTT version 3.1) or MQTTv311 (MQTT version 3.1.1). Default value is MQTTv311.

**Returns**  
NONE\_ERROR if the setup on openWRT side and connection settings are correct. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if input string exceeds the internal buffer size. SET\_UP\_ERROR if the setup failed.

<a name="config"></a>
### IoT\_Error\_t config(char\* host, int port, char\* cafile\_path, char\* keyfile\_path, char\* certfile_path)
**Description**  
Configure host, port and certs location used to connect to AWS IoT. If the input strings for host, cafile\_path, keyfile\_path and certfile\_path are set to NULL, the default value will be used to connect. Must be called to load user settings right after `aws_iot_mqtt_client::setup` and before connect.

**Syntax**

	object.config("example.awsamazon.com", 1234, "./cafile", "./keyfile", "./certfile");
	
**Parameters**  
*host* - The endpoint to connect to. Must be a NULL-terminated string.  
*port* - The port number to connect to.  
*cafile_path* - The path of CA file on OpenWRT. Must be a NULL-terminated string.  
*keyfile_path* - The path of private key file on OpenWRT. Must be a NULL-terminated string.  
*certfile_path* - The path of certificate file on OpenWRT. Must be a NULL-terminated string.

**Returns**  
NONE\_ERROR if the configuration is successful. CONFIG\_ERROR if the configuration failed.

<a name="connect"></a>
### IoT\_Error\_t connect(int keepalive\_interval)
**Description**  
Connect to AWS IoT, using user-specific keepalive setting.

**Syntax**
	
	object.connect(); // connect to AWS IoT with default keepalive set to 60 seconds
	object.connect(55); // connect to AWS IoT with keepalive set to 55 seconds
	
**Parameters**  
*keepalive\_interval* - amount of time for MQTT ping request interval, in seconds. Default is set to 60 seconds.

**Returns**  
NONE\_ERROR if the connect is successful. CONNECT_ERROR if the connection failed.

<a name="publish"></a>
### IoT\_Error\_t publish(char\* topic, char\* payload, int payload\_len, int qos, bool retain)
**Description**  
Publish a new message to the desired topic with qos and retain flag settings using MQTT protocol

**Syntax**

    object.publish("myTopic", "myMessage", strlen("myMessage"), 0, false); // publish "myMessage" to topic "myTopic" in QoS 0 with retain flag set to false

**Parameters**  
*topic* - Topic name to publish to. Must be a NULL-terminated string.  
*payload* - Payload to publish.  
*payload_len* - Length of payload.  
*qos* - Qualiy of service, could be 0 or 1.  
*retain* - retain flag.

**Returns**  
NONE\_ERROR if the publish is successful. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if topic/payload exceeds the internal buffer size. PUBLISH_ERROR if the publish failed.

<a name="subscribe"></a>
### IoT\_Error\_t subscribe(char\* topic, int qos, message_callback cb)
**Description**  
Subscribe to the desired topic and register a callback for new messages from this topic. 

**Syntax**

    object.subscribe("myTopic", 0, myCallbackFunc); // subscribe to topic "myTopic" in QoS 0 and register its callback function as myCallbackFunc

**Parameters**  
*topic* - The topic to subscribe to. Must be a NULL-terminated string.  
*qos* - Quality of service, could be 0 or 1.  
*cb* - Function pointer to user-specific callback function to call when a new message comes in for the subscribed topic. The callback function should have a parameter list of (char*, int) to store the incoming message content and the length of the message.

**Returns**  
NONE\_ERROR if the subscribe is successful. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if topic/payload exceeds the internal buffer size. OUT\_OF\_SKETCH\_SUBSCRIBE\_MEMORY if the number of current subscribe exceeds the configured number in aws\_iot\_config\_SDK.h. SUBSCRIBE\_ERROR if the subscribe failed.

<a name="unsubscribe"></a>
### IoT\_Error\_t unsubscribe(char\* topic)
**Description**  
Unsubscribe to the desired topic.

**Syntax**

    object.unsubscribe("myTopic");

**Parameters**  
*topic* - The topic to unsubscribe to. Must be a NULL-terminated string.

**Returns**  
NONE\_ERROR if the unsubscribe is successful. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if topic/payload exceeds the internal buffer size. UNSUBSCRIBE\_ERROR if the unsubscribe failed.

<a name="yield"></a>
### IoT\_Error\_t yield()
**Description**  
Called in the loop to check if there is a new message from all subscribed topics, as well as thing shadow topics. Registered callback functions will be called according to the sequence of messages if there is any. Specifically, unnecessary shadow thing topics (accepted/rejected) will be unsubscribed according to the incoming new messages to free subscribe slots. Users should call this function frequently to receive new messsages and free subscribe slots for new subscribes, especially for shadow thing requests.
 
**Syntax**

    object.yield();

**Parameters**  
None

**Returns**  
NONE\_ERROR if the yield is successful, whether there is a new message or not. OVERFLOW\_ERROR if the new message exceeds the internal buffer size. YIELD\_ERROR if the yield failed.

<a name="disconnect"></a>
### IoT\_Error\_t disconnect()
**Description**  
Disconnect from AWS IoT.

**Syntax**

	object.disconnect();
	
**Parameters**  
None

**Returns**  
NONE\_ERROR if disconnect is successful. DISCONNECT\_ERROR if the disconnect failed.

<a name="shadow_init"></a>
### IoT\_Error\_t shadow\_init(char\* thingName)
**Description**  
Initialize thing shadow configuration. Should be called before any of the thing shadow API.

**Syntax**

	object.shadow_init("NewThingName"); // Init thing shadow configuration and set thing name for current device to "NewThingName"

**Parameters**  
*thingName* - Thing name for this device. Must be a NULL-terminated string.

**Returns**  
NONE\_ERROR if thing shadow is successfully initialized. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if thing name exceeds the internal buffer size. SHADOW\_INIT\_ERROR if thing shadow initialization failed. 

<a name="shadow_update"></a>
### IoT\_Error\_t shadow\_update(char\* thingName, char* payload, int payload_len, message\_callback cb, int timeout)
**Description**  
Update the thing shadow data in the cloud by publishing a new JSON file onto the corresponding thing shadow topic and subscribing accepted/rejected thing shadow topics to get feedback of whether it is a successful/failed request. Timeout can be set in seconds as the maximum waiting time for feedback. Once the request gets timeout, a timeout message will be received. The registered callback function will be called whenever there is an accepted/rejected/timeout feedback. After the feedback comes in, it will automatically unsubscribe accepted/rejected shadow topics. Frequent subscribe/unsubscribe can be slow. If no feedback is needed, users can set callback function to NULL to do a simple shadow update without subscribe/unsubscribe at a higher rate.

**Syntax**

	object.shadow_update("UserThingName", JSON_FILE, strlen(JSON_FILE), UserCallbackFunction, 5); // update the data of "UserThingName" thing shadow in the cloud to JSON_FILE, with a timeout of 5 seconds and UserCallbackFunction as the callback function
	object.shadow_update("UserThingName", JSON_FILE, strlen(JSON_FILE), NULL, 5); // Perform a simple shadow update regardless of feedback, this is for high rate updating

**Parameters**  
*thingName* - The name of the thing shadow in the cloud. Must be a NULL-terminated string.  
*payload* - The data that needs to be updated into the cloud, in JSON file format.  
*payload_len* - Length of payload  
*cb* - Function pointer to user-specific callback function to call when a new message comes in for the subscribed topic. The callback function should have a parameter list of (char\*, int) to store the incoming message content and the length of the message.  
*timeout* - The maximum time to wait for feedback.  


**Returns**  
NONE\_ERROR if the shadow update request succeeds. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if thing name/payload exceeds the internal buffer size. OUT\_OF\_SKETCH\_SUBSCRIBE\_MEMORY if the number of current subscribe exceeds the configured number in aws\_iot\_config\_SDK.h. SHADOW\_UPDATE\_ERROR if the shadow update request failed. 

<a name="shadow_get"></a>
### IoT\_Error\_t shadow\_get(char\* thingName, message\_callback cb, int timeout)
**Description**  
Obtain the thing shadow data in the cloud by publishing an empty JSON file onto the corresponding thing shadow topic and subscribing accepted/rejected thing shadow topics to get feedback of whether it is a successful/failed request. Timeout can be set in seconds as the maximum waiting time for feedback. Once the request gets timeout, a timeout message will be received. The registered callback function will be called whenever there is an accepted/rejected/timeout feedback. After the feedback comes in, it will automatically unsubscribe accepted/rejected shadow topics. Thing shadow data will be available as a JSON file in the callback.

**Syntax**  

	object.shadow_get("UserThingName", UserCallbackFunction, 5); // get the data of the thing shadow "UserThingName", with a timeout of 5 seconds and UserCallbackFunction as the callback function

**Parameters**  
*thingName* - The name of the thing shadow in the cloud. Must be a NULL-terminated string.  
*cb* - Function pointer to user-specific callback function to call when a new message comes in for the subscribed topic. The callback function should have a parameter list of (char\*, int) to store the incoming message content and the length of the message.  
*timeout* - The maximum time to wait for feedback.  

**Returns**  
NONE\_ERROR if the shadow get request succeeds. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if thing name exceeds the internal buffer size. OUT\_OF\_SKETCH\_SUBSCRIBE\_MEMORY if the number of current subscribe exceeds the configured number in aws\_iot\_config\_SDK.h. SHADOW\_GET\_ERROR if the shadow get request failed.

<a name="shadow_delete"></a>
### IoT\_Error\_t shadow\_delete(char\* thingName, message\_callback cb, int timeout)
**Description**  
Delete the thing shadow data in the cloud by publishing an empty JSON file onto the corresponding thing shadow topic and subscribing accepted/rejected thing shadow topics to get feedback of whether it is a successful/failed request. Timeout can be set in seconds as the maximum waiting time for feedback. Once the request gets timeout, a timeout message will be received. The registered callback function will be called whenever there is an accepted/rejected/timeout feedback. After the feedback comes in, it will automatically unsubscribe accepted/rejected shadow topics. 

**Syntax**  

	object.shadow_delete("UserThingName", UserCallbackFunction, 5); // delete the data of the thing shadow "UserThingName", with a timeout of 5 seconds and UserCallbackFunction as the callback function

**Parameters**  
*thingName* - The name of the thing shadow in the cloud. Must be a NULL-terminated string.  
*cb* - Function pointer to user-specific callback function to call when a new message comes in for the subscribed topic. The callback function should have a parameter list of (char\*, int) to store the incoming message content and the length of the message.  
*timeout* - The maximum time to wait for feedback.  

**Returns**  
NONE\_ERROR if the shadow delete request succeeds. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if thing name exceeds the internal buffer size. OUT\_OF\_SKETCH\_SUBSCRIBE\_MEMORY if the number of current subscribe exceeds the configured number in aws\_iot\_config\_SDK.h. SHADOW\_DELETE\_ERROR if the shadow delete request failed.

<a name="shadow_register_delta_func"></a>
### IoT\_Error\_t shadow\_register\_delta\_func(char\* thingName, message\_callback cb)
**Description**  
Subscribe to the delta topic of the corresponding thing shadow with the given name and register a callback. Whenever there is a difference between the desired and reported state data, the registered callback will be called and the feedback/message will be available in the callback.

**Syntax**

	object.shadow_register_delta_func("UserThingName", UserCallBackFunction); // register UserCallbackFunction as the  delta callback function for the thing shadow "UserThingName"

**Parameters**  
*thingName* - The name of the thing shadow in the cloud. Must be a NULL-terminated string.  
*cb* - Function pointer to user-specific callback function to call when a new message comes in for the subscribed topic. The callback function should have a parameter list of (char\*, int) to store the incoming message content and the length of the message.

**Return**  
NONE\_ERROR if the shadow delta topic is successfully subscribed and the callback function is successfully registered. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if thing name exceeds the internal buffer size. OUT\_OF\_SKETCH\_SUBSCRIBE\_MEMORY if the number of current subscribe exceeds the configured number in aws\_iot\_config\_SDK.h. SUBSCRIBE\_ERROR if the delta topic subscribe failed.

<a name="shadow_unregister_delta_func"></a>
### IoT\_Error\_t shadow\_unregister\_delta\_func(char\* thingName)
**Description**  
Unsubscribe to the delta topic of the corresponding thing shadow with the given name and unregister the callback. There will be no message coming after this API call if another difference occurs between the desired and reported state data for this thing shadow.

**Syntax**

	object.shadow_unregister_delta_func("UserThingName"); // unregister the delta topic of the thing shadow "UserThingName"

**Parameters**  
*thingName* - The name of the thing shadow in the cloud. Must be a NULL-terminated string.

**Returns**  
NONE\_ERROR if the shadow delta topic is successfully unsubscribed and the callback function is successfully unregistered. NULL\_VALUE\_ERROR if input parameters have NULL value. OVERFLOW\_ERROR if thing name exceeds the internal buffer size. UNSUBSCRIBE\_ERROR if the delta topic unsubscribe failed.

****

<a name="usingthesdk"></a>
## Using the SDK
**Make sure you have properly installed the AWS-IoT-Arduino-Yún-SDK and setup the board.**

<a name="slowstartup"></a>
**Make sure to start the sketch after openWRT is ready and gets connected to WiFi. It takes about 80-90 seconds for Arduino Yún board to start the openWRT and get connected to WiFi for each power cycle.**

**Make sure you have properly configured SDK settings in `aws_iot_config.h` inside each sketch directory:**

	//===============================================================
	#define AWS_IOT_MQTT_HOST "data.iot.us-east-1.amazonaws.com" 	// your endpoint
	#define AWS_IOT_MQTT_PORT 8883									// your port
	#define AWS_IOT_CLIENT_ID	"My_ClientID"						// your client ID
	#define AWS_IOT_MY_THING_NAME "My_Board"						// your thing name
	#define AWS_IOT_ROOT_CA_FILENAME "aws-iot-rootCA.crt"           // your root-CA filename
	#define AWS_IOT_CERTIFICATE_FILENAME "cert.pem"                 // your certificate filename
	#define AWS_IOT_PRIVATE_KEY_FILENAME "privkey.pem"              // your private key filename
	//===============================================================

**These settings can be downloaded from the AWS IoT console after you created a device and licked on "Connect a device".**  	

**Make sure you have included the AWS-IoT-Arduino-Yún-SDK library:**

    #include <aws_iot_mqtt.h>
    

**Make sure you have included your configuration header file:**

	#include "aws_iot_config.h"

**Make sure you have enough memory for subscribe, messages and sketch runtime. Internal buffer size is defined in SDK library source directory `libraries/AWS-IoT-Arduino-Yun-Library/aws_iot_config_SDK.h`. The following are default settings:**

	#define MAX_BUF_SIZE 256										// maximum number of bytes to publish/receive
	#define MAX_SUB 15 												// maximum number of subscribe
	#define CMD_TIME_OUT 100										// maximum time to wait for feedback from AR9331, 100 = 10 sec
	#define MAX_SHADOW_TOPIC_LEN 64                                 // maximum length in bytes for shadow topic, the metadata length for shadow topic is 32, make sure your thing name length plus that does not exceed this limit

**Make sure you setup the client, configure it using your configuration and connect it to AWS IoT first. Remember to use certs path macros for configuration:**

    aws_iot_mqtt_client myClient;
    myClient.setup(AWS_IOT_CLIENT_ID);
    myClient.config(AWS_IOT_MQTT_HOST, AWS_IOT_MQTT_PORT, AWS_IOT_ROOT_CA_PATH, AWS_IOT_PRIVATE_KEY_PATH, AWS_IOT_CERTIFICATE_PATH);
    myClient.connnect();

**Remember to check incoming messages in a loop**:

    void loop() { 
      ...  
      myClient.yield();
      ...
    }

**When you are using thing shadow API, make sure you initialize the shadow with your device thing name first:**

	myClient.shadow_init(AWS_IOT_MY_THING_NAME);

**When you are using thing shadow API, always make sure MAX\_SUB is big enough for a thing shadow request in the loop:**

	...
	myClient.shadow_get("myThingName", myCallback, 5); // need 2 in MAX_SUB
	...
	void loop() {
		...
		myClient.shadow_get("myThingName", myCallback, 5); // need 4 in MAX_SUB
		myClient.yield(); // unsubscribe thing shadow topics when necessary
		...
	}

**When you are using thing shadow API, make sure you set the timeout to a proper value and frequently call yield to free subscribe resources. Long timeout with low rate of yielding and high rate of shadow request will result in exhaustion of subscribe resources:**

	void loop() {
		...
		myClient.shadow_get("myThingName", myCallback, 5); // 5 sec timeout is fine for a request per 5 sec
		
		// myClient.shadow_get("myThingName", myCallback, 50);
		// 50 sec timeout is too long. When missing feedback happens frequently, with a rate of 1 request per 5 sec, subscribed topics will soon accumulate and exceed MAX_SUB before any of the previously-subscribed topic gets timeout and unsubscribed
		
		myClient.yield();
		
		delay(5000); // 5 sec delay
		...
	}

**Enjoy the Internet of Things!**

****

<a name="example"></a>
## Example
### BasicPubSub
This [example](https://github.com/aws/aws-iot-device-sdk-arduino-yun/tree/master/AWS-IoT-Arduino-Yun-Library/examples/BasicPubSub) demonstrates a simple MQTT publish/subscribe using AWS IoT from Arduino Yún board. It first subscribes to a topic once and registers a callback to print out new messages to Serial monitor and then publishes to the topic in a loop. Whenever it receives a new message, it will be printed out to Serial monitor indicating the callback function has been called.

* **Hardware Required**  
Arduino Yún  
Computer connected with Arduino Yún using USB serial

* **Software Required**  
None

* **Circuit Required**  
None

* **Attention**  
Please make sure to start the example sketch after the board is fully set up and openWRT is up and connected to WiFi. See [here](#slowstartup).

* **Code**  
	Create an instance of aws\_iot\_mqtt\_client. 

		aws_iot_mqtt_client myClient;
		
	In `setup()`, open the Serial. Set the instance up and connect it to the AWS IoT.

		Serial.begin(115200);
		...
 		if((rc = myClient.setup(AWS_IOT_CLIENT_ID)) == 0) {
    		// Load user configuration
    		if((rc = myClient.config(AWS_IOT_MQTT_HOST, AWS_IOT_MQTT_PORT, AWS_IOT_ROOT_CA_PATH, AWS_IOT_PRIVATE_KEY_PATH, AWS_IOT_CERTIFICATE_PATH)) == 0) {
      			// Use default connect: 60 sec for keepalive
      			if((rc = myClient.connect()) == 0) {
        			success_connect = true;
        			...
        		}
        		else {...}
        	}
        	else {...}
        }
        else {...}
        ...
          		
  	In `setup()`, subscribe to the desired topic and wait for some delay time.
  	
  	  	if((rc = myClient.subscribe("topic1", 1, msg_callback)) != 0) {
    		Serial.println("Subscribe failed!");
    		Serial.println(rc);
    	}
    	delay(2000);
    	
  	In `loop()`, publish to this topic and call yield function to receive the message every 5 seconds.
  	
  		sprintf(msg, "new message %d", cnt);
  		if((rc = myClient.publish("topic1", msg, strlen(msg), 1, false)) != 0) {
  			Serial.println("Publish failed!");
  			Serial.println(rc);
  		}
		if((rc = myClient.yield()) != 0) {
			Serial.println("Yield failed!");
			Serial.println(rc);
		}
		...
		delay(5000);
		
	The full sketch can be found in `AWS-IoT-Arduino-Yun-Library/examples/BasicPubSub`.

### ThingShadowEcho sample app
This [example](https://github.com/aws/aws-iot-device-sdk-arduino-yun/tree/master/AWS-IoT-Arduino-Yun-Library/examples/ThingShadowEcho) demonstrates Arduino Yún board as a device communicating with AWS IoT, syncing data into the thing shadow in the cloud and receiving commands from an app. Whenever there is a new command from the app side to change the desired state of the device, the board will receive this request and apply the change by publishing it as the reported state. By registering a delta callback function, users will be able to see this incoming message and notice the syncing of the state.  

* **Hardware Required**  
Arduino Yún  
Computer connected with Arduino Yún using USB serial

* **Software Required**  
App-side code that updates the state of the corresponding thing shadow in the cloud
*Note:* You can also use [AWS IoT console](https://aws.amazon.com/iot/) to update the shadow data.

* **Circuit Required**  
None

* **Attention**  
Please make sure to start the example sketch after the board is fully set up and openWRT is up and connected to WiFi. See [here](#slowstartup).

* **Code**  
	Create an instance of aws\_iot\_mqtt\_client. 

		aws_iot_mqtt_client myClient;
		
	Create logging function for execution tracking.
	
		bool print_log(char* src, int len) {
			...
		}
	
	In `setup()`, open the Serial. Set the instance up and connect it to the AWS IoT. Init the shadow and register a delta callback function. All steps are tracked using logging function.
	
		if(print_log("setup", myClient.setup(AWS_IOT_CLIENT_ID))) {
			if(print_log("config", myClient.config(AWS_IOT_MQTT_HOST, AWS_IOT_MQTT_PORT, AWS_IOT_ROOT_CA_PATH, AWS_IOT_PRIVATE_KEY_PATH, AWS_IOT_CERTIFICATE_PATH))) {
				if(print_log("connect", myClient.connect())) {
        			success_connect = true;
        			print_log("shadow init", myClient.shadow_init(AWS_IOT_MY_THING_NAME));
        			print_log("register thing shadow delta function", myClient.shadow_register_delta_func(AWS_IOT_MY_THING_NAME, msg_callback_delta));
      			}
    		}
  		}
  		  		
  	In `loop()`, yield to check and receive new incoming messages every 1 second.
  	
  		if(myClient.yield()) {
  			Serial.println("Yield failed.");
  		}
  		delay(1000);
  		
  	For delta callback function, simply parse out the desired state and put it as the reported state in the JSON file that needs to be updated.
  	
  		void msg_callback_delta(char* src, int len) {
  			String data = String(src);
  			int st = data.indexOf("\"state\":") + strlen("\"state\":");
  			int ed = data.indexOf(",\"metadata\":");
  			String delta = data.substring(st, ed);
  			String payload = "{\"state\":{\"reported\":";
  			payload += delta;
  			payload += "}}";
  			payload.toCharArray(JSON_buf, 100);
  			print_log("update thing shadow", myClient.shadow_update(AWS_IOT_MY_THING_NAME, JSON_buf, strlen(JSON_buf), NULL, 5));
  		}
  	
  	Once an update of the desired state for this device is received, a delta message will be received and displayed in the Serial monitor. The device will update this data into the cloud.  
  	
	The full sketch can be found in `AWS-IoT-Arduino-Yun-Library/examples/ThingShadowEcho`.
	
<a name="errorcode"></a>
## Error code
The following error codes are defined in `AWS-IoT-Arduino-Yun-Library/aws_iot_error.h`:  

	typedef enum {
		NONE_ERROR = 0,
		GENERIC_ERROR = -1,
		NULL_VALUE_ERROR = -2,
		OVERFLOW_ERROR = -3,
		SET_UP_ERROR = -4,
		CONNECT_ERROR = -5,
		PUBLISH_ERROR = -6,
		SUBSCRIBE_ERROR = -7,
		UNSUBSCRIBE_ERROR = -8,
		YIELD_ERROR = -9,
		DISCONNECT_ERROR = -10,
		SHADOW_INIT_ERROR = -11,
		SHADOW_UPDATE_ERROR = -12,
		SHADOW_GET_ERROR = -13,
		SHADOW_DELETE_ERROR = -14,
		CONFIG_ERROR = -15,
		OUT_OF_SKETCH_SUBSCRIBE_MEMORY = -16,
		SERIAL1_COMMUNICATION_ERROR = -17
	} IoT_Error_t;
	
<a name="support"></a>
## Support
If you have technical questions about AWS IoT Device SDK, please use [AWS IoT forum](https://forums.aws.amazon.com/forum.jspa?forumID=210).  
For any other questions on AWS IoT, please contact [AWS Support](https://aws.amazon.com/contact-us/).
