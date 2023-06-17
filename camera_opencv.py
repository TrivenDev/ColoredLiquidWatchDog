import os
import random

import cv2

import app
from base_camera import BaseCamera
import numpy as np
import robot
import datetime
import time
import threading
import imutils
import ultra

from models import colorList
from models.compareArray import compareArray
import models.mqttTools as mqtttools

pydir_path = os.path.dirname(os.path.abspath(__file__))
img_savedir = pydir_path + r'/static/runs/imagesave'
linePos_1 = 440
linePos_2 = 380
lineColorSet = 0
frameRender = 1
findLineError = 30

colorUpper = np.array([44, 255, 255])
colorLower = np.array([24, 100, 100])

directionCommand = 'no'
turningCommand = 'no'
speedMove = 50
distanceCheck = 0.15
distavoidCheck =0.10

turningKeep = 3.5  # 3.5
stopKeep = 15


dic_labels = {0: 'onground',
              1: 'leakage',
              }  # 类别

model_h = 320  # 检测模型尺寸，必须与模型文件看齐
model_w = 320
onnx_model = pydir_path + '/models/best13c-320.onnx'  # onnx模型文件
video = 0  # 视频来源，填写路径或摄像头
net = cv2.dnn.readNetFromONNX(onnx_model)  # 适用cv2的dnn网络，套用onnx模型
# net.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)

det_boxes_show = []  # 每个元素是：[ x1 y1 x2 y2 ]
scores_show = []  # 置信度
ids_show = []  # 分类号
InferDelay_show = ""
capimg = None
lastupdatetime = time.time()
colors_dict = colorList.getColorList()  # 颜色的列表

# global det_boxes_show
# global scores_show
# global ids_show
# global InferDelay_show
#####################################################################################

def writeUsualRecord(title, color, getimg, datastream):
    # 记录异常
    new_title = title
    new_color = color
    new_date = datetime.date.today()
    new_time = datetime.datetime.now().strftime('%H:%M:%S')  # 准备信息
    try:
        new_record = app.Record(title=new_title, color=new_color, date=new_date,
                                time=new_time)
        app.db.session.add(new_record)
        app.db.session.commit()
    except:
        print('DataBase update error!')
        pass
    try:
        t = time.time()
        payload_json = {
            'id': int(t % 1000000),
            "version": "1.0",
            "sys": {
                "ack": 0
            },
            'params': {
                datastream: {
                    'title': new_title,  # 类别
                    'color': new_color,  # 颜色
                    'date': str(new_date),
                    'timep': new_time,
                }
            },
            'method': "thing.event.property.post"
        }  # MQTT上报
        mqtttools.aliclient.publish(mqtttools.PUB_TOPIC, payload=str(payload_json), qos=1)
        print('send data to iot server: ' + str(payload_json))
    except:
        print('MQTT publish error!')
        pass
    imgsave_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 准备时间
    try:

        if not os.path.exists(img_savedir):
            print('the Path do not exist!')
            os.makedirs(img_savedir)
        img_savepath = img_savedir + '/' + new_title + new_color + imgsave_time + r'.jpg'
        cv2.imwrite(img_savepath, getimg, [cv2.IMWRITE_JPEG_QUALITY, 80])
        print('Recorded current image at {0}'.format(img_savepath))
    except:
        print('Writing image error!')
        pass

