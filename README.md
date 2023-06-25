# WatchDog机器狗主程序

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

## 简介

本项目是毕业设计《针对有色废液检测的巡检机器狗设计》的源代码，项目基于Waveshare的开源树莓派机器狗**PIPPY**开发而成。Waveshare的PIPPY项目已经实现了机器狗的硬件设计、外壳材料制作以及机器狗运动控制算法、电池电压采集、超声波测距等功能。

机器狗的主程序使用 Python 3.7编写，它主要包括如下模块：

### 1）感知控制模块  

控制机械狗的运动、采集实时画面、使用超声波测距、循迹等。

### 2）Flask后端模块 

 能启动一个基于Flask后端框架开发的Web应用程序，实现远程手动控制、工作模式切换、实时画面上传、数据库管理等功能。用户可通过机器狗的IP地址或申请第三方内网穿透平台提供的端口映射访问到到机器狗的Web页面，实现远程控制和历史记录查看。

### 3）MQTT上传模块   

本项目使用MQTT协议将异常记录写成JSON格式的数据包上传到阿里云物联网平台，使用的账户ID是作者本人的。在下载使用时，可以注释掉与 mqttTolols.py 相关的代码，或将有关的参数修改为自己的账号ID。



## 新增功能

本项目在PIPPY的基础上增加的功能有：

### 1）自动循迹避障功能  

在  http://192.168.43.164:5000/wspanel  页面访问控制台页面，点击 【 Track Line 】 按钮，可以开启或关闭自动循迹功能。自动循迹功能是一个综合性较强的功能，它使用摄像头画面二值化分析，实现了循黑线或循白线。通过调用超声波模块，每隔1秒获取前方物体距离，遇到距离15cm的障碍物时会停止前进，障碍物距离低于10cm时，机器狗会自动后退远离。自动循迹开启时，也打开了目标检测功能，识别到的目标会在实时画面中框选出来，同时会在数据库中写入记录，保存截图等。

### 2）YOLOv5有色液体检测功能   

在  http://192.168.43.164:5000/wspanel  页面访问控制台页面，点击 【 YOLO Switch 】按钮，可以开启或关闭目标检测功能。该功能所需要的检测模型是基于YOLOv5目标检测模型框架训练而成的，数据集有一部分从网上搜索获取，也有和一部分是自己制作的有色液体照片。

要得到想要的目标检测模型，可在YOLOv5训练框架中加载数据集，实施自动训练，得到best.pt模型文件后，转换成.onnx模型文件移植到树莓派上，再使用OpenCV的DNN函数加载这个模型文件,实现目标检测。具体实现可参考【camera_opencv.py】的m_detection等函数。

### 3）历史记录Web页面  

在  http://192.168.43.164:5000/home  访问异常记录页面，可以查看到异常记录列表，每个列表项包括异常类别、液体颜色、日期、时间、截图。在导航栏的**Login**页面登录后，可以实现编辑、增加、删除等功能。

### 4）控制台Web页面  

在  http://192.168.43.164:5000/wspanel  页面访问控制台页面。控制台页面使用HTML、JavaScript和CSS等编写，页面主要由标题栏、实时图像区、硬件负载区、动作控制区、巡线设置区和工作模式选择区组成，点击相应按钮，前端会通过WebSocket给后端发送相应的数据，实现工作模式切换。

（注：192.168.43.164是机器狗连接热点时获取的局域网IP地址，端口5000是Flask后端服务使用的端口）

## 更新记录

### 2023-06-24

更新README文档，更新可能要用到的资料链接。

### 2023-06-16  Version 1.0

上传机器狗主程序代码，基本完成README文档的编写，尚未上传训练数据集和YOLO训练程序代码。



## 研究意义

随着工业发展，废液处理工作量扩大，产生废液巡检需求。人工巡检费时费力，容易产生惰性。

使用机器代替人工有以下好处：

1）代替重复性工作，减轻劳动强度；

2）深入管线密集区，保障人员安全；

3）搭载多种传感器，数据采集效率高；

4）实时上传记录到后台，可实现远程监控。

