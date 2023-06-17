import time

from linkkit import linkkit
import logging

"""
一型一密（预注册）用于在获取设备连云的身份证书信息。"预注册"是指用户需要事先在控制台创建设备。具体步骤如下：
    a.输入linkkit.LinkKit所需的参数
      auth_type：请填写"register"，表示当前是一型一密免预注册认证
      instance_id：对于企业实例, 或者2021年07月30日之后（含当日）开通的物联网平台服务下公共实例,请从"实例详情"页面中找到"实例 ID",填入；
      对于2021年07月30日之前（不含当日）开通的物联网平台服务下公共实例，该字段请填写空字符串""
    b.调用lk.connect_async()连接物联网平台，连接成功后，服务端下发device_secret, SDK自动断开连接（注：此连接仅限于用于
      获取设备秘钥,不能用于收发业务报文，因此收到设备秘钥等信息后SDK内部自动断开）
    c.建议用户参考本demo，在获取到device_secret后，调用destroy()退出
"""

# config log
__log_format = '%(asctime)s-%(process)d-%(thread)d - %(name)s:%(module)s:%(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(format=__log_format)

product_key = "${YourProductKey}"
device_name = "${YourDeviceName}"
product_secret = "${YourProductSecret}"
instance_id = "${YourInstanceId}"
device_secret = ""

lk_auth = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key=product_key,
    device_name=device_name,
    device_secret="",
    auth_type="register",
    instance_id=instance_id,
    product_secret=product_secret)


def on_device_dynamic_register(rc, value, userdata):
    if rc == 0:
        global device_secret
        print("dynamic register device success, rc:%d, value:%s" % (rc, value))
        device_secret = value
    else:
        print("dynamic register device fail,rc:%d, value:%s" % (rc, value))


lk_auth.enable_logger(logging.DEBUG)
lk_auth.on_device_dynamic_register = on_device_dynamic_register
lk_auth.connect_async()

# 等待下行报文，一般1s内就能返回
time.sleep(5)
lk_auth.destroy()

if device_secret is "":
    print("failed to get device secret, exit")
    exit(-1)

"""
   设备通过上述步骤已经获取了连云的秘钥device_secret
   之后使用一机一密的方式连云,本例仅做一个简单的演示，
   详细用法请参考mqtt_connect_TLS.py和thing_alink.py等用例
"""


def on_connect(session_flag, rc, userdata):
    print("on_connect:%d,rc:%d,userdata:" % (session_flag, rc))
    pass


def on_disconnect(rc, userdata):
    print("on_disconnect:rc:%d,userdata:" % rc)


def on_topic_message(topic, payload, qos, userdata):
    print("on_topic_message:" + topic + " payload:" + str(payload) + " qos:" + str(qos))
    pass


def on_subscribe_topic(mid, granted_qos, userdata):
    print("on_subscribe_topic mid:%d, granted_qos:%s" %
          (mid, str(','.join('%s' % it for it in granted_qos))))
    pass


def on_unsubscribe_topic(mid, userdata):
    print("on_unsubscribe_topic mid:%d" % mid)
    pass


def on_publish_topic(mid, userdata):
    print("on_publish_topic mid:%d" % mid)


lk_main = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key=product_key,
    device_name=device_name,
    device_secret=device_secret,
    product_secret="",
    instance_id=instance_id
)
lk_main.enable_logger(logging.DEBUG)
lk_main.on_connect = on_connect
lk_main.on_disconnect = on_disconnect
lk_main.on_topic_message = on_topic_message
lk_main.on_subscribe_topic = on_subscribe_topic
lk_main.on_unsubscribe_topic = on_unsubscribe_topic
lk_main.on_publish_topic = on_publish_topic
lk_main.connect_async()

while True:
    time.sleep(2)

