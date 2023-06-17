import asyncio
import threading

import websockets

import OLED
import PIPPY
import time

import info
import robot
from webServer import wifi_check, batteryStatus, main_logic

# OLED
screen = OLED.OLED_ctrl()
screen.start()
wifi_check()

bs_threading = threading.Thread(target=batteryStatus)
bs_threading.setDaemon(True)
bs_threading.start()

robotCtrl = PIPPY.PIPPY()
robotCtrl.start()  # 为了避免控制运动的函数造成阻塞，使用多线程来进行控制，这里开启这个线程

#获取cpu gpu温度
print('cpu temp:',info.get_cpu_tempfunc())
print('cpu use:', info.get_cpu_use())

# 动作
# robot.lookUp()
# time.sleep(1)
# robot.lookDown()
# time.sleep(2)
# robot.lookForward()
# time.sleep(1)
# robot.stayLow()
# time.sleep(2)
# robot.standUp()
# time.sleep(5)

# PIPPY底层运动控制
# robotCtrl.moveStart(100, 'forward', 'no')  # 机器人开始以100的速度向正前方走动
# time.sleep(10)  # 延迟10s，这段时间内机器人将会保持运动
#
# robotCtrl.moveStop()  # 机器人停止走动
# time.sleep(1)
#
# robotCtrl.moveStart(100, 'no', 'left')  # 机器人以100的速度向左转弯
# time.sleep(3)
#
# robotCtrl.moveStop()  # 机器人停止走动robotCtrl.moveStart(100, 'forward', 'no')  # 机器人开始以100的速度向正前方走动
# time.sleep(1)  # 延迟10s，这段时间内机器人将会保持运动
#
# robotCtrl.moveStop()  # 机器人停止走动
# time.sleep(1)
#
# robotCtrl.moveStart(100, 'no', 'left')  # 机器人以100的速度向左转弯
# time.sleep(3)

robotCtrl.moveStop()  # 机器人停止走动

while 1:
    try:  # Start server,waiting for client
        start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
        asyncio.get_event_loop().run_until_complete(start_server)
        print('waiting for connection...')
        # print('...connected from :', addr)
        break
    except Exception as e:
        print(e)

try:
    asyncio.get_event_loop().run_forever()
except Exception as e:
    print(e)





