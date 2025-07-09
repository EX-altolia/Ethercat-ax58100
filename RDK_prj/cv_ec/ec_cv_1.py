#!/usr/bin/env python3
import numpy as np
import cv2
import time
import ctypes
import json 
import sys
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

def detect_ball(frame):
    """优化后的小球检测函数，适应反光场景"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 调整红色阈值，提高饱和度要求以减少反光影响
    lower_red1 = np.array([0, 120, 100])  # 增加饱和度下限
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 120, 100])
    upper_red2 = np.array([180, 255, 255])

    # 合并红色掩膜
    mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    # 形态学处理优化（使用椭圆核，增强孔洞填充）
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)  # 先闭运算填充
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)  # 后开运算去噪

    # 高斯模糊减少高频噪声
    mask_blur = cv2.GaussianBlur(mask, (5, 5), 0)

    # 轮廓分析替代霍夫圆检测
    contours, _ = cv2.findContours(mask_blur, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_circle = None
    max_weight = 0

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:  # 忽略小面积噪声
            continue

        # 计算圆形度筛选
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)

        # 圆形度阈值和面积加权评分
        if circularity > 0.6:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            radius = int(radius)
            if 10 <= radius <= 200:
                # 综合圆形度和面积计算权重
                weight = circularity * area
                if weight > max_weight:
                    best_circle = ((int(x), int(y)), radius)
                    max_weight = weight

    if best_circle:
        # 颜色后验证（检查检测区域颜色一致性）
        (center, radius) = best_circle
        # 生成验证掩膜
        validation_mask = np.zeros_like(mask)
        cv2.circle(validation_mask, center, radius, 255, -1)
        # 计算红色像素比例
        red_pixels = cv2.countNonZero(cv2.bitwise_and(mask, validation_mask))
        total_pixels = np.pi * (radius ** 2)

        if total_pixels > 0 and red_pixels / total_pixels > 0.4:  # 红色占比阈值
            return center, radius

    return (0, 0), 0

def perform_cv_detection(img_file):
    global inference_finished
    try:
        prev_center = (data_timely.result_Position_x, data_timely.result_Position_y)
        prev_time = data_timely.prev_time if hasattr(data_timely, 'prev_time') else time.time()

        (x, y), radius = detect_ball(img_file)

        current_time = time.time()
        dt = current_time - prev_time

        if radius > 0:
            current_center = (x, y)
            dx = current_center[0] - prev_center[0]
            dy = current_center[1] - prev_center[1]

            if dt > 0:
                speed_x = dx / dt
                speed_y = dy / dt
                speed = np.sqrt(speed_x ** 2 + speed_y ** 2)

                if speed_x != 0:
                    direction = np.arctan2(speed_y, speed_x) * 180 / np.pi
                else:
                    direction = 90 if speed_y > 0 else -90 if speed_y < 0 else 0

                # 将速度和方向转换为 8 位整数
                data_timely.result_Speed = int(np.clip(speed, 0, 255))
                data_timely.result_Direction = int(np.clip(direction, 0, 255))
            else:
                data_timely.result_Speed = 0
                data_timely.result_Direction = 0

            # 将位置转换为 16 位整数
            data_timely.result_Position_x = int(np.clip(x, 0, 65535))
            data_timely.result_Position_y = int(np.clip(y, 0, 65535))
        else:
            data_timely.result_Position_x = 0
            data_timely.result_Position_y = 0
            data_timely.result_Speed = 0
            data_timely.result_Direction = 0

        data_timely.prev_time = current_time

    except Exception as e:
        print(f"Error during CV detection: {e}")

    finally:
        # 推理完成，设置事件
        inference_finished.set()


def perform_ethercat(spi):
    global ethercat_finished
    while True:
        try:
            if ec_def.bEscIntEnabled == 0:
                ec_status.free_run(spi)
            ec_status.al_event(spi)
        except Exception as e:
            print(f"Error during EtherCAT event handling: {e}")
        time.sleep(0.1)


if __name__ == '__main__':

    # 摄像头初始化
    if len(sys.argv) > 1: 
        video_device = sys.argv[1]
    else:
        video_device = find_first_usb_camera()
    if video_device is None:
        print("No USB camera found.")
        sys.exit(-1)
    print(f"Opening video device: {video_device}")
    cap = cv2.VideoCapture(video_device)
    if not cap.isOpened():
        exit(-1)
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

    data_timely.prev_time = time.time()

    # 循环推理输出
    while True:
        ret, img_file = cap.read()
        if img_file is None:
            print("Failed to get image from usb camera")
        else:
            # 重置事件
            inference_finished.clear()

            # 启动推理检测
            perform_cv_detection(img_file)

            # 阻塞直到推理完成
            inference_finished.wait()

    cap.release()
    cv2.destroyAllWindows()