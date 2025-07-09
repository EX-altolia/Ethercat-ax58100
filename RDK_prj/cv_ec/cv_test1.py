import cv2
import numpy as np
import time

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
    import os
    video_devices = [os.path.join('/dev', dev) for dev in os.listdir('/dev') if dev.startswith('video')]
    for dev in video_devices:
        if is_usb_camera(dev):
            return dev
    return None

def usb_camera_ball_detection():
    """使用USB摄像头实时检测小球位置"""
    # 查找可用的USB摄像头
    video_device = find_first_usb_camera()
    if video_device is None:
        print("No USB camera found.")
        return

    # 初始化摄像头
    cap = cv2.VideoCapture(video_device)

    if not cap.isOpened():
        print("无法打开摄像头，请检查：")
        print("1. 摄像头是否正确连接")
        print("2. 其他程序是否占用摄像头")
        print("3. 尝试更换摄像头索引号(0/1/2)")
        return

    # 设置分辨率
    width, height = 640, 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    prev_center = (0, 0)
    prev_time = time.time()

    try:
        while True:
            # 读取帧
            ret, frame = cap.read()
            if not ret:
                print("无法获取帧")
                break

            # 检测小球
            (x, y), radius = detect_ball(frame)

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

                    print(f"小球中心点坐标: ({x}, {y}), 速度: {speed:.2f} 像素/秒, 速度方向: {direction:.2f} 度")
                else:
                    print(f"小球中心点坐标: ({x}, {y}), 速度: 0 像素/秒, 速度方向: 0 度")

                prev_center = current_center
            else:
                print("未检测到小球")

            prev_time = current_time

    finally:
        # 释放资源
        cap.release()
        print("摄像头资源已释放")


if __name__ == "__main__":
    usb_camera_ball_detection()