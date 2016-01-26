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

#include "aws_iot_mqtt.h"
#include "Arduino.h"
#include "stdio.h"
#include "stdlib.h"
#include "string.h"
#include "ctype.h"

#define LINUX_BAUD_DEFAULT 250000
#define LINUX_BAUD_LININO 115200
#define RETURN_KEY 13 // ASCII code for '\r'
#define NEXTLINE_KEY 10 // ASCII code for '\n'
#define MAX_NUM_PARA 6 // Maximum number of parameters in protocol communication
#define NUM_ATTEMPT_BEFORE_EXIT MAX_NUM_PARA/2+1 // Number of '~' to fully exit the protocol command
const char* OUT_OF_BUFFER_ERR_MSG = "OUT OF BUFFER SIZE";

// Choose different baudrate for different version of openWRT OS
Baud_t aws_iot_mqtt_client::find_baud_type() {
	Baud_t rc_type = BAUD_TYPE_UNKNOWN;
	// 1st attempt
	clearProtocolOnSerialBegin(LINUX_BAUD_DEFAULT);
	exec_cmd("uname\n", true, false); // check OS version
	if(strncmp(rw_buf, "Linux", 5) != 0) { // Not an Arduino?
		clearProtocolOnSerialBegin(LINUX_BAUD_LININO);
		exec_cmd("uname\n", true, false); // check OS version
		if(strncmp(rw_buf, "Linux", 5) != 0) {
			// No more board types to try
		}
		else {rc_type = BAUD_TYPE_LININO;}
	}
	else {rc_type = BAUD_TYPE_ARDUINO;}

	return rc_type;
}

IoT_Error_t aws_iot_mqtt_client::setup_exec(char* client_id, bool clean_session, MQTTv_t MQTT_version) {
	// Serial1 is started before this call
	IoT_Error_t rc = NONE_ERROR;
	exec_cmd("cd /root/AWS-IoT-Python-Runtime/runtime/\n", false, false);
	exec_cmd("python run.py\n", false, false);

	// Create obj
	exec_cmd("4\n", false, false);

	exec_cmd("i\n", false, false);

	sprintf(rw_buf, "%s\n", client_id);
	exec_cmd(rw_buf, false, false);

	int num_temp = clean_session ? 1 : 0;
	sprintf(rw_buf, "%d\n", num_temp);
	exec_cmd(rw_buf, false, false);

	sprintf(rw_buf, "%u\n", MQTT_version);
	exec_cmd(rw_buf, true, false);

	if(strncmp(rw_buf, "I T", 3) != 0) {
		if(strncmp(rw_buf, "I F", 3) == 0) {rc = SET_UP_ERROR;}
		else rc = GENERIC_ERROR;
	}

	return rc;
}

