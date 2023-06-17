import sys
from linkkit import linkkit
import logging

"""
一.网关上线说明
网关需要先上线，才能对子设备进行操作。具体步骤如下：
1.在linkkit.LinkKit的构造参数中填入网关的三元组
2.调用linkkit.Linkkit()连云，结果在on_connect回调中透出. 若成功，rc=0
3.本demo演示的物模型功能是针对网关的。针对子设备的物模型功能暂未开发

二.子设备上线和收发消息说明
网关需要添加子设备的topo关系后，才能对子设备进行login（上线），之后才能收发消息。具体步骤如下：
1.在demo_get_subdev_list函数中，通过数组方式，添加子设备的三元组.
2.网关连云成功后(比如在on_connect中), 执行self.__linkkit.gateway_add_subdev_topo，将子设备的topo关系添加到网关中.注：单次添加topo关系的子设备数量不能超过30个，否则服务端会报错.
3.添加子设备topo关系的结果会在on_gateway_add_subdev_topo_reply这个回调中透出。若成功，用户需要在其中调用self.__linkkit.gateway_login_subdev进行子设备login的操作.注：单次添加topo关系的子设备数量不能超过50个，否则服务端会报错.
4.子设备login的结果会在on_gateway_login_subdev_reply这个回调中透出。若成功，用户就能对子设备进行消息的收发的操作。子设备上行消息，请参考on_gateway_login_subdev_reply这个回调中参考实现。子设备的下行的消息，都在on_topic_message这个回调中透出。具体操作请参考user_loop中的步骤"2"/"3"
5.topo关系保存在服务端。如果子设备的topo关系之前被添加过，而且并没有删除，下次子设备上线时可以跳过gateway_add_subdev_topo这个步骤，直接走到gateway_login_subdev

三.子设备下线操作说明
1.网关调用self.__linkkit.gateway_logout_subdev可以对子设备进行下线操作
2.子设备下线后，可以调用self.__linkkit.gateway_delete_subdev_topo将其topo关系删除(可选）
3.单次gateway_logout_subdev子设备的最大数量是50，单次gateway_delete_subdev_topo关系的最大子设备数量是30
4.具体操作请参考user_loop中的步骤"4"/"5"

四.子设备动态注册说明
1.子设备的deviceSecrete如果还没有获取到，需要先通过self.__linkkit.gateway_product_register_subdev或者self.__linkkit.gateway_register_subdev进行动态注册
2.秘钥获取到之后，才能参照"二.子设备上线和收发消息说明"对子设备进行操作
3.具体操作请参考user_loop中的步骤"1"
"""

# config log
__log_format = '%(asctime)s-%(process)d-%(thread)d - %(name)s:%(module)s:%(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(format=__log_format)