本设计针对废液泄漏场景，设计了一种用于有色废液检测的智能巡检机器狗。所谓智能巡检机器狗，就是一种运用图像识别、远程操控等技术，实现自动巡逻或手动遥控的机器狗。它在通过各种传感器收集附近的数据后，将数据上报给后台服务器，并在客户端直观显示。它拥有四肢，较为发达的四肢可攀爬一定坡度的台阶。它代替巡检人员从事一些重复性工作，或进入不安全的区域查看现场情况，有助于减少人力成本，并降低工作风险。



## 安装和配置

系统环境：刷入【2021-10-18-raspbian-buster-full.7z】系统包的树莓派4B。

WiFi网络：要连接到自己的热点，首先需要拧开后背上的四颗螺丝，将SD卡取出，用读卡器插到电脑上。接着在wpa_supplicant.conf文件（见网盘附件）中写入自己的手机热点的名字和密码。然后复制ssh文件和wpa_supplicant.conf文件（见网盘附件）到SD卡上，将SD卡插入到树莓派上。最后打开自己的手机热点并启动树莓派，看到树莓派连接到热点上即为成功。

Python依赖库：可直接执行【setup.py】安装依赖包，之后再升级OpenCV到4.5.5。

**注：如果想用GPU进行推理，不要用.whl文件安装OpenCV，因为.whl是编译好的包，基本上可以确定是用CPU推理的。GPU推理版要手动设定安装参数进行安装，具体方法请自行百度。**

可能需要的依赖包：

```sh
sudo apt update
sudo apt -y dist-upgrade
sudo apt clean
sudo pip3 install -U pip

sudo apt-get install -y python-dev python3-pip libfreetype6-dev libjpeg-dev build-essential
sudo -H pip3 install --upgrade luma.oled
sudo apt-get install -y i2c-tools
sudo apt-get install -y python3-smbus
sudo pip3 install icm20948
sudo pip3 install flask
sudo pip3 install flask_cors
sudo pip3 install websockets

sudo pip3 install opencv-contrib-python==3.4.11.45
sudo pip3 uninstall -y numpy
sudo pip3 install numpy==1.21

sudo apt-get -y install libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev
sudo pip3 install imutils zmq pybase64 psutil
sudo apt-get install -y util-linux procps hostapd iproute2 iw haveged dnsmasq

sudo pip3 install pi-ina219
```



## 使用方法

### 1）启动工作程序

前提：树莓派开机以后，命令行所在目录为  /home/pi  ，而且WatchDog工作程序的文件夹在这个目录下。

在命令行执行以下命令即可启动工作程序。

```sh
cd WatchDog
python3 webServer.py
```

### 2）关闭工作程序

之前启动工作程序所在的命令行**无法通过Ctrl+C或Ctrl+D关掉程序**，应使用如下方法关闭：