def drawYoloResult(img):
    global lastupdatetime
    global colors_dict
    nowupdatetime = time.time()
    for box, score, id in zip(det_boxes_show, scores_show, ids_show):

        # 意思是，从这三列表中，分别取一个，组合在一起
        # 每循环一次就会在图上圈出一个目标的位置
        xmid, ymid = int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)  # 这是中点坐标
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_value = hsv[ymid, xmid]  # 得到一个三维数组
        color_confirm = ''
        for c, hsv_range in colors_dict.items():  # 识别中心点的颜色
            if compareArray(hsv_value, hsv_range[0], hsv_range[1]):
                color_confirm = c

        # 方框左上角的文字
        label = '%s-%s:%.2f' % (color_confirm, dic_labels[id], score)
        plot_one_box(box, img, color=(255, 0, 0), label=label,
                     line_thickness=None)  # 根据坐标、类别、置信度 画框

        # 向数据库中添加信息
        if nowupdatetime - lastupdatetime > 10 and score >= 0.5:  # 浮点数减法， 每10秒才会上传一次，避免过度操作
            print('HSV:', hsv_value, 'Mid Location:[', xmid, ',', ymid, ']')
            new_title = dic_labels[id]
            new_color = color_confirm
            new_date = datetime.date.today()
            new_time = datetime.datetime.now().strftime('%H:%M:%S')  # 准备信息
            try:
                new_record = app.Record(title=new_title, color=new_color, date=new_date,
                                        time=new_time)
                app.db.session.add(new_record)
                app.db.session.commit()
            except:
                print('DataBase update error!')
                pass

            try:
                t = time.time()
                payload_json = {
                    'id': int(t % 1000000),
                    "version": "1.0",
                    "sys": {
                        "ack": 0
                    },
                    'params': {
                        'singlerecord': {
                            'title': new_title,  # 类别
                            'color': new_color,  # 颜色
                            'date': str(new_date),
                            'timep': new_time,
                        }
                    },
                    'method': "thing.event.property.post"
                }  # MQTT上报
                mqtttools.aliclient.publish(mqtttools.PUB_TOPIC, payload=str(payload_json), qos=1)
                print('send data to iot server: ' + str(payload_json))
            except:
                print('MQTT publish error!')
                pass
            # 保存照片
            imgsave_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 准备信息
            try:

                if not os.path.exists(img_savedir):
                    print('the Path do not exist!')
                    os.makedirs(img_savedir)
                img_savepath = img_savedir + '/' + new_title + new_color + imgsave_time + r'.jpg'
                cv2.imwrite(img_savepath, img, [cv2.IMWRITE_JPEG_QUALITY, 80])
                print('Recorded current image at {0}'.format(img_savepath))
            except:
                print('Writing image error!')
                pass
            lastupdatetime = nowupdatetime  # 更新上传时间

    str_InferDelay = InferDelay_show
    cv2.putText(img, str_InferDelay, (300, 30), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 0), 2)  # 最后写延迟时间有多大

class Camera(BaseCamera):  # 父类提供： frames要实现！
    video_source = 0
    modeSelect = 'none'
    # modeSelect = 'findlineCV'
    # modeSelect = 'findColor'
    # modeSelect = 'watchDog'

    CVMode = 'run'

    # CVMode = 'no'

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()  # 启动BaseCam线程，

    def robotStop(self):
        robot.robotCtrl.moveStart(speedMove, 'no', 'no')
        time.sleep(0.1)
        robot.robotCtrl.moveStart(speedMove, 'no', 'no')

    def colorFindSet(self, invarH, invarS, invarV):
        global colorUpper, colorLower
        # 先计算 该颜色 附近的HSV值
        HUE_1 = invarH + 15
        HUE_2 = invarH - 15
        if HUE_1 > 180: HUE_1 = 180
        if HUE_2 < 0: HUE_2 = 0

        SAT_1 = invarS + 150
        SAT_2 = invarS - 150
        if SAT_1 > 255: SAT_1 = 255
        if SAT_2 < 0: SAT_2 = 0

        VAL_1 = invarV + 150
        VAL_2 = invarV - 150
        if VAL_1 > 255: VAL_1 = 255
        if VAL_2 < 0: VAL_2 = 0
        # 然后设定上下区间的HSV
        colorUpper = np.array([HUE_1, SAT_1, VAL_1])
        colorLower = np.array([HUE_2, SAT_2, VAL_2])
        print('HSV_1:%d %d %d' % (HUE_1, SAT_1, VAL_1))
        print('HSV_2:%d %d %d' % (HUE_2, SAT_2, VAL_2))
        print(colorUpper)
        print(colorLower)

    def modeSet(self, invar):
        Camera.modeSelect = invar

    def CVRunSet(self, invar):
        global CVRun
        CVRun = invar

    def linePosSet_1(self, invar):
        global linePos_1
        linePos_1 = invar

    def linePosSet_2(self, invar):
        global linePos_2
        linePos_2 = invar

    def colorSet(self, invar):
        global lineColorSet
        lineColorSet = invar  # 设置黑白线？

    def randerSet(self, invar):
        global frameRender
        frameRender = invar

    def errorSet(self, invar):
        global findLineError
        findLineError = invar

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():  # 负责返回一系列纯净的帧 img
        global capimg
        camera = cv2.VideoCapture(Camera.video_source)  # 0 camera-->cap

        # 0 camera-->cap
        if not camera.isOpened():
            raise RuntimeError('Could not start camera!')

        cvt = CVThread()
        cvt.start()  # 这是什么线程

        while True:
            loop_start = time.time()
            time.sleep(1 / 15)  # 可以调节帧率
            # read current frame
            success, img = camera.read()  # 读取一个帧
            capimg = img.copy()  # 供给其他函数使用
            # img = cv2.resize(frame, (640, 480)) # 改变图像尺寸
            # 做目标检测
            try:
                if success and m_thread.isRunning(): # 如果目标检测线程在运行，就画框，否则，不画！
                    drawYoloResult(img)  # 画目标检测框
            except:
                print("Function- frames()'s img has problem!")
                pass
            # 目标检测完毕
            if Camera.modeSelect == 'none':
                cvt.pause()  # 挂起
            else:  # 如果模式不是默认
                if cvt.CVThreading:
                    pass
                else:  # cvt为0
                    cvt.mode(Camera.modeSelect, img)  # 画过检测框
                    cvt.resume()  # cvt恢复
                try:
                    # drawYoloResult(img)  # 画目标检测
                    img = cvt.elementDraw(img)  # 画线
                except:
                    pass

            # 计算一个循环之后的时间
            loop_time = time.time() - loop_start
            FPS = 1 / loop_time
            # 显示帧数
            cv2.putText(img, 'FPS:%.2f' % FPS, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # plot_one_box(yolobox, img, color=(255, 0, 0), label=yololabel,
            #              line_thickness=None)  # 根据坐标、类别、置信度 画框
            # frame=capimg
            # scale_percent = 60  # percent of original size
            # width = int(frame.shape[1] * scale_percent / 100)
            # height = int(frame.shape[0] * scale_percent / 100)
            # dim = (width, height)
            #
            # frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

            # 这是生成器，返回编码后的图像 画质降低为50%
            yield cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY,50])[1].tobytes()