class CustomerThing(object):
    def __init__(self):
        self.__linkkit = linkkit.LinkKit(
            host_name="cn-shanghai",
            product_key="{YourGatewayProductKey}",
            device_name="{YourGatewayDeviceName}",
            device_secret="{YourGatewayDeviceSecret}")
        #企业版实例和新版公共实例的用户,需要打开下句中的#注释符号，在endpoint字段中填写该实例的接入点
        #self.__linkkit.config_mqtt(endpoint="iot-xxxxx.mqtt.iothub.aliyuncs.com")
        self.__linkkit.enable_logger(logging.DEBUG)
        self.__linkkit.on_device_dynamic_register = self.on_device_dynamic_register
        self.__linkkit.on_connect = self.on_connect
        self.__linkkit.on_disconnect = self.on_disconnect
        self.__linkkit.on_topic_message = self.on_topic_message
        self.__linkkit.on_subscribe_topic = self.on_subscribe_topic
        self.__linkkit.on_unsubscribe_topic = self.on_unsubscribe_topic
        self.__linkkit.on_publish_topic = self.on_publish_topic
        self.__linkkit.on_thing_enable = self.on_thing_enable
        self.__linkkit.on_thing_disable = self.on_thing_disable
        self.__linkkit.on_thing_event_post = self.on_thing_event_post
        self.__linkkit.on_thing_prop_post = self.on_thing_prop_post
        self.__linkkit.on_thing_prop_changed = self.on_thing_prop_changed
        self.__linkkit.on_thing_call_service = self.on_thing_call_service
        self.__linkkit.on_thing_raw_data_post = self.on_thing_raw_data_post
        self.__linkkit.on_thing_raw_data_arrived = self.on_thing_raw_data_arrived
        self.__linkkit.on_gateway_add_subdev_topo_reply = self.on_gateway_add_subdev_topo_reply
        self.__linkkit.on_gateway_delete_subdev_topo_reply = self.on_gateway_delete_subdev_topo_reply
        self.__linkkit.on_gateway_login_subdev_reply = self.on_gateway_login_subdev_reply
        self.__linkkit.on_gateway_logout_subdev_reply = self.on_gateway_logout_subdev_reply
        self.__linkkit.on_gateway_register_subdev_reply = self.on_gateway_register_subdev_reply
        self.__linkkit.on_gateway_product_register_subdev_reply = self.on_gateway_product_register_subdev_reply
        self.__linkkit.on_gateway_topo_change = self.on_gateway_topo_change
        # 加载网关的物模型数据
        self.__linkkit.thing_setup("tsl.json")
        self.__linkkit.config_device_info("Eth|03ACDEFF0032|Eth|03ACDEFF0031")
        self.__call_service_request_id = 0

    def on_device_dynamic_register(self, rc, value, userdata):
        if rc == 0:
            print("dynamic register device success, value:" + value)
        else:
            print("dynamic register device fail, message:" + value)

    def demo_get_subdev_list(self):
        subdev1 = ["{YourSubDevProductKey01}", "{YourSubDevDeviceName01}", "{YourSubDevDeviceSecret01}"]
        subdev2 = ["{YourSubDevProductKey02}", "{YourSubDevDeviceName02}", "{YourSubDevDeviceSecret02}"]
        subdev3 = ["{YourSubDevProductKey03}", "{YourSubDevDeviceName03}", "{YourSubDevDeviceSecret03}"]
        subdev4 = ["{YourSubDevProductKey04}", "{YourSubDevDeviceName04}", "{YourSubDevDeviceSecret04}"]
        subdev5 = ["{YourSubDevProductKey05}", "{YourSubDevDeviceName05}", "{YourSubDevDeviceSecret05}"]
        subdev_array = [subdev1, subdev2, subdev3, subdev4, subdev5]
        return subdev_array

    # 连接建立的回调
    def on_connect(self, session_flag, rc, userdata):
        print("on_connect:%d,rc:%d,userdata:" % (session_flag, rc))
        subdev_array = self.demo_get_subdev_list()
        # 增加子设备的topo关系
        ret, request_id = self.__linkkit.gateway_add_subdev_topo(subdev_array)
        print("gateway_add_subdev_topo ret:%d, with request_id:%s" % (ret, request_id))

    def on_disconnect(self, rc, userdata):
        print("on_disconnect:rc:%d,userdata:" % rc)

    def on_topic_message(self, topic, payload, qos, userdata):
        print("on_topic_message:" + topic + " payload:" + str(payload) + " qos:" + str(qos))
        pass

    def on_subscribe_topic(self, mid, granted_qos, userdata):
        print("on_subscribe_topic mid:%d, granted_qos:%s" %
              (mid, str(','.join('%s' % it for it in granted_qos))))
        pass

    def on_unsubscribe_topic(self, mid, userdata):
        print("on_unsubscribe_topic mid:%d" % mid)
        pass

    def on_publish_topic(self, mid, userdata):
        print("on_publish_topic mid:%d" % mid)

    def on_thing_prop_changed(self, params, userdata):
        print("on_thing_prop_changed params:" + str(params))

    def on_thing_enable(self, userdata):
        print("on_thing_enable")

    def on_thing_disable(self, userdata):
        print("on_thing_disable")

    def on_thing_event_post(self, event, request_id, code, data, message, userdata):
        print("on_thing_event_post event:%s,request id:%s, code:%d, data:%s, message:%s" %
              (event, request_id, code, str(data), message))
        pass

    def on_thing_prop_post(self, request_id, code, data, message,userdata):
        print("on_thing_prop_post request id:%s, code:%d, data:%s message:%s" %
              (request_id, code, str(data), message))

    def on_thing_raw_data_arrived(self, payload, userdata):
        print("on_thing_raw_data_arrived:%s" % str(payload))

    def on_thing_raw_data_post(self, payload, userdata):
        print("on_thing_raw_data_post: %s" % str(payload))

    # 添加子设备topo关系结果的回调
    def on_gateway_add_subdev_topo_reply(self, request_id, code, data, msg, user_data):
        print("on_gateway_add_subdev_topo_reply for request_id:%s, code:%d, data:%s message:%s" %
            (request_id, code, str(data), msg))
        if code != 200:
            print("unexpected error code:" + code)
            # 如果添加topo关系失败则退出
            return
        subdev_array = self.demo_get_subdev_list()
        # topo关系添加成功后，要进行子设备的login操作，之后才能上报数据
        # 具体子设备的信息请参见data参数中的json字段
        ret, request_id_2 = self.__linkkit.gateway_login_subdev(subdev_array)
        print("gateway_login_subdev, ret:%d, request_id:%s" % (ret, request_id_2))

    def on_gateway_delete_subdev_topo_reply(self, request_id, code, data, msg, user_data):
        print("on_gateway_delete_subdev_topo_reply for request_id:%s, code:%d, data:%s message:%s" %
            (request_id, code, str(data), msg))

    def on_gateway_login_subdev_reply(self, request_id, code, data, msg, user_data):
        print("on_gateway_login_subdev_reply for request_id:%s, code:%d, data:%s message:%s" %
            (request_id, code, str(data), msg))
        # 如果返回值不成功，就要返回错误值
        if 200 != code:
            print("unexpected error code:" + code)
            return
        # 如果login成功，子设备发布消息
        # self.__linkkit.publish_topic("/sys/{YourSubdevProductKey}/{YourSubdevDeviceName}/thing/event/property/post","123", 0)

    def on_gateway_logout_subdev_reply(self, request_id, code, data, msg, user_data):
        print("on_gateway_logout_subdev_reply for request_id:%s, code:%d, data:%s message:%s" %
            (request_id, code, str(data), msg))
        if code != 200:
            print("gateway_logout_subdev failed")
            return

    def on_gateway_register_subdev_reply(self, request_id, code, data, msg, user_data):
        print("on_gateway_register_subdev_reply for request_id:%s, code:%d, data:%s message:%s" %
            (request_id, code, str(data), msg))

    def on_gateway_product_register_subdev_reply(self, request_id, code, data, msg, user_data):
        print("on_gateway_product_register_subdev_reply for request_id:%s, code:%d, data:%s message:%s" %
            (request_id, code, str(data), msg))

    def on_gateway_topo_change(self, request_id, params, userdata):
        print("on_gateway_topo_change request_id:%s, params:%s" %
            (request_id, params))

    def on_topic_message(self, topic, payload, qos, userdata):
        print("on topic message: topic:%s, payload:%s qos%d" %
            (topic, payload, qos))

    def on_thing_call_service(self, identifier, request_id, params, userdata):
        print("on_thing_call_service identifier:%s, request_id:%s, params:%s" %
              (identifier, request_id, params))
        self.__call_service_request_id = request_id
        pass

    def user_loop(self):
        self.__linkkit.connect_async()
        tips = "1: gateway dynamic register subdevs\n" +\
               "2 subdev publish message\n" +\
               "3 subdev subscribe topics\n" +\
               "4 gateway logout subdev \n" +\
               "5 gateway delete subdev topo \n" +\
               ""
        while True:
            try:
                msg = input()
            except KeyboardInterrupt:
                sys.exit()
            else:
                #若子设备的deviceSecret还没有获取到，网关需要对子设备先进行动态注册. 注：这里输入的是productSecret
                if msg == "1":
                    subdev1 = ["{YourSubDevProductKey01}", "{YourSubDevDeviceName01}", "{YourSubDevProductSecret01}"]
                    subdev_array = [subdev1]
                    ret, request_id = self.__linkkit.gateway_product_register_subdev(subdev_array)
                    print("gateway_product_register_subdev ret:%d, with request_id:%s" % (ret, request_id))
                # 子设备login后，发送消息
                elif msg == "2":
                    self.__linkkit.publish_topic(
                        "/sys/{YourSubDevProductKey01}/{YourSubDevDeviceName01}/user/update", "demo Payload", 0)
                # 子设备login后，订阅报文
                elif msg == "3":
                    self.__linkkit.subscribe_topic(
                         "/{YourSubDevProductKey01}/{YourSubDevDeviceName01}/user/get", 0)
                # 子设备login并完成业务后，通过logout进行离线
                elif msg == "4":
                    subdev_array = self.demo_get_subdev_list()
                    ret, request_id = self.__linkkit.gateway_logout_subdev(subdev_array)
                    print("gateway_logout_subdev, ret:%d, with request_id:%s" % (ret, request_id))
                # logout后，若要删除云端的topo关系，可通过gateway_delete_subdev_topo来进行
                elif msg == "5":
                    subdev_array = self.demo_get_subdev_list()
                    ret, request_id_2 = self.__linkkit.gateway_delete_subdev_topo(subdev_array)
                    print("gateway_delete_subdev_topo ret:%d with request_id:%s" % (ret, request_id_2))
                else:
                    sys.exit()

if __name__ == "__main__":
    custom_thing = CustomerThing()
    custom_thing.user_loop()
