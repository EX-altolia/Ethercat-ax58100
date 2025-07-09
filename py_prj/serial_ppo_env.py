import gym
import numpy as np
import onnxruntime as ort
import serial
import time

# 配置串口参数（根据实际修改）
SERIAL_PORT = 'COM11'  # Windows串口名，如COM3、COM4等
BAUDRATE = 115200

def main():
    try:
        # 打开串口
        with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser:
            print(f"已连接到串口: {SERIAL_PORT} @ {BAUDRATE}bps")

            # 初始化环境
            env = gym.make("BipedalWalkerHardcore-v3")
            state = env.reset()  # 初始化状态
            total_reward = 0
            step_count = 0
            done = False

            while not done:
                # 将观测数据转换为适合发送的格式
                state_str = ' '.join(map(str, state))

                # 发送环境信息
                ser.write(f"{state_str}\n".encode('utf-8'))
                print(f"已发送环境信息: {state_str}")

                # 接收模型返回的信息
                response = ser.readline().decode('utf-8').strip()
                if response:
                    try:
                        action = np.array(list(map(float, response.split())))
                        print(f"收到动作: {action}")

                        # 与环境交互
                        next_obs, reward, done, info = env.step(action.flatten())
                        env.render()
                        if done:
                            next_obs = env.reset()

                        total_reward += reward
                        step_count += 1
                        print(f'At step {step_count}, reward = {reward}, done = {done}')

                        state = next_obs

                    except ValueError:
                        print(f"收到无效响应: {response}")
                else:
                    print("接收超时，未收到响应")

            print(f'Total reward: {total_reward}')

    except serial.SerialException as e:
        print(f"串口错误: {e}")
        print(f"提示: 请检查串口名是否正确（当前: {SERIAL_PORT}）")
    except Exception as e:
        print(f"其他错误: {e}")

if __name__ == "__main__":
    main()