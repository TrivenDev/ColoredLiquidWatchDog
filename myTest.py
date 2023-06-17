import random
import cv2
import numpy as np
import time
from threading import Thread

from cv2 import getTickCount, getTickFrequency

import models.colorList
from models.compareArray import compareArray

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
    color = color or [random.randint(0, 255) for _ in range(3)] #如果没有指定就是随机生成的颜色作方框颜色
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3])) #(x1 y1) (x2 y2)


    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA) #画一个框
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


def infer_image(net, img0, model_h, model_w, thred_nms=0.3, thred_cond=0.3):
    img = img0.copy()
    img = cv2.resize(img, [model_h, model_w])
    blob = cv2.dnn.blobFromImage(img, scalefactor=1 / 255.0, swapRB=True)  # 图像预处理 BGR->RGB
    net.setInput(blob)
    outs = net.forward()[0]  # 推论 cx cy w h 框内物体概率 A B C类型的概率
    det_boxes, scores, ids = post_process_opencv(outs, model_h, model_w, img0.shape[0], img0.shape[1], thred_nms,
                                                 thred_cond)
    return det_boxes, scores, ids


global det_boxes_show

global scores_show

global ids_show

global InferDelay_show


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
    while True:
        success, img0 = cap.read()  # img0是单帧图像
        if success:
            t1 = time.time()
            det_boxes, scores, ids = infer_image(net, img0, model_h, model_w, thred_nms=0.4, thred_cond=0.3)
            # 图形推理，返回：框、置信度、分类号，他们都是列表
            t2 = time.time()
            str_fps = "Inference delay: %.2f" % (t2 - t1)  # 计算出延迟，这是一个字符串

            det_boxes_show = det_boxes
            scores_show = scores
            ids_show = ids
            InferDelay_show = str_fps

            # time.sleep(1)


if __name__ == "__main__":
    dic_labels = {0: 'onground',
                  1: 'leakage',
                  }  # 类别

    model_h = 320  # 图像尺寸 高640 宽640
    model_w = 320
    file_model = 'models/best13c-320.onnx'  # onnx模型文件
    net = cv2.dnn.readNet(file_model)  # 适用cv2的dnn网络，套用onnx模型

    video = 0  # 视频来源，填写路径或摄像头
    cap = cv2.VideoCapture(video)


    m_thread = Thread(target=m_detection, args=([net, cap, model_h, model_w]), daemon=True)  # 开一个线程，执行mdetection函数，
    m_thread.start()

    global det_boxes_show
    global scores_show
    global ids_show
    global InferDelay_show

    det_boxes_show = []  # 每个元素是：[ x1 y1 x2 y2 ]

    scores_show = []  # 置信度

    ids_show = []  # 分类号

    InferDelay_show = ""
    #主线程：读取图像，计算中点颜色，画框
    while True:
        loop_start = getTickCount()
        success, img0 = cap.read()  # 读取图像
        if success:
            for box, score, id in zip(det_boxes_show, scores_show, ids_show):  # 意思是，从这三列表中，分别取一个，组合在一起
                #计算颜色
                xmid, ymid = int((box[0] + box[2]) / 2),int( (box[1] + box[3]) / 2)  # 这就是中点坐标
                hsv = cv2.cvtColor(img0, cv2.COLOR_BGR2HSV)
                hsv_value = hsv[ymid, xmid]
                print('HSV:', hsv_value, 'Location:[',xmid,',',ymid,']')
                colors_dict = colorList.getColorList()  # 颜色的列表
                color_confirm = ''
                for c, hsv_range in colors_dict.items():
                    if compareArray(hsv_value, hsv_range[0], hsv_range[1]):
                        color_confirm = c
                #方框左上角的文字
                label = '%s-%s:%.2f' % (color_confirm,dic_labels[id], score)

                plot_one_box(box, img0, color=(255, 0, 0), label=label, line_thickness=None)  #根据坐标、类别、置信度 画框
                #计算中点 写中点颜色

            str_InferDelay = InferDelay_show

            cv2.putText(img0, str_InferDelay, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 0), 2) #写rate
            #计算一个循环之后的时间
            loop_time = getTickCount() - loop_start
            total_time = loop_time / (getTickFrequency())
            FPS = 1 / total_time
            # 显示帧数
            cv2.putText(img0, 'FPS:%.2f'%(FPS), (5, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255),2)

            cv2.imshow("video", img0) #在窗口中展示
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
