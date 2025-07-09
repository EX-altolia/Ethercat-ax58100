import ec_def
import spi_rw
import ec_status
import time
import spidev




# spi设备初始化
spi = spidev.SpiDev()
spi.open(1, 1)
spi.max_speed_hz = 12000000
spi.mode = 0b11
# ax58100初始化
ec_status.ECAT_init(spi)


'''
test_0x0E08 = spi_rw.spi_read_32(spi, 0x0E08)
print(spi_rw.BytesToHex(test_0x0E08))
'''

# 工作循环
while True:
    if ec_def.bEscIntEnabled == 0:
        ec_status.free_run(spi)
    ec_status.al_event(spi)
    # print(ec_def.nAlStatus,ec_def.EscAlEvent, ec_def.bEscIntEnabled)
    time.sleep(0.02)