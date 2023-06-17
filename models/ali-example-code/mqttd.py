#!/usr/bin/python3

# pip install paho-mqtt
import paho.mqtt.client

# =====初始化======
class MQTT():
    def __init__(self,host,CcientID,username=None,password=None,port=1883,timeOut=60):
        self.Host = host
        self.Port = port
        self.timeOut = timeOut
        self.username =username
        self.password = password
        self.CcientID = CcientID

        self.mqttc = paho.mqtt.client.Client(self.CcientID)    #配置ID
        if self.username is not None:    #判断用户名密码是否为空
            self.mqttc.username_pw_set(self.username, self.password)    #不为空则配置账号密码

        self.mqttc.connect(self.Host, self.Port, self.timeOut) #初始化服务器  IP  端口  超时时间


    # 初始化
    def begin(self,message,connect):
        self.mqttc.on_connect = connect
        self.mqttc.on_message = message
        self.mqttc.loop_start()  # 后台新进程循环监听

# =====发送消息==========
    def push(self,tag,date,_Qos = 0):
        self.mqttc.publish(tag,date,_Qos)
        #print('OK',date)

# =======订阅tips=====
    def subscribe(self,_tag):
        self.mqttc.subscribe(_tag)   #监听标签
