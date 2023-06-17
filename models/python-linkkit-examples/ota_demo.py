import sys
from linkkit import linkkit
import logging

# config log
__log_format = '%(asctime)s-%(process)d-%(thread)d - %(name)s:%(module)s:%(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(format=__log_format)

# TODO: 输入设备的证书信息
lk = linkkit.LinkKit(
    host_name="cn-shanghai",
    product_key="xxxxxxxxxxx",
    device_name="device-name",
    device_secret="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
# TODO: 输入用户的mqtt接入点
lk.config_mqtt(endpoint="iot-********.mqtt.iothub.aliyuncs.com")

lk.enable_logger(logging.DEBUG)


def on_device_dynamic_register(rc, value, userdata):
    if rc == 0:
        print("dynamic register device success, rc:%d, value:%s" % (rc, value))
    else:
        print("dynamic register device fail,rc:%d, value:%s" % (rc, value))


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


def on_ota_message_arrived(ota_notice_type, version, size, url, sign_method, sign, module, extra):
    # ota_notice_type 为0，表示没有服务端没有部署ota任务；为1，表示云端下推的ota任务；为2，表示设备端自己主动向服务端查询ota任务
    if ota_notice_type > 0:
        # TODO: 用户判断版本号，决定是否要升级，以及何时升级

        # TODO: 如果固件的大下载耗时长，建议用户在这里起一个线程来处理，从而不阻塞整体链路。在这种情况下，如果用户在短时间内多次收到OTA消息
        #  （比如用户短期内多次主动请求OTA固件,或者收到平台主动推送的同时又自己主动请求固件），那么用户需要做好多线程之间的并发处理逻辑，
        #  避免多个线程同时写同一个文件

        print("on_ota_message version:" + version + " size:" + str(size) + " url:" + url + " sign_method:" + sign_method)
        print("on_ota_message sign:" + sign + " module:" + module + " extra:" + extra)
        # TODO: 修改firmware_path变量，将固件存储到需要用户自定义的路径
        firmware_path = "demo_ota.py"
        ret = lk.download_ota_firmware(url, firmware_path, sign_method, sign)

        if lk.ErrorCode.SUCCESS == ret:
            # TODO: 用户部署新的固件，并上报新固件的版本号，确认升级完成
            print("report version ")
            lk.ota_report_version(module, version)
            pass
        else:
            print("download error code %x" % ret.value)
    else:
        print("no firmware ")

lk.on_device_dynamic_register = on_device_dynamic_register
lk.on_connect = on_connect
lk.on_disconnect = on_disconnect
lk.on_topic_message = on_topic_message
lk.on_subscribe_topic = on_subscribe_topic
lk.on_unsubscribe_topic = on_unsubscribe_topic
lk.on_publish_topic = on_publish_topic
lk.on_ota_message_arrived = on_ota_message_arrived
lk.connect_async()

while True:
    try:
        msg = input()
    except KeyboardInterrupt:
        sys.exit()
    else:
        if msg == "1":
            lk.disconnect()
        elif msg == "2":
            lk.connect_async()
        else:
            sys.exit()