def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    """
    description: Plots one bounding box on image img,
                 this function comes from YoLov5 project.
    param:
        x:      a box likes [x1,y1,x2,y2] 一个四维数组
        img:    a opencv image object
        color:  color to draw rectangle, such as (0,255,0) 画框颜色
        label:  str 要写的文字，包括类型和置信度
        line_thickness: int 方框宽度
    return:
        no return
    """
    tl = (
            line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1
    )  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]  # 如果没有指定就是随机生成的颜色作方框颜色
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))  # (x1 y1) (x2 y2)

    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)  # 画一个框
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(
            img,
            label,
            (c1[0], c1[1] - 2),
            0,
            tl / 3,
            [225, 255, 255],
            thickness=tf,
            lineType=cv2.LINE_AA,
        )

def post_process_opencv(outputs, model_h, model_w, img_h, img_w, thred_nms, thred_cond):
    conf = outputs[:, 4].tolist()
    c_x = outputs[:, 0] / model_w * img_w
    c_y = outputs[:, 1] / model_h * img_h
    w = outputs[:, 2] / model_w * img_w
    h = outputs[:, 3] / model_h * img_h
    p_cls = outputs[:, 5:]
    if len(p_cls.shape) == 1:
        p_cls = np.expand_dims(p_cls, 1)
    cls_id = np.argmax(p_cls, axis=1)

    p_x1 = np.expand_dims(c_x - w / 2, -1)
    p_y1 = np.expand_dims(c_y - h / 2, -1)
    p_x2 = np.expand_dims(c_x + w / 2, -1)
    p_y2 = np.expand_dims(c_y + h / 2, -1)  # x1 y1 x2 y2
    areas = np.concatenate((p_x1, p_y1, p_x2, p_y2), axis=-1)
    print(areas.shape)
    areas = areas.tolist()
    ids = cv2.dnn.NMSBoxes(areas, conf, thred_cond, thred_nms)  # 第三是概率阈值，第四是重叠面积大于nms就会去掉小的那个，避免多框重叠
    if len(ids) > 0:
        return np.array(areas)[ids], np.array(conf)[ids], cls_id[ids]
    else:
        return [], [], []

# 推理，这里设置的是默认值
def infer_image(net, img0, model_h, model_w, thred_nms=0.5, thred_cond=0.5):
    # print('infering image...')
    img = img0.copy()  #
    img = cv2.resize(img, [model_h, model_w])
    blob = cv2.dnn.blobFromImage(img, scalefactor=1 / 255.0, swapRB=True)  # 图像预处理 BGR->RGB
    net.setInput(blob)
    outs = net.forward()[0]  # 推论 cx cy w h 框内物体概率 A B C类型的概率
    det_boxes, scores, ids = post_process_opencv(outs, model_h, model_w, img0.shape[0], img0.shape[1], thred_nms,
                                                 thred_cond)
    return det_boxes, scores, ids

# 主线程：读取图像，计算中点颜色，画框

def m_detection(net, cap, model_h, model_w):
    '''
    多线程函数：模型推理
    :param net: cv2网络对象
    :param cap: videocapture对象
    :param model_h: 图像的高
    :param model_w: 图像的宽
    :return: 没有返回值
    '''
    global det_boxes_show  # 全局变量
    global scores_show
    global ids_show
    global InferDelay_show
    global capimg
    # while True:
    # success, img0 = cap.read()  # img0是单帧图像
    try:
        img0 = capimg.copy()
        if True:
            t1 = time.time()
            det_boxes, scores, ids = infer_image(net, img0, model_h, model_w, thred_nms=0.3, thred_cond=0.3)
            # 图形推理，返回：框、置信度、分类号，他们都是列表
            t2 = time.time()
            str_fps = "Infer_delay: %.2f" % (t2 - t1)  # 计算出延迟，这是一个字符串

            det_boxes_show = det_boxes
            scores_show = scores
            ids_show = ids
            InferDelay_show = str_fps

            # time.sleep(1)
    except:
        print('no img0 in mdetection!')
        time.sleep(3)
        pass

