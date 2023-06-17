# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import hashlib
import hmac
import random
import json

# 这个就是我们在阿里云注册产品和设备时的三元组啦
# 把我们自己对应的三元组填进去即可
options = {
    'productKey': 'im02gnzJO0e',
    'deviceName': 'raspi-dog',
    'deviceSecret': '3f685d1da7aafda9d3a812b0f946fd3a',
    'regionId': 'cn-shanghai'
}
# 字典

# HOST = options['productKey'] + '.iot-as-mqtt.' + options['regionId'] + '.aliyuncs.com'
HOST = "iot-06z00evt6sb8zbg.mqtt.iothub.aliyuncs.com"
PORT = 1883
PUB_TOPIC = "/sys/" + options['productKey'] + "/" + options['deviceName'] + "/thing/event/property/post"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # client.subscribe("the/topic")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def hmacsha1(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha1).hexdigest()


def getAliyunIoTClient():
    timestamp = str(int(time.time()))
    CLIENT_ID = "paho.py|securemode=3,signmethod=hmacsha1,timestamp=" + timestamp + "|"
    CONTENT_STR_FORMAT = "clientIdpaho.pydeviceName" + options['deviceName'] + "productKey" + options[
        'productKey'] + "timestamp" + timestamp
    # set username/password.
    USER_NAME = options['deviceName'] + "&" + options['productKey']
    PWD = hmacsha1(options['deviceSecret'], CONTENT_STR_FORMAT)
    client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
    client.username_pw_set(USER_NAME, PWD)
    return client

# 建立连接
aliclient = getAliyunIoTClient()
aliclient.on_connect = on_connect
aliclient.on_message = on_message
aliclient.connect(HOST, 1883, 300)

if __name__ == '__main__':
    # aliclient = getAliyunIoTClient()
    # aliclient.on_connect = on_connect
    # aliclient.on_message = on_message
    #
    # aliclient.connect(HOST, 1883, 300)
    ###
    while True:
        payload_json = {
            'id': "2",
            "version": "1.0",
            "sys": {
                "ack": 0
            },
            'params': {
                'singlerecord': {
                    'title': 'onground',  # 随机温度
                    'color': 'green',  # 随机相对湿度
                    'date': '2023-05-10',
                    'timep': '10:57:00',
                }
            },
            'method': "thing.event.property.post"
        }
        print('send data to iot server: ' + str(payload_json))
        aliclient.publish(PUB_TOPIC, payload=str(payload_json), qos=1)
        time.sleep(20)
    ###
    # aliclient.loop_forever()
