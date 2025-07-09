import spidev
import time
import ec_def
import data_timely
MAX_PD_INPUT_SIZE = 0x0040
MAX_PD_OUTPUT_SIZE = 0x0040
MAX_MB_INPUT_SIZE = 0x0040
MAX_MB_OUTPUT_SIZE = 0x0040


def BytesToHex(num):
    # 将整数转换为 16 位的十六进制字符串，不足 16 位时前面补 0
    hex_str = '{:016X}'.format(num)
    # 按每 4 位分割十六进制字符串，并使用下划线连接
    formatted_str = '_'.join([hex_str[i:i+4] for i in range(0, len(hex_str), 4)])
    # 添加 0x 前缀
    return '0x' + formatted_str



# 初始化 SPI 设备
def init_spi():
    spi = spidev.SpiDev()
    # 设置 spi 频率为 12MHz
    spi.max_speed_hz = 1200000
    spi.open(1, 1)
    return spi


def spi_read_8(spi, address):
    temp = (address << 3) | 0x02
    send_buffer = [(temp >> 8) & 0xFF, temp & 0xFF, 0xFF]
    resp = spi.xfer2(send_buffer)
    return resp[2]

# 读取 16 位数据
def spi_read_16(spi, address):
    temp = (address << 3) | 0x02
    send_buffer = [(temp >> 8) & 0xFF, temp & 0xFF, 0x00, 0xFF]
    resp = spi.xfer2(send_buffer)
    return (resp[3] << 8) | resp[2]

# 读取 32 位数据
def spi_read_32(spi, address):
    temp = (address << 3) | 0x02
    send_buffer = [(temp >> 8) & 0xFF, temp & 0xFF, 0x00, 0x00, 0x00, 0xFF]
    resp = spi.xfer2(send_buffer)
    return (resp[5] << 24) | (resp[4] << 16) | (resp[3] << 8) | resp[2]

def spi_write_8(spi, address, data):
    temp = (address << 3) | 0x04
    send_buffer = [(temp >> 8) & 0xFF, temp & 0xFF, data]
    spi.xfer2(send_buffer)
    return


def spi_write_16(spi, address, data):
    temp = (address << 3) | 0x04
    send_buffer = [(temp >> 8) & 0xFF, temp & 0xFF, data & 0xFF, (data >> 8) & 0xFF]
    #print(send_buffer, address)
    spi.xfer2(send_buffer)
    return



# 写入输入数据
def writeinputdata(spi):
    default_id = 0  # 无效ID默认值（根据需求调整）
    default_pos = 320  # 坐标默认值（根据需求调整）
    
    for i in range(ec_def.nPdInputSize):
        address = ec_def.nEscAddrInputData + i
        if i == 0:
            data = int(data_timely.result_Speed) & 0xFF
        elif i == 1:
            raw_x = int(data_timely.result_Position_x)
            data = raw_x & 0xFF
        elif i == 2:
            raw_x = int(data_timely.result_Position_x)
            data = (raw_x & 0xFF00) >> 8
        elif i == 3:
            raw_y = int(data_timely.result_Position_y)
            data = raw_y & 0xFF
        elif i == 4:
            raw_y = int(data_timely.result_Position_y)
            data = (raw_y & 0xFF00) >> 8   
        elif i == 5:
            data = int(data_timely.result_Direction & 0xFF)   

        
        spi_write_8(spi, address, data)

def readoutputdata(spi):
    # print(ec_def.nEscAddrOutputData)
    try:
        for i in range(ec_def.nPdOutputSize):
            if i == 0:
                ec_def.aPdOutputData[i] = spi_read_8(spi, ec_def.nEscAddrOutputData + i)
                # print(ec_def.aPdOutputData[i])
            elif i == 1:
                ec_def.aPdOutputData[i] = spi_read_8(spi, ec_def.nEscAddrOutputData + i)
            elif i == 2:
                ec_def.aPdOutputData[i] = spi_read_8(spi, ec_def.nEscAddrOutputData + i)
            elif i == 3:
                ec_def.aPdOutputData[i] = spi_read_8(spi, ec_def.nEscAddrOutputData + i)
            elif i == 4:
                ec_def.aPdOutputData[i] = spi_read_8(spi, ec_def.nEscAddrOutputData + i)
            else:break
        #print("get output data")
        return
    except:
        print("no output data")
        return
    