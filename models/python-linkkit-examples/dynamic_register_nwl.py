import sys
import time

from linkkit import linkkit
import logging

"""
一型一密（免预注册）用于在获取设备连云的身份证书信息。"免预注册"是指用户不用事先在控制台创建设备，可以依靠本次操作直接在物联网平台创建设备。

1.使用一型一密（免预注册）获取设备连云的client_id, username, token
    a.输入linkkit.LinkKit所需的参数
      auth_type：请填写"regnwl"，表示当前是一型一密免预注册认证
      instance_id：对于企业实例, 或者2021年07月30日之后（含当日）开通的物联网平台服务下公共实例,请从"实例详情"页面中找到"实例 ID",填入；
      对于2021年07月30日之前（不含当日）开通的物联网平台服务下公共实例，该字段请填写空字符串""
    b.调用lk.connect_async()连接物联网平台，连接成功后，服务端下发client_id, username, token, SDK自动断开连接（注：此连接仅限于用于
      获取token等设备证书信息,不能用于收发业务报文，因此收到token等信息后SDK内部自动断开）
    c.建议用户参考本demo，调用lk.destroy()退出
"""

# config log
__log_format = '%(asctime)s-%(process)d-%(thread)d - %(name)s:%(module)s:%(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(format=__log_format)


product_key = "${YourProductKey}"
device_name = "${YourDeviceName}"
product_secret = "${YourProductSecret}"
instance_id = "${YourInstanceId}"
client_id = ""
username = ""
password = ""
g_got_result = 0

lk_auth = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key=product_key,
    product_secret=product_secret,
    device_name=device_name,
    device_secret="",
    instance_id=instance_id,
    auth_type="regnwl")


def on_device_dynamic_register_nwl_reply(code, client_id_l, user_name_l, password_l):
    print("code:", code)
    if 0 == code:
        print("cid:", client_id_l)
        print("user_name:", user_name_l)
        print("password:", password_l)
        global client_id
        global username
        global password
        global g_got_result
        g_got_result = 1
        client_id = client_id_l
        username = user_name_l
        password = password_l


lk_auth.enable_logger(logging.DEBUG)
lk_auth.on_device_dynamic_register_nwl_reply = on_device_dynamic_register_nwl_reply
lk_auth.connect_async()
# 等待下行报文，一般1s内就能返回
time.sleep(5)
lk_auth.destroy()

if g_got_result == 0:
    print("failed to get device client_id/username/password, exit")
    exit(-1)

"""
    设备通过上述步骤已经获取了连云的client_id, username, token
    接着我们演示设备如何使用这三个元素连云
    一型一密免预注册，返回的不是device_secret,而是client_id,username,token。
    在获取到client_id, username, token后，请参考thing_alink.py连接物联网平台，其中构造函数的linkkit.LinkKit中要传入client_id,
    username，password这三个字段, 值从步骤1中获得.参考构造函数如下：
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


lk = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key=product_key,
    device_name=device_name,
    device_secret="",
    instance_id=instance_id,
    username=username,
    password=password,
    client_id=client_id)
lk.on_connect = on_connect
lk.on_disconnect = on_disconnect
lk.on_topic_message = on_topic_message
lk.on_subscribe_topic = on_subscribe_topic
lk.on_unsubscribe_topic = on_unsubscribe_topic
lk.on_publish_topic = on_publish_topic
lk.connect_async()

while True:
    time.sleep(2)