IoT_Error_t aws_iot_mqtt_client::setup(char* client_id, bool clean_session, MQTTv_t MQTT_version) {
	IoT_Error_t rc = NONE_ERROR;
	if(client_id == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(client_id) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	// No input error below this line
	else {
		Baud_t baud_type = find_baud_type(); // Find out baud type
		// Communication failed due to baud rate issue
		if(BAUD_TYPE_UNKNOWN == baud_type) {rc = SERIAL1_COMMUNICATION_ERROR;}
		else {
			rc = setup_exec(client_id, clean_session, MQTT_version);
		}
	}

	return rc;
}

IoT_Error_t aws_iot_mqtt_client::config(char* host, int port, char* cafile_path, char* keyfile_path, char* certfile_path) {
	IoT_Error_t rc = NONE_ERROR;

	if(host != NULL && strlen(host) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else if(cafile_path != NULL && strlen(cafile_path) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else if(keyfile_path != NULL && strlen(keyfile_path) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else if(certfile_path != NULL && strlen(certfile_path) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		const char* helper = "";
		const char* placeholder = "";

		exec_cmd("6\n", false, false);

		exec_cmd("g\n", false, false);

		helper = host == NULL ? placeholder : host;
		sprintf(rw_buf, "%s\n", helper);
		exec_cmd(rw_buf, false, false);

		sprintf(rw_buf, "%d\n", port);
		exec_cmd(rw_buf, false, false);

		helper = cafile_path == NULL ? placeholder : cafile_path;
		sprintf(rw_buf, "%s\n", helper);
		exec_cmd(rw_buf, false, false);

		helper = keyfile_path == NULL ? placeholder : keyfile_path;
		sprintf(rw_buf, "%s\n", helper);
		exec_cmd(rw_buf, false, false);

		helper = certfile_path == NULL ? placeholder : certfile_path;
		sprintf(rw_buf, "%s\n", helper);
		exec_cmd(rw_buf, true, false);

		if(strncmp(rw_buf, "G T", 3) != 0) {
			if(strncmp(rw_buf, "G1F", 3) == 0) {rc = NO_SET_UP_ERROR;}
			else if(strncmp(rw_buf, "G2F", 3) == 0) {rc = WRONG_PARAMETER_ERROR;}
			else if(strncmp(rw_buf, "GFF", 3) == 0) {rc = CONFIG_GENERIC_ERROR;}
			else rc = GENERIC_ERROR;
		}
	}

	return rc;
}

IoT_Error_t aws_iot_mqtt_client::connect(int keepalive_interval) {
	IoT_Error_t rc = NONE_ERROR;
	exec_cmd("2\n", false, false);

	exec_cmd("c\n", false, false);

	sprintf(rw_buf, "%d\n", keepalive_interval);
	exec_cmd(rw_buf, true, false);

	if(strncmp(rw_buf, "C T", 3) != 0) {
		if(strncmp(rw_buf, "C1F", 3) == 0) {rc = NO_SET_UP_ERROR;}
		else if(strncmp(rw_buf, "C2F", 3) == 0) {rc = WRONG_PARAMETER_ERROR;}
		else if(strncmp(rw_buf, "C3F", 3) == 0) {rc = CONNECT_SSL_ERROR;}
		else if(strncmp(rw_buf, "C4F", 3) == 0) {rc = CONNECT_ERROR;}
		else if(strncmp(rw_buf, "C5F", 3) == 0) {rc = CONNECT_TIMEOUT;}
		else if(strncmp(rw_buf, "C6F", 3) == 0) {rc = CONNECT_CREDENTIAL_NOT_FOUND;}
		else if(strncmp(rw_buf, "CFF", 3) == 0) {rc = CONNECT_GENERIC_ERROR;}
		else rc = GENERIC_ERROR;
	}

	return rc;
}

IoT_Error_t aws_iot_mqtt_client::publish(char* topic, char* payload, int payload_len, int qos, bool retain) {
	IoT_Error_t rc = NONE_ERROR;
	if(topic == NULL || payload == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(topic) >= MAX_BUF_SIZE || payload_len >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		exec_cmd("5\n", false, false);

		exec_cmd("p\n", false, false);

		sprintf(rw_buf, "%s\n", topic);
		exec_cmd(rw_buf, false, false);

		sprintf(rw_buf, "%s\n", payload);
		exec_cmd(rw_buf, false, false);

		sprintf(rw_buf, "%d\n", qos);
		exec_cmd(rw_buf, false, false);

		int num_temp = retain ? 1 : 0;
		sprintf(rw_buf, "%d\n", num_temp);
		exec_cmd(rw_buf, true, false);

		if(strncmp(rw_buf, "P T", 3) != 0) {
			if(strncmp(rw_buf, "P1F", 3) == 0) {rc = NO_SET_UP_ERROR;}
			else if(strncmp(rw_buf, "P2F", 3) == 0) {rc = WRONG_PARAMETER_ERROR;}
			else if(strncmp(rw_buf, "P3F", 3) == 0) {rc = PUBLISH_ERROR;}
			else if(strncmp(rw_buf, "P4F", 3) == 0) {rc = PUBLISH_TIMEOUT;}
			else if(strncmp(rw_buf, "PFF", 3) == 0) {rc = PUBLISH_GENERIC_ERROR;}
			else rc = GENERIC_ERROR;
		}
	}
	return rc;
}

IoT_Error_t aws_iot_mqtt_client::subscribe(char* topic, int qos, message_callback cb) {
	IoT_Error_t rc = NONE_ERROR;
	if(topic == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(topic) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		// find unused slots for new subscribe
		int i = find_unused_subgroup();
		if(i < MAX_SUB) {
			exec_cmd("4\n", false, false);

			exec_cmd("s\n", false, false);

			sprintf(rw_buf, "%s\n", topic);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%d\n", qos);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%d\n", i); // ino_id
			exec_cmd(rw_buf, true, false);

			if(strncmp(rw_buf, "S T", 3) == 0) {
				sub_group[i].is_used = true;
				sub_group[i].is_shadow_gud = false;
				sub_group[i].callback = cb;
			}
			else {
				if(strncmp(rw_buf, "S1F", 3) == 0) {rc = NO_SET_UP_ERROR;}
				else if(strncmp(rw_buf, "S2F", 3) == 0) {rc = WRONG_PARAMETER_ERROR;}
				else if(strncmp(rw_buf, "S3F", 3) == 0) {rc = SUBSCRIBE_ERROR;}
				else if(strncmp(rw_buf, "S4F", 3) == 0) {rc = SUBSCRIBE_TIMEOUT;}
				else if(strncmp(rw_buf, "SFF", 3) == 0) {rc = SUBSCRIBE_GENERIC_ERROR;}
				else rc = GENERIC_ERROR;
			}
		}
		else {rc = OUT_OF_SKETCH_SUBSCRIBE_MEMORY;}
	}
	return rc;
}

IoT_Error_t aws_iot_mqtt_client::unsubscribe(char* topic) {
	IoT_Error_t rc = NONE_ERROR;
	if(topic == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(topic) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		exec_cmd("2\n", false, false);

		exec_cmd("u\n", false, false);

		sprintf(rw_buf, "%s\n", topic);
		exec_cmd(rw_buf, true, false);

		// Unsubscribe to a topic never subscribed, ignore
		if(strncmp(rw_buf, "U T", 3) == 0) {rc = NONE_ERROR;}
		else {
			char* saveptr;
			char* p;
			p = strtok_r(rw_buf, " ", &saveptr); // 'U'
			p = strtok_r(NULL, " ", &saveptr); // ino_id
			int ino_id = -1;
			if(p != NULL) {ino_id = is_num(p) ? atoi(p) : -1;}
			if(ino_id >= 0 && ino_id < MAX_SUB) {
				sub_group[ino_id].is_used = false;
				sub_group[ino_id].is_shadow_gud = false;
				sub_group[ino_id].callback = NULL;
			}
			else if(strncmp(rw_buf, "U1F", 3) == 0) {rc = NO_SET_UP_ERROR;}
			else if(strncmp(rw_buf, "U2F", 3) == 0) {rc = WRONG_PARAMETER_ERROR;}
			else if(strncmp(rw_buf, "U3F", 3) == 0) {rc = UNSUBSCRIBE_ERROR;}
			else if(strncmp(rw_buf, "U4F", 3) == 0) {rc = UNSUBSCRIBE_TIMEOUT;}
			else if(strncmp(rw_buf, "UFF", 3) == 0) {rc = UNSUBSCRIBE_GENERIC_ERROR;}
			else rc = GENERIC_ERROR;
		}
	}
	return rc;
}

IoT_Error_t aws_iot_mqtt_client::yield() {
	IoT_Error_t rc = NONE_ERROR;
	exec_cmd("1\n", false, false);
	exec_cmd("z\n", true, false); // tell the python runtime to lock the current msg queue size
	if(strncmp(rw_buf, "Z T", 3) != 0) {rc = YIELD_ERROR;} // broken protocol
	else { // start the BIG yield loop
		while(true) {
			exec_cmd("1\n", false, false);
			exec_cmd("y\n", true, false);
			if(strncmp(rw_buf, "Y F", 3) == 0) {break;}
			if(rw_buf[0] != 'Y') { // filter out garbage feedback
				rc = YIELD_ERROR;
				break;
			}
			// From here, there is a new message chunk in rw_buf
			char* saveptr;
			char* p;
			p = strtok_r(rw_buf, " ", &saveptr); // 'Y'
			p = strtok_r(NULL, " ", &saveptr); // ino_id
			if(p != NULL) {
			  	int ino_id = is_num(p) ? atoi(p) : -1;
			    size_t id_len = strlen(p);
			    p = strtok_r(NULL, " ", &saveptr); // more chunk?
			    if(p != NULL) {
			      	int more = is_num(p) ? atoi(p) : -1;
			      	if(more != 1 && more != 0) { // broken protocol
			      		rc = YIELD_ERROR;
			      		break;
			      	}
			      	else if(ino_id == -1) {
			      		rc = YIELD_ERROR;
			      		break;
			      	}
			      	else {
			      		char* payload = rw_buf + id_len + 5; // step over the protocol and get payload
			      		if(strlen(msg_buf) + strlen(payload) > MAX_BUF_SIZE) {
			      			rc = OVERFLOW_ERROR; // if it is exceeding MAX_BUF_SIZE, return the corresponding error code
			      		}
			      		else {strcat(msg_buf, payload);}
			      		if(more == 0) { // This is the end of this message, do callback and clean up
						    // user callback, watch out for ino_id boundary issue and callback registration
						    if(ino_id >= 0 && ino_id < MAX_SUB && sub_group[ino_id].is_used) {
                                // User callback
                                if(sub_group[ino_id].callback != NULL) {
									if(rc == NONE_ERROR) {
										sub_group[ino_id].callback(msg_buf, (int)strlen(msg_buf));
									}
									if(rc == OVERFLOW_ERROR) {
										sub_group[ino_id].callback((char*)OUT_OF_BUFFER_ERR_MSG, (int)strlen(OUT_OF_BUFFER_ERR_MSG));
									}
								}
								// always free the shadow slot and recover the context
								if(sub_group[ino_id].is_shadow_gud) {
									sub_group[ino_id].is_used = false;
									sub_group[ino_id].is_shadow_gud = false;
									sub_group[ino_id].callback = NULL;
								}
						    }
						    // clean up
						    msg_buf[0] = '\0'; // mark msg_buf as 'unused', ready for the next flush
			      		}
			      		// more to come? do NOTHING to msg_buf and DO NOT call callback
			      	}
			    }
			    else {
			      	rc = YIELD_ERROR;
			      	break;
			    }
			}
			else {
			    rc = YIELD_ERROR;
			    break;
			}
		}
	}
	return rc;
}

IoT_Error_t aws_iot_mqtt_client::disconnect() {
	IoT_Error_t rc = NONE_ERROR;
	exec_cmd("1\n", false, false);

	exec_cmd("d\n", true, false);

	if(strncmp(rw_buf, "D T", 3) != 0) {
		if(strncmp(rw_buf, "D1F", 3) == 0) {rc = NO_SET_UP_ERROR;}
		else if(strncmp(rw_buf, "D2F", 3) == 0) {rc = DISCONNECT_ERROR;}
		else if(strncmp(rw_buf, "D3F", 3) == 0) {rc = DISCONNECT_TIMEOUT;}
		else if(strncmp(rw_buf, "DFF", 3) == 0) {rc = DISCONNECT_GENERIC_ERROR;}
		else rc = GENERIC_ERROR;
	}
	return rc;
}

// DeviceShadow-support API
IoT_Error_t aws_iot_mqtt_client::shadow_init(char* thingName) {
	IoT_Error_t rc = NONE_ERROR;
	if(thingName == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(thingName) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		exec_cmd("3\n", false, false);

		exec_cmd("si\n", false, false);

		sprintf(rw_buf, "%s\n", thingName);
		exec_cmd(rw_buf, false, false);

		exec_cmd("1\n", true, false); // isPersistentSubscribe, always true

		if(strncmp(rw_buf, "SI T", 4) != 0) {
			if(strncmp(rw_buf, "SI F", 4) == 0) {rc = SHADOW_INIT_ERROR;}
			else rc = GENERIC_ERROR;
		}
	}
	return rc;
}

IoT_Error_t aws_iot_mqtt_client::shadow_register_delta_func(char* thingName, message_callback cb) {
	IoT_Error_t rc = NONE_ERROR;
	if(thingName == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(thingName) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		// find unused slots for new subscribe
		int i = find_unused_subgroup();
		if(i < MAX_SUB) {
			exec_cmd("3\n", false, false);

			exec_cmd("s_rd\n", false, false);

			sprintf(rw_buf, "%s\n", thingName);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%d\n", i);
			exec_cmd(rw_buf, true, false);

			if(strncmp(rw_buf, "S_RD T", 6) == 0) {
				sub_group[i].is_used = true;
				sub_group[i].callback = cb;
			}
			else {
				if(strncmp(rw_buf, "S_RD1F", 6) == 0) {rc = NO_SHADOW_INIT_ERROR;}
				else if(strncmp(rw_buf, "S_RD2F", 6) == 0) {rc = WRONG_PARAMETER_ERROR;}
				else if(strncmp(rw_buf, "S_RD3F", 6) == 0) {rc = SUBSCRIBE_ERROR;}
				else if(strncmp(rw_buf, "S_RD4F", 6) == 0) {rc = SUBSCRIBE_TIMEOUT;}
				else if(strncmp(rw_buf, "S_RDFF", 6) == 0) {rc = SHADOW_REGISTER_DELTA_CALLBACK_GENERIC_ERROR;}
				else rc = GENERIC_ERROR;
			}
		}
	}
	return rc;
}

IoT_Error_t aws_iot_mqtt_client::shadow_unregister_delta_func(char* thingName) {
	IoT_Error_t rc = NONE_ERROR;
	if(thingName == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(thingName) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		exec_cmd("2\n", false, false);

		exec_cmd("s_ud\n", false, false);

		sprintf(rw_buf, "%s\n", thingName);
		exec_cmd(rw_buf, true, false);

		// Unsubscribe to a topic never subscribed, ignore
		if(strncmp(rw_buf, "S_UD T", 6) == 0) {rc = NONE_ERROR;}
		else {
			char* saveptr;
			char* p;
			p = strtok_r(rw_buf, " ", &saveptr); // 'S_UD'
			p = strtok_r(NULL, " ", &saveptr); // ino_id
			int ino_id = -1;
			if(p != NULL) {ino_id = is_num(p) ? atoi(p) : -1;}
			if(ino_id >= 0 && ino_id < MAX_SUB) {
				sub_group[ino_id].is_used = false;
				sub_group[ino_id].callback = NULL;
			}
			else if(strncmp(rw_buf, "S_UD1F", 6) == 0) {rc = NO_SHADOW_INIT_ERROR;}
			else if(strncmp(rw_buf, "S_UD2F", 6) == 0) {rc = WRONG_PARAMETER_ERROR;}
			else if(strncmp(rw_buf, "S_UD3F", 6) == 0) {rc = UNSUBSCRIBE_ERROR;}
			else if(strncmp(rw_buf, "S_UD4F", 6) == 0) {rc = UNSUBSCRIBE_TIMEOUT;}
			else if(strncmp(rw_buf, "S_UDFF", 6) == 0) {rc = SHADOW_UNREGISTER_DELTA_CALLBACK_GENERIC_ERROR;}
			else rc = GENERIC_ERROR;
		}
	}
	return rc;
}

IoT_Error_t aws_iot_mqtt_client::shadow_get(char* thingName, message_callback cb, int timeout) {
	IoT_Error_t rc = NONE_ERROR;
	if(thingName == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(thingName) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		// find unused slots for new subscribe
		int i = find_unused_subgroup();	    
		if(i < MAX_SUB) {
			exec_cmd("4\n", false, false);

			exec_cmd("sg\n", false, false);

			sprintf(rw_buf, "%s\n", thingName);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%d\n", i);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%d\n", timeout);
			exec_cmd(rw_buf, true, false);
	        
			if(strncmp(rw_buf, "SG T", 4) == 0) {
				sub_group[i].is_used = true;
				sub_group[i].is_shadow_gud = true;
				sub_group[i].callback = cb;
			}
			else {
				if(strncmp(rw_buf, "SG1F", 4) == 0) {rc = NO_SHADOW_INIT_ERROR;}
				else if(strncmp(rw_buf, "SG2F", 4) == 0) {rc = WRONG_PARAMETER_ERROR;}
				else if(strncmp(rw_buf, "SG3F", 4) == 0) {rc = SUBSCRIBE_ERROR;}
				else if(strncmp(rw_buf, "SG4F", 4) == 0) {rc = SUBSCRIBE_TIMEOUT;}
				else if(strncmp(rw_buf, "SG5F", 4) == 0) {rc = PUBLISH_ERROR;}
				else if(strncmp(rw_buf, "SG6F", 4) == 0) {rc = PUBLISH_TIMEOUT;}
				else if(strncmp(rw_buf, "SGFF", 4) == 0) {rc = SHADOW_GET_GENERIC_ERROR;}
				else rc = GENERIC_ERROR;
			}
		}
		else {rc = OUT_OF_SKETCH_SUBSCRIBE_MEMORY;}
	}
	return rc;
}

IoT_Error_t aws_iot_mqtt_client::shadow_update(char* thingName, char* payload, int payload_len, message_callback cb, int timeout) {
	IoT_Error_t rc = NONE_ERROR;
	if(thingName == NULL || payload == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(thingName) >= MAX_BUF_SIZE || payload_len >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		// find unused slots for new subscribe
		int i = find_unused_subgroup();
		if(i < MAX_SUB) {
			exec_cmd("5\n", false, false);

			exec_cmd("su\n", false, false);

			sprintf(rw_buf, "%s\n", thingName);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%s\n", payload);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%d\n", i);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%d\n", timeout);
			exec_cmd(rw_buf, true, false);

			if(strncmp(rw_buf, "SU T", 4) == 0) {
				sub_group[i].is_used = true;
				sub_group[i].is_shadow_gud = true;
				sub_group[i].callback = cb;
			}
			else {
				if(strncmp(rw_buf, "SU1F", 4) == 0) {rc = NO_SHADOW_INIT_ERROR;}
				else if(strncmp(rw_buf, "SU2F", 4) == 0) {rc = WRONG_PARAMETER_ERROR;}
				else if(strncmp(rw_buf, "SU3F", 4) == 0) {rc = SHADOW_UPDATE_INVALID_JSON_ERROR;}
				else if(strncmp(rw_buf, "SU4F", 4) == 0) {rc = SUBSCRIBE_ERROR;}
				else if(strncmp(rw_buf, "SU5F", 4) == 0) {rc = SUBSCRIBE_TIMEOUT;}
				else if(strncmp(rw_buf, "SU6F", 4) == 0) {rc = PUBLISH_ERROR;}
				else if(strncmp(rw_buf, "SU7F", 4) == 0) {rc = PUBLISH_TIMEOUT;}
				else if(strncmp(rw_buf, "SUFF", 4) == 0) {rc = SHADOW_UPDATE_GENERIC_ERROR;}
				else rc = GENERIC_ERROR;
			}
		}	        
		else {rc = OUT_OF_SKETCH_SUBSCRIBE_MEMORY;}
	}
	return rc;
}

IoT_Error_t aws_iot_mqtt_client::shadow_delete(char* thingName, message_callback cb, int timeout) {
	IoT_Error_t rc = NONE_ERROR;
	if(thingName == NULL) {rc = NULL_VALUE_ERROR;}
	else if(strlen(thingName) >= MAX_BUF_SIZE) {rc = OVERFLOW_ERROR;}
	else {
		// find unused slots for new subscribe
		int i = find_unused_subgroup();
		if(i < MAX_SUB) {
			exec_cmd("4\n", false, false);

			exec_cmd("sd\n", false, false);

			sprintf(rw_buf, "%s\n", thingName);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%d\n", i);
			exec_cmd(rw_buf, false, false);

			sprintf(rw_buf, "%d\n", timeout);
			exec_cmd(rw_buf, true, false);
			if(strncmp(rw_buf, "SD T", 4) == 0) {
				sub_group[i].is_used = true;
				sub_group[i].is_shadow_gud = true;
				sub_group[i].callback = cb;
			}
			else {
				if(strncmp(rw_buf, "SD1F", 4) == 0) {rc = NO_SHADOW_INIT_ERROR;}
				else if(strncmp(rw_buf, "SD2F", 4) == 0) {rc = WRONG_PARAMETER_ERROR;}
				else if(strncmp(rw_buf, "SD3F", 4) == 0) {rc = SUBSCRIBE_ERROR;}
				else if(strncmp(rw_buf, "SD4F", 4) == 0) {rc = SUBSCRIBE_TIMEOUT;}
				else if(strncmp(rw_buf, "SD5F", 4) == 0) {rc = PUBLISH_ERROR;}
				else if(strncmp(rw_buf, "SD6F", 4) == 0) {rc = PUBLISH_TIMEOUT;}
				else if(strncmp(rw_buf, "SDFF", 4) == 0) {rc = SHADOW_DELETE_GENERIC_ERROR;}
				else rc = GENERIC_ERROR;
			}
		}
		else {rc = OUT_OF_SKETCH_SUBSCRIBE_MEMORY;}
	}
	return rc;
}

// Exec command and get feedback into rw_buf
void aws_iot_mqtt_client::exec_cmd(const char* cmd, bool wait, bool single_line) {
	// Write cmd
	int cnt = Serial1.write(cmd) + 1;
	timeout_flag = false;
	int timeout_sec = 0;
	// step1: forget the echo
	while(timeout_sec < CMD_TIME_OUT && cnt != 0) {
		if(Serial1.read() != -1) {cnt--;}
		else { // only start counting the timer when the serial1 is keeping us waiting...
			delay(5); // echo comes faster than python runtime client. Decreasing delay to avoid latency issue
			timeout_sec++;
		}
	}
	timeout_flag = timeout_sec == CMD_TIME_OUT; // Update timeout flag
	int ptr = 0;
	if(!timeout_flag) { // step 1 clear
		timeout_flag = false;
		timeout_sec = 0;
		// step2: waiting
		delay(10);
		if(wait) {
			while(timeout_sec < CMD_TIME_OUT && !Serial1.available()) {
				delay(100); // 0.1 sec
				timeout_sec++;
			}
		}
		timeout_flag = timeout_sec == CMD_TIME_OUT; // Update timeout flag
		if(!timeout_flag) { // step 2 clear
			// read feedback
		    // will read all the available data in Serial1 but only store the message with the limit of MAX_BUF_SIZE
			bool stop_sign = false;
			while(Serial1.available()) {
				int cc = Serial1.read();
				if(cc != -1) {
					if(cc == NEXTLINE_KEY || ptr == MAX_BUF_SIZE - 1) {
						stop_sign = true;
						if(single_line) {break;}
					} // end of feedback
					if(!stop_sign && cc != RETURN_KEY) {
						rw_buf[ptr++] = (char)cc;
					}
				}
			}
		}
	}
	timeout_flag = false; // Clear timeout flag
	rw_buf[ptr] = '\0'; // add terminator in case of garbage data in rw_buf
	// printf("%s\n------\n", rw_buf);
}

int aws_iot_mqtt_client::find_unused_subgroup() {
	int i = 0;
	for(i = 0; i < MAX_SUB; i++) {
		if(!sub_group[i].is_used) {break;}
	}
	return i; // could be MAX_SUB (Not found)
}

void aws_iot_mqtt_client::clearProtocolOnSerialBegin(long baudrate) {
	Serial1.begin(baudrate);
	while(!Serial1);
	exec_cmd("\n", true, false); // jump over the welcoming prompt for Open WRT
	delay(1000); // in case this is the first boot-up
	int i;
	for(i = 0; i < NUM_ATTEMPT_BEFORE_EXIT; i++) {
		// exit the previous python process and jump over the half-baked protocol communication
		exec_cmd("1\n", false, false);
		exec_cmd("~\n", true, false);
	}
	delay(1500); // delay 1500 ms for all related python script to exit
}

bool aws_iot_mqtt_client::is_num(char* src) {
	bool rc = true;
	if(src == NULL) {rc = false;}
	else {
		char* p = src;
		while(*p != '\0') {
			if(*p > '9' || *p < '0') {
				rc = false;
				break;
			}
			p++;
		}
	}
	return rc;
}