class m_detectServer(threading.Thread):
    def __init__(self, net, cap, model_h, model_w):
        super().__init__()
        self.net = net
        self.cap = cap
        self.model_h = model_h
        self.model_w = model_w
        self.__mEvent = threading.Event()
        self.__aliveflag = threading.Event()  # 用于停止线程的标识 1表示活着 0表示关停
        self.__mEvent.set()  # 运行，
        self.__aliveflag.set()  # 活着，

    def run(self):
        while self.__aliveflag.isSet():
            self.__mEvent.wait()
            m_detection(self.net, self.cap, self.model_h, self.model_w)
            time.sleep(0.5)

    def pause(self):
        print('YoloDetection pause!')
        self.__mEvent.clear()

    def resume(self):
        print('YoloDetection resume!')
        self.__mEvent.set()

    def stop(self):
        print('YoloDetection stop!')
        self.__mEvent.set()  # 1 将线程从暂停状态恢复, 如何已经暂停的话
        self.__aliveflag.clear()  # 0 设置为False

    def isRunning(self):
        if self.__mEvent.isSet():
            return True
        else:
            return False

# m_thread = threading.Thread(target=m_detection, args=([net, None, model_h, model_w]),
#                             daemon=True)  # 开一个线程，执行mdetection函数，
# m_thread.start()

###############################################################################

def posUpDown(command, spd):  # 抬头或低头动作
    if command == 'up':
        robot.lookUp()
    elif command == 'down':
        robot.lookDown()

