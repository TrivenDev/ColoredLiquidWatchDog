#!/usr/bin/env/python
# File name   : server.py
# Production  : PIPPY
# Author	  : WaveShare

import time
import threading
import os
import socket

# import camera_opencv
import info
import OLED

# websocket
import asyncio
import websockets

import json
import app

websocketport = 8888
screen = OLED.OLED_ctrl()
screen.start()


def ap_thread():
    os.system("sudo create_ap wlan0 eth0 WatchDog 12345678")  # 建立默认热点


def wifi_check():
    time.sleep(5)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))  # HTTP 测试
        ipaddr_check = s.getsockname()[0]
        s.close()
        print(ipaddr_check)
        screen.screen_show(1, 'IP:' + str(ipaddr_check))  # 显示IP地址和模式
        screen.screen_show(3, 'WIFI MODE: STA')
    except:
        ap_threading = threading.Thread(target=ap_thread)
        ap_threading.setDaemon(True)  # 启动一个热点进程，这个进程要保护
        ap_threading.start()

        screen.screen_show(1, 'IP:192.168.12.1')
        screen.screen_show(3, 'AP STARTING 10%')

        time.sleep(1)
        screen.screen_show(3, 'AP STARTING 50%')

        time.sleep(1)
        screen.screen_show(3, 'AP STARTING 80%')

        time.sleep(1)
        screen.screen_show(3, 'AP STARTING 100%')

        time.sleep(1)
        screen.screen_show(3, 'WIFI MODE: AP')


def batteryStatus():
    while 1:  # 需要循环进行，5秒获取一次电压
        batteryV = app.camera_opencv.robot.getVoltage()
        screen.screen_show(2, 'POWER: {:.2f}V'.format(batteryV))  # 在第二行打出电压
        time.sleep(5)


async def check_permit(websocket):
    await websocket.send("Please login. Send username:password to me.")
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "Connected!"
            await websocket.send(response_str)  # 服务端回复已连接
            return True
        else:
            response_str = "Sorry, the username or password is Wrong！"
            await websocket.send(response_str)  # 服务端回复未连接


async def recv_msg(websocket, fpv=None):
    while True:
        response = {
            'status': 'ok',
            'title': '',
            'data': None
        }  # 服务器ws响应报文

        data = ''
        data = await websocket.recv()  # 通过websocket接收指令，接收的是json字符串
        try:
            data = json.loads(data)  # 如果是把json数据'{k:v}'转为 字典
        except Exception as e:
            print('not A JSON')
            pass

        if not data:
            continue

        if isinstance(data, str):
            # 动作控制
            # 包括方向、姿态、保持距离、自动绕开障碍物
            # camera_opencv.commandAct(inputCommand)
            flask_app.commandInput(data)  # Class webapp

            if 'get_info' == data:
                response['title'] = 'get_info'
                response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]

            if 'findColor' == data:  # 寻颜色模式
                flask_app.modeselect('findColor')  # 收到寻找颜色的命令
                print('set mode as findColor')

            elif 'scan' == data:  # 扫描
                print('scanning')
                ds = app.camera_opencv.ultra.checkdist()
                print(ds)
                radar_send = [[3, 60], [ds, 70], [ds, 80], [ds, 90], [ds, 100], [ds, 110], [3, 120]]
                # radar_send = []
                # for i in range(1,150):
                # 	radar_send.append[ds]
                response['title'] = 'scanResult'
                response['data'] = radar_send
                time.sleep(0.3)
                pass

            elif 'motionGet' == data:  # 追踪动作
                flask_app.modeselect('watchDog')
                print('set mode as watchDog')

            elif 'stopCV' == data:  # 切换为默认相机模式
                # camera_opencv.m_thread.pause()
                flask_app.modeselect('none')

            # CVFL
            elif 'CVFL' == data:
                flask_app.modeselect('findlineCV')  # 巡线
                print('Set mode as findlineCV')

            elif 'CVFLColorSet' in data:  # 寻找黑线/白线
                color = int(data.split()[1])
                print('set findline color ' + str(color))
                flask_app.camera.colorSet(color)

            elif 'CVFLL1' in data:  # 点击设置巡线区域
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_1(pos)

            elif 'CVFLL2' in data:
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_2(pos)

            elif 'CVFLSP' in data:  # 警戒区长度
                err = int(data.split()[1])
                flask_app.camera.errorSet(err)

            elif 'defEC' in data:  # Z
                fpv.defaultExpCom()


        elif (isinstance(data, dict)):  # 如果收到的数据是一个字典
            if data['title'] == "findColorSet":
                color = data['data']
                flask_app.colorFindSet(color[0], color[1], color[2])  # 设置寻找颜色的参数：hsv的值

        print(data)
        response = json.dumps(response)  # 把字典打包成json字符串
        await websocket.send(response)


async def main_logic(websocket, path):  # 被动执行的函数

    await check_permit(websocket)  # 检查许可
    await recv_msg(websocket)  # 接收命令并给予回复


if __name__ == '__main__':
    global flask_app

    wifi_check()  # 网络初始化，如果有wifi就用wifi，没有wifi就开热点，只是执行一次
    flask_app = app.webapp()  # 可以通过app.camera调用相机
    flask_app.startthread()  # 启动flask进程

    bs_threading = threading.Thread(target=batteryStatus)  # 显示电池电压 这是一个进程
    bs_threading.setDaemon(True)
    bs_threading.start()  # 守护进程

    while 1:  # 创建一个websocket服务器，用于监听网页的信息
        try:  # Start server,waiting for client
            ws_server = websockets.serve(main_logic, '0.0.0.0', websocketport)
            asyncio.get_event_loop().run_until_complete(ws_server)
            print('waiting for connection...')
            # print('...connected from :', addr)
            break  # 如果创建成功就可以退了
        except Exception as e:
            print(e)
            pass

    try:  # loop 心跳
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(e)
        pass
