#!/usr/bin/env python3
import numpy as np
import cv2
from hobot_dnn import pyeasy_dnn as dnn
import time
import ctypes
import json 
import sys
import colorsys
import signal
import os
# ethercat_package
import ec_def
import spi_rw
import ec_status
import spidev
import data_timely
# ethercat_end
import threading

# 用于线程同步的事件
inference_finished = threading.Event()
ethercat_finished = threading.Event()

class hbSysMem_t(ctypes.Structure):
    _fields_ = [
        ("phyAddr",ctypes.c_double),
        ("virAddr",ctypes.c_void_p),
        ("memSize",ctypes.c_int)
    ]

class hbDNNQuantiShift_yt(ctypes.Structure):
    _fields_ = [
        ("shiftLen",ctypes.c_int),
        ("shiftData",ctypes.c_char_p)
    ]

class hbDNNQuantiScale_t(ctypes.Structure):
    _fields_ = [
        ("scaleLen",ctypes.c_int),
        ("scaleData",ctypes.POINTER(ctypes.c_float)),
        ("zeroPointLen",ctypes.c_int),
        ("zeroPointData",ctypes.c_char_p)
    ]    

class hbDNNTensorShape_t(ctypes.Structure):
    _fields_ = [
        ("dimensionSize",ctypes.c_int * 8),
        ("numDimensions",ctypes.c_int)
    ]

class hbDNNTensorProperties_t(ctypes.Structure):
    _fields_ = [
        ("validShape",hbDNNTensorShape_t),
        ("alignedShape",hbDNNTensorShape_t),
        ("tensorLayout",ctypes.c_int),
        ("tensorType",ctypes.c_int),
        ("shift",hbDNNQuantiShift_yt),
        ("scale",hbDNNQuantiScale_t),
        ("quantiType",ctypes.c_int),
        ("quantizeAxis", ctypes.c_int),
        ("alignedByteSize",ctypes.c_int),
        ("stride",ctypes.c_int * 8)
    ]

class hbDNNTensor_t(ctypes.Structure):
    _fields_ = [
        ("sysMem",hbSysMem_t * 4),
        ("properties",hbDNNTensorProperties_t)
    ]


class Yolov5PostProcessInfo_t(ctypes.Structure):
    _fields_ = [
        ("height",ctypes.c_int),
        ("width",ctypes.c_int),
        ("ori_height",ctypes.c_int),
        ("ori_width",ctypes.c_int),
        ("score_threshold",ctypes.c_float),
        ("nms_threshold",ctypes.c_float),
        ("nms_top_k",ctypes.c_int),
        ("is_pad_resize",ctypes.c_int)
    ]

libpostprocess = ctypes.CDLL('/usr/lib/libpostprocess.so') 

get_Postprocess_result = libpostprocess.Yolov5PostProcess
get_Postprocess_result.argtypes = [ctypes.POINTER(Yolov5PostProcessInfo_t)]  
get_Postprocess_result.restype = ctypes.c_char_p  

def get_TensorLayout(Layout):
    if Layout == "NCHW":
        return int(2)
    else:
        return int(0)

