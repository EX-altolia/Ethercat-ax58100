import serial
import time

# 配置串口参数（根据实际修改）
SERIAL_PORT = '/dev/ttyS1'  # Linux串口名，如ttyS1、ttyUSB0等
BAUDRATE = 115200

def main():
    try:
        # 打开串口
        with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1) as ser:
            print(f"已连接到串口: {SERIAL_PORT} @ {BAUDRATE}bps")
            print("等待接收数据...")
            
            while True:
                # 读取数据
                data = ser.readline().decode('utf-8').strip()
                
                if data:
                    try:
                        # 解析为整数
                        num = int(data)
                        print(f"收到: {num}")
                        
                        # 加一处理
                        result = num + 1
                        
                        # 返回结果
                        ser.write(f"{result}\n".encode('utf-8'))
                        print(f"已返回: {result}")
                        
                    except ValueError:
                        print(f"收到无效数据: {data}")
                
                # 短暂休眠避免CPU占用过高
                time.sleep(0.01)
                
    except serial.SerialException as e:
        print(f"串口错误: {e}")
    except KeyboardInterrupt:
        print("\n程序已停止")
    except Exception as e:
        print(f"其他错误: {e}")

if __name__ == "__main__":
    main()