(1）再打开一个命令行；

(2）直接输入`sudo killall python3`，然后回车。



### 3）添加或修改Web页面的用户名和密码

参考来源：[第 8 章：用户认证 - Flask 入门教程 (helloflask.com)](https://tutorial.helloflask.com/login/) 【生成管理员用户】

```
(env) $ flask admin
Username: McEwan
Password: 1233211234567  # hide_input=True 会让密码输入隐藏
Repeat for confirmation: 1233211234567  # confirmation_prompt=True 会要求二次确认输入
Updating user...
Done.
```



### 4）在电脑上的PyCharm远程编辑代码

1）在PyCharm设置的【项目：PIPPY】的【Python解释器】为`Remote Python 3.7.3 (sftp://pi@192.168.43.164:22/usr/bin/python3.7)`，然后点右边的...设置，选择SSH，然后选择树莓派的Python解释器的位置，默认是 `usr/bin/python3.7` ；

2）远程保存地址`/home/pi/WatchDog`，填写完成后，点击完成，就会建立自动同步；

3）编辑代码后，点击PyCharm上方的工具——部署——上传到...，即可将该文件上传到树莓派的对应位置。工作目录中的其他文件或文件夹同样可以在PyCharm左侧选中它们，然后右键——部署——上传。



## 项目结构

注：可查看README源代码看到正常渲染的目录结构。

.  				根目录
│  app.py  			Flask视图函数所在位置
│  base_camera.py 	摄像头基本使用函数
│  camera_opencv.py  	OpenCV图像处理有关函数
│  data.db			SQLite数据库
│  ICM20948.py		姿态传感器
│  info.py			获取CPU温度等信息
│  initServo.py		组装舵机时用于初始化舵机角度
│  Kalman_filter.py	卡尔曼滤波
│  linkageREVERSE.py	连杆逆解（没有用到）
│  list.txt			文件夹树形目录
│  myTest.py		简单的测试功能（没有用到）
│  nohup.out		--
│  OLED.py			OLED小屏幕有关函数
│  PCA9685.py		舵机控制模块有关函数
│  PIPPY.py			机器狗运动的偏底层函数
│  README.md		--
│  robot.py			机器狗运动的封装函数
│  setup.py			安装相关依赖
│  simpleTest.py		简单的测试功能（没有用到）
│  ultra.py			超声波测距相关函数
│  Voltage.py		获取电池电压
│  webServer.py		主程序入口
│  
├─dist			控制台Web页面资源
│  │  123.txt
│  │  favicon.ico
│  │  index.html
│  │  logo.png
│  │  manifest.json
│  │  precache-manifest.02b800736c2da055bda815acfa037b17.js
│  │  robots.txt
│  │  service-worker.js
│  │  
│  ├─css
│  │      app.8a756fac.css
│  │      chunk-vendors.a639f090.css
│  │      css.txt
│  │      
│  ├─fonts
│  │      fonts.txt
│  │      materialdesignicons-webfont.2d0a0d8f.eot
│  │      materialdesignicons-webfont.b4917be2.woff
│  │      materialdesignicons-webfont.d0066537.woff2
│  │      materialdesignicons-webfont.f5111234.ttf
│  │      roboto-latin-100.5cb7edfc.woff
│  │      roboto-latin-100.7370c367.woff2
│  │      roboto-latin-100italic.f8b1df51.woff2
│  │      roboto-latin-100italic.f9e8e590.woff
│  │      roboto-latin-300.b00849e0.woff
│  │      roboto-latin-300.ef7c6637.woff2
│  │      roboto-latin-300italic.14286f3b.woff2
│  │      roboto-latin-300italic.4df32891.woff
│  │      roboto-latin-400.479970ff.woff2
│  │      roboto-latin-400.60fa3c06.woff
│  │      roboto-latin-400italic.51521a2a.woff2
│  │      roboto-latin-400italic.fe65b833.woff
│  │      roboto-latin-500.020c97dc.woff2
│  │      roboto-latin-500.87284894.woff
│  │      roboto-latin-500italic.288ad9c6.woff
│  │      roboto-latin-500italic.db4a2a23.woff2
│  │      roboto-latin-700.2735a3a6.woff2
│  │      roboto-latin-700.adcde98f.woff
│  │      roboto-latin-700italic.81f57861.woff
│  │      roboto-latin-700italic.da0e7178.woff2
│  │      roboto-latin-900.9b3766ef.woff2
│  │      roboto-latin-900.bb1e4dc6.woff
│  │      roboto-latin-900italic.28f91510.woff
│  │      roboto-latin-900italic.ebf6d164.woff2
│  │      
│  ├─img
│  │  │  bg.jpg
│  │  │  bg2.jpg
│  │  │  img.txt
│  │  │  
│  │  └─icons
│  │          favicon-32x32 .png
│  │          favicon.ico
│  │          icons.txt
│  │          logo.png
│  │          safari-pinned-tab.svg
│  │          wavelogo.png
│  │          
│  └─js
│          app.38235a8c.js
│          app.38235a8c.js.map
│          chunk-vendors.3007e197.js
│          chunk-vendors.3007e197.js.map
│          js.txt
│          
├─models			MQTT相关函数、目标检测模型文件
│  │  best13c-320.onnx
│  │  best14c320.onnx
│  │  colorList.py
│  │  compareArray.py
│  │  mqttTools.py
│  │  
│  ├─ali-example-code
│  │  │  aliLink.py
│  │  │  mqttd.py
│  │  │  readme.md
│  │  │  rpi.py
│  │  │  run.py
│  │  │  
│  │  └─__pycache__
│  │          aliLink.cpython-37.pyc
│  │          mqttd.cpython-37.pyc
│  │          rpi.cpython-37.pyc
│  │          
│  ├─python-linkkit-examples
│  │      data_transfer.js
│  │      dynamic_register.py
│  │      dynamic_register_deprecated.py
│  │      dynamic_register_nwl.py
│  │      gateway_demo.py
│  │      model_raw.json
│  │      mqtt_connect_TCP.py
│  │      mqtt_connect_TLS.py
│  │      mqtt_sub_pub_on.py
│  │      ota_demo.py
│  │      Readme.txt
│  │      thing_alink.py
│  │      thing_custom.py
│  │      tsl.json
│  │      
│  └─__pycache__
│          colorList.cpython-37.pyc
│          compareArray.cpython-37.pyc
│          mqttTools.cpython-37.pyc
│          
├─static			异常记录Web页面资源
│  ├─css
│  │      style.css
│  │      
│  ├─images
│  │      avatar.png
│  │      bg.jpg
│  │      bg2.jpg
│  │      logo.png
│  │      totoro.gif
│  │      yanni.png
│  │      
│  └─runs
│      └─imagesave
├─templates			异常记录Web页面资源
│      base.html
│      edit.html
│      imageshow.html
│      login.html
│      record.html
│      settings.html
│      
├─waveshare_OLED		OLED有关函数库
│  │  config.py
│  │  OLED_0in91.py
│  │  __init__.py
│  │  
│  └─__pycache__
│          config.cpython-37.pyc
│          config.cpython-39.pyc
│          OLED_0in91.cpython-37.pyc
│          OLED_0in91.cpython-39.pyc
│          __init__.cpython-37.pyc
│          __init__.cpython-39.pyc
│          
└─__pycache__
        app.cpython-37.pyc
        base_camera.cpython-37.pyc
        camera_opencv.cpython-37.pyc
        ICM20948.cpython-37.pyc
        info.cpython-37.pyc
        info.cpython-39.pyc
        Kalman_filter.cpython-37.pyc
        OLED.cpython-37.pyc
        OLED.cpython-39.pyc
        PCA9685.cpython-37.pyc
        PIPPY.cpython-37.pyc
        robot.cpython-37.pyc
        ultra.cpython-37.pyc
        Voltage.cpython-37.pyc



## 相关资源和教程

- [waveshare/PIPPY: PIPPY, An Open Source Bionic Dog-Like Robot Powered By Raspberry Pi (github.com)](https://github.com/waveshare/PIPPY)— PIPPY项目主页
- [ultralytics/yolov5 at v6.1 (github.com)](https://github.com/ultralytics/yolov5/tree/v6.1)— YOLOv5项目主页（v6.1）
- [Flask 入门教程 (helloflask.com)](https://tutorial.helloflask.com/)——Flask入门教程
- [NATTUNNEL 内网穿透 – 量子互联 (uulap.com)](https://www.uulap.com/nattunnel)——量子互联内网穿透
- [MobaXterm Xserver with SSH, telnet, RDP, VNC and X11 - Download (mobatek.net)](https://mobaxterm.mobatek.net/download.html) ——MobaXterm
- 百度网盘：https://pan.baidu.com/s/1-BUoXd8oCyYGEy-90Em37Q?pwd=3oqn ——可能用到的资料包，提取码：3oqn 
	

## 联系作者

欢迎将本项目的功能继续完善，使其成为更强大的机(Wan)器(Ju)狗系统。

[提一个 Issue](https://github.com/cqwsadev/ColoredLiquidWatchDog/issues) 或者提交一个 Pull Request，也可通过chinas0310@gmail.com邮件联系。



## 致谢

感谢以下开源项目对本项目的帮助：

- Raspberry Pi
- PIPPY
- Python
- Flask
- OpenCV