def bgr2nv12_opencv(image):
    height, width = image.shape[0], image.shape[1]
    area = height * width
    yuv420p = cv2.cvtColor(image, cv2.COLOR_BGR2YUV_I420).reshape((area * 3 // 2,))
    y = yuv420p[:area]
    uv_planar = yuv420p[area:].reshape((2, area // 4))
    uv_packed = uv_planar.transpose((1, 0)).reshape((area // 2,))

    nv12 = np.zeros_like(yuv420p)
    nv12[:height * width] = y
    nv12[height * width:] = uv_packed
    return nv12

def get_hw(pro):
    if pro.layout == "NCHW":
        return pro.shape[2], pro.shape[3]
    else:
        return pro.shape[1], pro.shape[2]

def print_properties(pro):
    print("tensor type:", pro.tensor_type)
    print("data type:", pro.dtype)
    print("layout:", pro.layout)
    print("shape:", pro.shape)

def signal_handler(signal, frame):
    print("\nExiting program")
    sys.exit(0)

def is_usb_camera(device):
    try:
        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            return False
        cap.release()
        return True
    except Exception:
        return False

def find_first_usb_camera():
    video_devices = [os.path.join('/dev', dev) for dev in os.listdir('/dev') if dev.startswith('video')]
    for dev in video_devices:
        if is_usb_camera(dev):
            return dev
    return None

def perform_inference(models, img_file):
    global inference_finished
    try:
        # 根据模型进行前向推理
        h, w = get_hw(models[0].inputs[0].properties)
        des_dim = (w, h)
        resized_data = cv2.resize(img_file, des_dim, interpolation=cv2.INTER_AREA)
        nv12_data = bgr2nv12_opencv(resized_data)
        outputs = models[0].forward(nv12_data)
        yolov5_postprocess_info = Yolov5PostProcessInfo_t()
        yolov5_postprocess_info.height = h
        yolov5_postprocess_info.width = w
        org_height, org_width = img_file.shape[0:2]
        yolov5_postprocess_info.ori_height = org_height
        yolov5_postprocess_info.ori_width = org_width
        yolov5_postprocess_info.score_threshold = 0.4 
        yolov5_postprocess_info.nms_threshold = 0.45
        yolov5_postprocess_info.nms_top_k = 20
        yolov5_postprocess_info.is_pad_resize = 0
        output_tensors = (hbDNNTensor_t * len(models[0].outputs))()

        for i in range(len(models[0].outputs)):
            output_tensors[i].properties.tensorLayout = get_TensorLayout(outputs[i].properties.layout)
            # print(output_tensors[i].properties.tensorLayout)
            if (len(outputs[i].properties.scale_data) == 0):
                output_tensors[i].properties.quantiType = 0
                output_tensors[i].sysMem[0].virAddr = ctypes.cast(outputs[i].buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), ctypes.c_void_p)
            else:
                output_tensors[i].properties.quantiType = 2       
                output_tensors[i].properties.scale.scaleData = outputs[i].properties.scale_data.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
                output_tensors[i].sysMem[0].virAddr = ctypes.cast(outputs[i].buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)), ctypes.c_void_p)
            
            for j in range(len(outputs[i].properties.shape)):
                output_tensors[i].properties.validShape.dimensionSize[j] = outputs[i].properties.shape[j]

            libpostprocess.Yolov5doProcess(output_tensors[i], ctypes.pointer(yolov5_postprocess_info), i)

        result_str = get_Postprocess_result(ctypes.pointer(yolov5_postprocess_info))  
        result_str = result_str.decode('utf-8')  
        data = json.loads(result_str[16:])  

        # 按框面积排序
        data.sort(key=lambda x: (x['bbox'][2] - x['bbox'][0]) * (x['bbox'][3] - x['bbox'][1]), reverse=True)

        # 取最大的三个框
        top_three = data[:3]

        # 打印前三名目标的类别与中心位置
        for i, result in enumerate(top_three, start=0):
            bbox = result['bbox']
            id = result['id']
            name = result['name']
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            data_timely.result_ID[i] = id
            data_timely.result_Position_x[i] = int(center_x)
            data_timely.result_Position_y[i] = int(center_y)
            # print(f"Outputting data for target {i}: Class ID: {data_timely.result_ID[i]}, Class: {name}, Center Position: ({data_timely.result_Position_x[i]}, {data_timely.result_Position_y[i]})")
            # time.sleep(0.01)
    except Exception as e:
        print(f"Error during inference: {e}")

    finally:
        # 推理完成，设置事件
        inference_finished.set()


def perform_ethercat(spi):
    global ethercat_finished
    while True:
        try:
            #print("perform_ethercat working")
            if ec_def.bEscIntEnabled == 0:
                ec_status.free_run(spi)
            ec_status.al_event(spi)
        except Exception as e:
            print(f"Error during EtherCAT event handling: {e}")
            traceback.print_exc()  # 新增：打印完整堆栈
        time.sleep(0.1)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    # 载入模型
    models = dnn.load('yolov5s_672x672_nv12.bin')

    # 摄像头初始化
    if len(sys.argv) > 1: video_device = sys.argv[1]
    else: video_device = find_first_usb_camera()
    if video_device is None:
        print("No USB camera found.")
        sys.exit(-1)
    print(f"Opening video device: {video_device}")
    cap = cv2.VideoCapture(video_device)
    if(not cap.isOpened()): exit(-1)
    print("Open usb camera successfully")

    # spi初始化
    spi = spidev.SpiDev()
    spi.open(1, 1)
    spi.max_speed_hz = 8000000
    spi.mode = 0b11
    # ax58100初始化
    ec_status.ECAT_init(spi)

    # 启动 EtherCAT 事件处理线程
    ethercat_thread = threading.Thread(target=perform_ethercat, args=(spi,))
    ethercat_thread.daemon = True  # 设置为守护线程，主线程退出时自动退出
    ethercat_thread.start()

    # 循环推理输出
    while True:
        ret, img_file = cap.read()
        if img_file is None:
            print("Failed to get image from usb camera")
        else:
            # 重置事件
            inference_finished.clear()

            # 启动推理
            perform_inference(models, img_file)

            # 阻塞直到推理完成
            inference_finished.wait()

    cap.release()
    cv2.destroyAllWindows()