class CVThread(threading.Thread):  # 提供：模式修改、画线、
    font = cv2.FONT_HERSHEY_SIMPLEX

    cameraDiagonalW = 64
    cameraDiagonalH = 48
    videoW = 640
    videoH = 480
    Y_lock = 0
    X_lock = 0
    tor = 27
    aspd = 0.005

    def __init__(self, *args, **kwargs):
        self.CVThreading = 0  # 标志 1 --do -- 0
        self.CVMode = 'none'  # 无/ 查找颜色/
        self.imgCV = None

        self.mov_x = None
        self.mov_y = None
        self.mov_w = None
        self.mov_h = None

        self.radius = 0
        self.box_x = None
        self.box_y = None
        self.drawing = 0

        self.findColorDetection = 0

        self.left_Pos1 = None
        self.right_Pos1 = None
        self.center_Pos1 = None

        self.left_Pos2 = None
        self.right_Pos2 = None
        self.center_Pos2 = None

        self.center = None

        super(CVThread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()  # 0

        self.avg = None
        self.motionCounter = 0
        self.lastMovtionCaptured = datetime.datetime.now()
        self.frameDelta = None
        self.thresh = None
        self.cnts = None

        self.CVCommand = 'forward'

    def mode(self, invar, imgInput):
        self.CVMode = invar
        self.imgCV = imgInput
        self.resume()

    # 可用的imgInput 图像绘制函数，【会返回处理后的图像回去】
    def elementDraw(self, imgInput):
        global det_boxes_show
        global scores_show
        global ids_show
        global InferDelay_show

        if self.CVMode == 'none':
            pass  # 什么也不做，直接把原图像返回回去就可以了

        elif self.CVMode == 'findColor':  # 查找颜色的实施步骤
            if self.findColorDetection:
                cv2.putText(imgInput, 'Target Detected', (40, 60), CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                self.drawing = 1
            else:
                cv2.putText(imgInput, 'Target Detecting', (40, 60), CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                self.drawing = 0

            if self.radius > 10 and self.drawing:
                cv2.rectangle(imgInput, (int(self.box_x - self.radius), int(self.box_y + self.radius)),
                              (int(self.box_x + self.radius), int(self.box_y - self.radius)), (255, 255, 255), 1)

        elif self.CVMode == 'findlineCV':  # 巡线
            if frameRender:
                pass  # 这里做了修改，为了不让显示的图像是被二值化的
                # imgInput = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
                # retval_bw, imgInput = cv2.threshold(imgInput, 0, 255, cv2.THRESH_OTSU)
                # imgInput = cv2.erode(imgInput, None, iterations=6) #呈现的img被二值化了

            # 画有关巡线检测的线
            try:
                if lineColorSet == 255:
                    cv2.putText(imgInput, ('Following White Line'), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(imgInput, ('Following White Line'), (230, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),
                                1, cv2.LINE_AA)
                elif lineColorSet == 0:  #
                    cv2.putText(imgInput, ('Following Black Line'), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(imgInput, ('Following Black Line'), (230, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),
                                1, cv2.LINE_AA)

                cv2.putText(imgInput, (self.CVCommand), (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
                            cv2.LINE_AA)
                cv2.putText(imgInput, (self.CVCommand), (230, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1,
                            cv2.LINE_AA)

                cv2.line(imgInput, (self.left_Pos1, (linePos_1 + 30)), (self.left_Pos1, (linePos_1 - 30)),
                         (255, 255, 255), 1)
                cv2.line(imgInput, ((self.left_Pos1 + 1), (linePos_1 + 30)), ((self.left_Pos1 + 1), (linePos_1 - 30)),
                         (0, 0, 0), 1)

                cv2.line(imgInput, (self.right_Pos1, (linePos_1 + 30)), (self.right_Pos1, (linePos_1 - 30)),
                         (255, 255, 255), 1)
                cv2.line(imgInput, ((self.right_Pos1 - 1), (linePos_1 + 30)), ((self.right_Pos1 - 1), (linePos_1 - 30)),
                         (0, 0, 0), 1)

                cv2.line(imgInput, (0, linePos_1), (640, linePos_1), (255, 255, 255), 1)
                cv2.line(imgInput, (0, linePos_1 + 1), (640, linePos_1 + 1), (0, 0, 0), 1)

                cv2.line(imgInput, (320 - findLineError, 0), (320 - findLineError, 480), (255, 255, 255), 1)
                cv2.line(imgInput, (320 + findLineError, 0), (320 + findLineError, 480), (255, 255, 255), 1)

                cv2.line(imgInput, (320 - findLineError + 1, 0), (320 - findLineError + 1, 480), (0, 0, 0), 1)
                cv2.line(imgInput, (320 + findLineError - 1, 0), (320 + findLineError - 1, 480), (0, 0, 0), 1)

                cv2.line(imgInput, (self.left_Pos2, (linePos_2 + 30)), (self.left_Pos2, (linePos_2 - 30)),
                         (255, 255, 255), 1)
                cv2.line(imgInput, (self.right_Pos2, (linePos_2 + 30)), (self.right_Pos2, (linePos_2 - 30)),
                         (255, 255, 255), 1)
                cv2.line(imgInput, (0, linePos_2), (640, linePos_2), (255, 255, 255), 1)

                cv2.line(imgInput, (self.left_Pos2 + 1, (linePos_2 + 30)), (self.left_Pos2 + 1, (linePos_2 - 30)),
                         (0, 0, 0), 1)
                cv2.line(imgInput, (self.right_Pos2 - 1, (linePos_2 + 30)), (self.right_Pos2 - 1, (linePos_2 - 30)),
                         (0, 0, 0), 1)
                cv2.line(imgInput, (0, linePos_2 + 1), (640, linePos_2 + 1), (0, 0, 0), 1)

                cv2.line(imgInput, ((self.center - 20), int((linePos_1 + linePos_2) / 2)),
                         ((self.center + 20), int((linePos_1 + linePos_2) / 2)), (0, 0, 0), 1)
                cv2.line(imgInput, ((self.center), int((linePos_1 + linePos_2) / 2 + 20)),
                         ((self.center), int((linePos_1 + linePos_2) / 2 - 20)), (0, 0, 0), 1)

                cv2.line(imgInput, ((self.center - 20), int((linePos_1 + linePos_2) / 2 + 1)),
                         ((self.center + 20), int((linePos_1 + linePos_2) / 2 + 1)), (255, 255, 255), 1)
                cv2.line(imgInput, ((self.center + 1), int((linePos_1 + linePos_2) / 2 + 20)),
                         ((self.center + 1), int((linePos_1 + linePos_2) / 2 - 20)), (255, 255, 255), 1)
            except:
                print('Draw trackLine element failed!')
                pass

        elif self.CVMode == 'watchDog':  # 观察移动物体
            if self.drawing:  # 框出移动物体的位置
                cv2.rectangle(imgInput, (self.mov_x, self.mov_y), (self.mov_x + self.mov_w, self.mov_y + self.mov_h),
                              (128, 255, 0), 1)

        return imgInput  # 返回处理后的图像

    def watchDog(self, imgInput):
        timestamp = datetime.datetime.now()
        gray = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.avg is None:
            print("[INFO] starting background model...")
            self.avg = gray.copy().astype("float")
            return 'background model'

        cv2.accumulateWeighted(gray, self.avg, 0.5)
        self.frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        self.thresh = cv2.threshold(self.frameDelta, 5, 255,
                                    cv2.THRESH_BINARY)[1]
        self.thresh = cv2.dilate(self.thresh, None, iterations=2)
        self.cnts = cv2.findContours(self.thresh.copy(), cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)
        self.cnts = imutils.grab_contours(self.cnts)
        # print('x')
        # loop over the contours
        for c in self.cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 5000:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (self.mov_x, self.mov_y, self.mov_w, self.mov_h) = cv2.boundingRect(c)  # 获取动作物体的位置信息
            self.drawing = 1
            self.motionCounter += 1
            self.lastMovtionCaptured = timestamp
            # robot.standUp()

        if (timestamp - self.lastMovtionCaptured).seconds >= 0.5:
            self.drawing = 0
            # robot.stayLow()
        self.pause()

    # 尝试调整方向
    def findLineTest(self, posInput, setCenter):  # 2
        checkBegin = 320 - 160
        if posInput == checkBegin:
            robot.robotCtrl.moveStart(speedMove, 'no', 'no')
            return

        if posInput > (setCenter + findLineError):
            self.CVCommand = 'Turning Right'

        elif posInput < (setCenter - findLineError):
            self.CVCommand = 'Turning Left'

        else:
            self.CVCommand = 'Forward'

    def findLineCtrl(self, posInput, setCenter):  # 2
        checkBegin = 320 - 160
        # 找不到线
        if posInput == 0 + checkBegin:
            robot.robotCtrl.moveStart(speedMove, 'no', 'no')
            return

        # 纠正方向
        if posInput > (setCenter + findLineError):  # Error就是SP，是死区
            # turnRight
            robot.right(speedMove)
            self.CVCommand = 'Turning Right'  # 转向状态
            print('Turning Right')

        elif posInput < (setCenter - findLineError):
            # turnLeft
            robot.left(speedMove)
            self.CVCommand = 'Turning Left'
            print('Turning Left')

        else:
            # forward
            robot.forward()
            self.CVCommand = 'Forward'
            print('Forward')

    def findlineCV(self, frame_image):  # CV巡线图像处理
        global lastupdatetime
        checkBegin = 320 - 160
        """
        巡线的函数
        :param frame_image:一个图像帧
        :return:
        """
        # 先转换图像的颜色
        # frame_bgr = frame_image
        # frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        frame_findline = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
        # 二值化：frame被改成了二值化图像 最后一个是处理方式
        retval, frame_findline = cv2.threshold(frame_findline, 0, 255, cv2.THRESH_OTSU)
        # 腐蚀图像，可以平滑图像，迭代6次
        frame_findline = cv2.erode(frame_findline, None, iterations=6)
        # 取某两行
        colorPos_1 = frame_findline[linePos_1]
        colorPos_2 = frame_findline[linePos_2]

        # print(len(colorPos_1)) #640
        # 切片
        #
        try:
            lineColorCount_Pos1 = np.sum(colorPos_1[320 - 160: 320 + 161] == lineColorSet)  # 看看这一行有多少个像素符合设置的巡线颜色
            lineColorCount_Pos2 = np.sum(colorPos_2[320 - 160: 320 + 161] == lineColorSet)

            lineIndex_Pos1 = np.where(colorPos_1[320 - 160: 320 + 161] == lineColorSet)  # 看看这一行符合设置的巡线颜色的像素在哪些列
            lineIndex_Pos2 = np.where(colorPos_2[320 - 160: 320 + 161] == lineColorSet)

            lineIndex_Pos1 = [x + checkBegin for x in lineIndex_Pos1]  # 黑色所在列数
            lineIndex_Pos2 = [x + checkBegin for x in lineIndex_Pos2]

            if lineColorCount_Pos1 == 0 + checkBegin:
                lineColorCount_Pos1 = 1 + checkBegin
            if lineColorCount_Pos2 == 0 + checkBegin:
                lineColorCount_Pos2 = 1 + checkBegin
            # 得出相关数据
            self.left_Pos1 = lineIndex_Pos1[0][lineColorCount_Pos1 - 1]  # 得出第一根线的最右边符合所求颜色的像素列数
            self.right_Pos1 = lineIndex_Pos1[0][0]  # 得出第一根线的最左边符合所求颜色的像素列数
            self.center_Pos1 = int((self.left_Pos1 + self.right_Pos1) / 2)

            self.left_Pos2 = lineIndex_Pos2[0][lineColorCount_Pos2 - 1]
            self.right_Pos2 = lineIndex_Pos2[0][0]
            self.center_Pos2 = int((self.left_Pos2 + self.right_Pos2) / 2)

            self.center = int((self.center_Pos1 + self.center_Pos2) / 2)  # 上线中 和 下线中 的中点
        except:
            center = None
            pass

        # 避障
        dist = ultra.checkdist()  # 获取面前的距离
        now_time = time.time()
        # print("ultradist" + str(dist))
        if dist < distanceCheck:  # 近了
            print("ultradist:" + str(dist) + "Stop!")

            if now_time - lastupdatetime > stopKeep:
                writeUsualRecord('Obstruction', 'None', capimg, 'obstructionrecord')
                lastupdatetime = now_time

            if dist < distavoidCheck:  # 距离低于0.05m
                print("Too close! Backward!")
                robot.robotCtrl.moveStart(speedMove, 'backward', 'no')
                time.sleep(1)
            else:
                robot.robotCtrl.moveStart(speedMove, 'no', 'no')
                time.sleep(1)

                # time.sleep(stopKeep)
                # self.pause()
        else:
            if Camera.CVMode == 'run':
                self.findLineCtrl(self.center, 320)  # 前进或纠正方向的动作函数
            else:
                self.findLineTest(self.center, 320)

        #     # robot.robotCtrl.moveStart(100, 'no', 'left')
        #     robot.robotCtrl.moveStop()
        #     # 记录异常
        #     writeUsualRecord('Obstruction', 'None', capimg, 'obstructionrecord')
        #     time.sleep(stopKeep)
        #     continue
        # else:  # 正常距离, 按原计划进行
        #     # robot.robotCtrl.moveStart(100, 'forward', 'no')
        #     if Camera.CVMode == 'run':
        #         self.findLineCtrl(self.center, 320)  # 纠正方向的动作函数
        #     else:
        #         self.findLineTest(self.center, 320)

        time.sleep(0.1)
        self.pause()

    def findColor(self, frame_image):
        """
           寻找颜色
        """
        hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, colorLower, colorUpper)  # 1
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        if len(cnts) > 0:
            self.findColorDetection = 1
            c = max(cnts, key=cv2.contourArea)
            ((self.box_x, self.box_y), self.radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            X = int(self.box_x)
            Y = int(self.box_y)
            error_Y = abs(240 - Y)

            if Y < 240 - CVThread.tor:
                # posUpDown('up', error_Y*CVThread.aspd)
                robot.lookUp(error_Y * CVThread.aspd)
            elif Y > 240 + CVThread.tor:
                # posUpDown('down', error_Y*CVThread.aspd)
                robot.lookDown(error_Y * CVThread.aspd)

        else:
            self.findColorDetection = 0
        self.pause()

    def pause(self):
        self.__flag.clear()  # 0

    def resume(self):
        self.__flag.set()  # 1

    def run(self):  # 开启摄像头后就开始跑这个 线程函数
        while 1:  # 会在后台循环，查CVMode变成什么了
            self.__flag.wait()
            if self.CVMode == 'none':
                robot.robotCtrl.moveStart(speedMove, 'no', 'no')  #
                self.pause()
                continue

            elif self.CVMode == 'findColor':
                self.CVThreading = 1
                self.findColor(self.imgCV)
                self.CVThreading = 0

            elif self.CVMode == 'findlineCV':  # CV寻线模式，只要这个模式开着，就得做这个函数
                self.CVThreading = 1
                self.findlineCV(self.imgCV)
                self.CVThreading = 0

            elif self.CVMode == 'watchDog':
                self.CVThreading = 1
                self.watchDog(self.imgCV)
                self.CVThreading = 0
            pass

class Functions(threading.Thread):  # 线程，用于

    def __init__(self, *args, **kwargs):
        super(Functions, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()
        self.funcMode = 'no'

    def pause(self):
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def keepDProcessing(self):
        dist = ultra.checkdist()

        if dist < distanceCheck - 0.1:
            robot.robotCtrl.moveStart(100, 'backward', 'no')
        elif dist > distanceCheck + 0.1:
            robot.robotCtrl.moveStart(100, 'forward', 'no')
        else:
            robot.robotCtrl.moveStop()

        time.sleep(0.1)

    # 自动避障
    def automaticProcessing(self):
        dist = ultra.checkdist()  # 获取面前的距离

        if dist < distanceCheck:  # 近了，左转
            robot.robotCtrl.moveStart(100, 'no', 'left')
            time.sleep(turningKeep)
        else:  # 正常距离，直行
            robot.robotCtrl.moveStart(100, 'forward', 'no')

        time.sleep(0.1)

    def funcProcessing(self):
        if self.funcMode == 'keepDistance':
            self.keepDProcessing()
        elif self.funcMode == 'automatic':
            self.automaticProcessing()

    def functionSelect(self, funcName):
        self.funcMode = funcName
        if self.funcMode == 'no':
            robot.robotCtrl.moveStart(speedMove, 'no', 'no')
            self.pause()
            robot.robotCtrl.moveStart(speedMove, 'no', 'no')
        else:
            self.resume()

    def run(self):
        while 1:
            self.__flag.wait()
            if self.funcMode == 'no':
                robot.robotCtrl.moveStart(speedMove, 'no', 'no')
                self.pause()
                robot.robotCtrl.moveStart(speedMove, 'no', 'no')
            else:
                self.funcProcessing()
                if self.funcMode == 'no':
                    robot.robotCtrl.moveStart(speedMove, 'no', 'no')
                    self.pause()
                    robot.robotCtrl.moveStart(speedMove, 'no', 'no')

# 这个方法主管动作模式
def commandAct(act, inputA):
    global directionCommand, turningCommand, speedMove, posUD
    robot.PIPPY.configPWM(act)
    if act == 'forward':  # 看看是什么动作？
        directionCommand = 'forward'
        robot.robotCtrl.moveStart(speedMove, directionCommand, turningCommand)
    elif act == 'backward':
        directionCommand = 'backward'
        robot.robotCtrl.moveStart(speedMove, directionCommand, turningCommand)
    elif act == 'left':
        turningCommand = 'left'
        robot.robotCtrl.moveStart(speedMove, directionCommand, turningCommand)
    elif act == 'right':
        turningCommand = 'right'
        robot.robotCtrl.moveStart(speedMove, directionCommand, turningCommand)
    elif act == 'DS':
        directionCommand = 'no'
        robot.robotCtrl.moveStart(speedMove, directionCommand, turningCommand)
    elif act == 'TS':
        turningCommand = 'no'
        robot.robotCtrl.moveStart(speedMove, directionCommand, turningCommand)
    elif 'wsB' in act:
        speedMove = int(act.split()[1])
    elif 'grab' == act:
        robot.standUp()  # standUp
        pass
    elif 'loose' == act:
        robot.stayLow()  # stayLow
        pass
    elif 'up' == act:
        # look up
        # robot.standUp()
        robot.lookUp()
        time.sleep(0.1)
        pass
    elif 'down' == act:
        # look down
        # robot.stayLow()
        robot.lookDown()
        time.sleep(0.1)
        pass
    elif 'lookleft' == act:
        robot.PIPPY.pitchRoll(0, 15)

    elif 'lookright' == act:
        robot.PIPPY.pitchRoll(0, -15)

    # 动作：巡线！
    elif 'trackLine' == act:  # 启动巡线
        Camera.modeSelect = 'findlineCV'
        Camera.CVMode = 'run'
        print("Start Track Line!!")
        m_thread.resume()
        time.sleep(0.1)
        pass

    elif 'trackLineOff' == act:  # 停止巡线
        Camera.modeSelect = 'none'
        print("Stop Track Line!!")
        m_thread.pause()
        time.sleep(0.1)
        robot.robotCtrl.moveStart(speedMove, 'no', 'no')
    # 动作：开启关闭yolo
    elif 'yoloOpen' == act:
        print("Open Yolo Mode!")
        m_thread.resume()
        time.sleep(0.1)

    elif 'yoloOff' == act:
        print("Stop Yolo Mode!")
        m_thread.pause()
        time.sleep(0.1)

    elif 'KD' == act:
        func.functionSelect('keepDistance')
    # 动作：自动避障
    elif 'automatic' == act:
        func.functionSelect('automatic')

    elif 'automaticOff' == act:
        func.functionSelect('no')
    # 动作：自动避障
    elif 'automatic' == act:
        func.functionSelect('automatic')

    elif 'automaticOff' == act:
        func.functionSelect('no')

    elif 'speech' == act:
        robot.robotCtrl.functionSelect('steady')
        func.functionSelect('no')

    elif 'speechOff' == act:
        robot.robotCtrl.functionSelect('no')
        func.functionSelect('no')

    '''
    elif 'police' == act:
        alterMove.startPoliceLight()

    elif 'policeOff' == act:
        alterMove.lightStop()


    elif 'Switch_1_on' == act:
        alterMove.switchCtrl(1, 1)

    elif 'Switch_2_on' == act:
        alterMove.switchCtrl(2, 1)

    elif 'Switch_3_on' == act:
        alterMove.switchCtrl(3, 1)

    elif 'Switch_1_off' == act:
        alterMove.switchCtrl(1, 0)

    elif 'Switch_2_off' == act:
        alterMove.switchCtrl(2, 0)

    elif 'Switch_3_off' == act:
        alterMove.switchCtrl(3, 0)


    elif act == 'breathLight':
        alterMove.startBreathLight(inputA[0], inputA[1], inputA[2])
    elif act == 'setWS':
        alterMove.lightStop()
        alterMove.set2812(inputA[0], inputA[1], inputA[2])

    elif act == 'looks':
        if inputA == 'laugh':
            screen.showLooks('laugh')

        else:
            screen.oledShowText(inputA, 0, 0)
    '''

##############################################################################
# 开启线程做检测
m_thread = m_detectServer(net, None, model_h, model_w)
m_thread.start()
m_thread.pause()

func = Functions()
func.start()
