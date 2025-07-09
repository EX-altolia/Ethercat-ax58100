# 协议相关变量定义，主要为ProcessData和MailBox
MAX_RX_PDOS = 0x0001
MAX_TX_PDOS = 0x0001
MIN_PD_WRITE_ADDRESS = 0x1000
MAX_PD_WRITE_ADDRESS = 0x2000
MIN_PD_READ_ADDRESS = 0x1000
MAX_PD_READ_ADDRESS = 0x2000
NO_OF_PD_INPUT_BUFFER = 0x0003
NO_OF_PD_OUTPUT_BUFFER = 0x0003

MAX_PD_INPUT_SIZE = 0x0040
MAX_PD_OUTPUT_SIZE = 0x0040
MAX_MB_INPUT_SIZE = 0x0040
MAX_MB_OUTPUT_SIZE = 0x0040
MIN_MBX_SIZE = 0x0020
MAX_MBX_SIZE = 0x0400
MIN_MBX_WRITE_ADDRESS = 0x1000
MIN_MBX_READ_ADDRESS = 0x1000
MAX_MBX_WRUTE_ADDRESS = 0x2000
MAX_MBX_READ_ADDRESS = 0x2000
# 初始的状态变量
STATE_INIT = 0x01
STATE_PREOP = 0x02
STATE_BOOT = 0x03
STATE_SAFEOP = 0x04
STATE_OP = 0x08
STATE_MASK = 0x0F
STATE_CHANGE = 0x10
STATE_ERRACK = 0x10
STATE_ERROR = 0x10
# 状态转移变量
INIT_2_INIT = ((STATE_INIT << 4) | STATE_INIT)
INIT_2_PREOP = ((STATE_INIT << 4) | STATE_PREOP)
INIT_2_SAFEOP = ((STATE_INIT << 4) | STATE_SAFEOP)
INIT_2_OP = ((STATE_INIT << 4) | STATE_OP)
PREOP_2_INIT = ((STATE_PREOP << 4) | STATE_INIT)
PREOP_2_PREOP = ((STATE_PREOP << 4) | STATE_PREOP)
PREOP_2_SAFEOP = ((STATE_PREOP << 4) | STATE_SAFEOP)
PREOP_2_OP = ((STATE_PREOP << 4) | STATE_OP)
SAFEOP_2_INIT = ((STATE_SAFEOP << 4) | STATE_INIT)
SAFEOP_2_PREOP = ((STATE_SAFEOP << 4) | STATE_PREOP)
SAFEOP_2_SAFEOP = ((STATE_SAFEOP << 4) | STATE_SAFEOP)
SAFEOP_2_OP = ((STATE_SAFEOP << 4) | STATE_OP)
OP_2_INIT = ((STATE_OP << 4) | STATE_INIT)
OP_2_PREOP = ((STATE_OP << 4) | STATE_PREOP)
OP_2_SAFEOP = ((STATE_OP << 4) | STATE_SAFEOP)
OP_2_OP = ((STATE_OP << 4) | STATE_OP)
# SM通道定义
MAILBOX_WRITE = 0
MAILBOX_READ = 1
PROCESS_DATA_OUT = 2
PROCESS_DATA_IN = 3
# 相关中断定义，寄存器0x220-0x221位判断
AL_CONTROL_EVENT = 0x0001
SYNC0_EVENT = 0x0400
SYNC1_EVENT = 0x0800
SM_CHANGE_EVENT = 0x0010
MAILBOX_WRITE_EVENT = 0x0100
MAILBOX_READ_EVENT = 0x0200
PROCESS_OUTPUT_EVENT = 0x0400
PROCESS_INPUT_EVENT = 0x0800
# AL状态码，写入寄存器0x134-0x135
ALSTATUSCODE_NOERROR = 0x0000
ALSTATUSCODE_UNSPECIFIEDERROR = 0x0001
ALSTATUSCODE_INVALIDALCONTROL = 0x0011
ALSTATUSCODE_UNKNOWNALCONTROL = 0x0012
ALSTATUSCODE_BOOTNOTSUPP = 0x0013
ALSTATUSCODE_NOVALIDFIRMWARE = 0x0014
ALSTATUSCODE_INVALIDMBXCFGINBOOT = 0x0015
ALSTATUSCODE_INVALIDMBXCFGINPRE = 0x0016
ALSTATUSCODE_INVALIDSMCFG = 0x0017
ALSTATUSCODE_NOVALIDINPUTS = 0x0018
ALSTATUSCODE_NOVALIDOUTPUTS = 0x0019
ALSTATUSCODE_SYNCERROR = 0x001A
ALSTATUSCODE_SMWATCHDOG = 0x001B
ALSTATUSCODE_SYNCTYPESNOTCOMPATIBLE = 0x001C
ALSTATUSCODE_INVALIDSMOUTCFG = 0x001D
ALSTATUSCODE_INVALIDSMINCFG = 0x001E
ALSTATUSCODE_WAITFORCOLDSTART = 0x0020
ALSTATUSCODE_WAITFORINIT = 0x0021
ALSTATUSCODE_WAITFORPREOP = 0x0022
ALSTATUSCODE_WAITFORSAFEOP = 0x0023
ALSTATUSCODE_DCINVALIDSYNCCFG = 0x0030
NOERROR_NOSTATECHANGE = 0xFE
NOERROR_INWORK = 0xFF
# 配置出错标识代码
SYNCMANCHADDRESS = 0x01
SYNCMANCHSETTINGS = 0x03
SYNCMANCHSIZE = 0x02
#  SYNC MANAGER 寄存器位定义
SM_PDINITMASK = 0x0D
SM_TOGGLEMASTER = 0x02
SM_ECATENABLE = 0x01
SM_INITMASK = 0x0F
ONE_BUFFER = 0x02
THREE_BUFFER = 0x00
PD_OUT_BUFFER_TYPE = THREE_BUFFER
PD_IN_BUFFER_TYPE = THREE_BUFFER
SM_WRITESETTINGS = 0x04
SM_READSETTINGS = 0x00
SM_PDIDISABLE = 0x01
WATCHDOG_TRIGGER = 0x40
DC_SYNC0_ACTIVE = 0x02
DC_SYNC1_ACTIVE = 0x04
DC_EVENT_MASK = 0x0002


class UALEVENT:
    def __init__(self):
        self.Byte = [0] * 4


class UALEVENTMASK:
    def __init__(self):
        self.Word = [0] * 2


class TSYNCMAN:
    def __init__(self):
        self.sm_physical_addr = 0
        self.sm_length = 0
        self.sm_register_control = 0
        self.sm_register_status = 0
        self.sm_register_activate = 0
        self.sm_register_pdictl = 0


class TEEPROM_DEF:
    def __init__(self):
        self.eeprom_config = 0
        self.eeprom_pdi_acstate = 0
        self.eeprom_ctl_status = 0
        self.eeprom_addr = 0
        self.eeprom_data = [0] * 2


class TMII:
    def __init__(self):
        self.mii_ctl_status = 0
        self.mii_phy_addr = 0
        self.mii_phy_registeraddr = 0
        self.mii_phy_data = 0


class TFMMU:
    def __init__(self):
        self.logical_start_addr = 0
        self.length = 0
        self.logical_start_bit = 0
        self.logical_stop_bit = 0
        self.physical_start_bit = 0
        self.physical_stop_bit = 0
        self.type = 0
        self.activate = 0
        self.res = [0] * 3


class TDC:
    def __init__(self):
        self.receive_port = [0] * 4
        self.sys_time = [0] * 2
        self.receive_time_pu = [0] * 8
        self.sys_time_offset = [0] * 2
        self.sys_time_delay = 0
        self.sys_time_diff = 0
        self.speed_cnt_start = 0
        self.speed_cnt_diff = 0
        self.sys_filter_depth = 0
        self.res27 = [0] * 37
        self.cyclic_unit_ctl = 0
        self.activation = 0
        self.pulse_length = 0
        self.res28 = [0] * 5
        self.sync0_status = 0
        self.sync1_status = 0
        self.start_time_cyclic = [0] * 2
        self.next_sync1_pulse = [0] * 2
        self.sync0_cyclic_time = 0
        self.sync1_cyclic_time = 0
        self.latch0_ctl = 0
        self.latch1_ctl = 0
        self.res29 = [0] * 2
        self.latch0_status = 0
        self.latch1_status = 0
        self.latch0_time_pedge = [0] * 2
        self.latch0_time_nedge = [0] * 2
        self.latch1_time_pedge = [0] * 2
        self.latch1_time_nedge = [0] * 2
        self.res30 = [0] * 16
        self.ecat_bchangee_time = 0
        self.res31 = [0] * 17
        self.pdi_bstarte_time = 0
        self.pdi_bchangee_time = 0


class TESC_REG:
    def __init__(self):
        self.type = 0
        self.revision = 0
        self.build = 0
        self.fmmus_supported = 0
        self.sm_supported = 0
        self.ram_size = 0
        self.port_descriptor = 0
        self.esc_feature = 0
        self.res1 = [0] * 3
        self.station_addr = 0
        self.alias_addr = 0
        self.res2 = [0] * 6
        self.write_enable = 0
        self.write_protection = 0
        self.res3 = [0] * 7
        self.esc_wrenable = 0
        self.esc_wrprotection = 0
        self.res4 = [0] * 7
        self.esc_reset = 0
        self.res5 = [0] * 191
        self.esc_dlctl = 0
        self.res6 = [0] * 2
        self.physical_rdwr_offset = 0
        self.res7 = [0] * 3
        self.esc_dlstatus = 0
        self.res8 = [0] * 7
        self.al_ctl = 0
        self.res9 = [0] * 7
        self.al_status = 0
        self.res10 = 0
        self.al_statuscode = 0
        self.res11 = [0] * 5
        self.pdi_ctl = 0
        self.res12 = [0] * 7
        self.pdi_config = 0
        self.res13 = [0] * 86
        self.ecat_interrupt_mask = 0
        self.res14 = 0
        self.al_event_mask = UALEVENTMASK()
        self.res15 = [0] * 4
        self.ecat_interrupt_request = 0
        self.res16 = [0] * 7
        self.AlEvent = UALEVENT()
        self.res17 = [0] * 110
        self.rx_error_counter = [0] * 4
        self.rx_error_cntforwarded = [0] * 4
        self.ecat_pu_errorcnt = 0
        self.pdi_error_cnt = 0
        self.res18 = 0
        self.lost_link_cnt = [0] * 4
        self.res19 = [0] * 118
        self.watchdog_divider = 0
        self.res20 = [0] * 7
        self.watchdog_time_pdi = 0
        self.res21 = [0] * 7
        self.watchdog_time_pd = 0
        self.res22 = [0] * 15
        self.watchdog_status_pd = 0
        self.watchdog_cnt_pd = 0
        self.watchdog_cnt_pdi = 0
        self.res23 = [0] * 94
        self.eeprom_interface = TEEPROM_DEF()
        self.mii_man = TMII()
        self.res24 = [0] * 117
        self.fmmu_register = [TFMMU() for _ in range(16)]
        self.res25 = [0] * 128
        self.sm_register = [TSYNCMAN() for _ in range(8)]
        self.res26 = [0] * 64
        self.dc_register = TDC()
        self.res32 = [0] * 512
        self.esc_specific_register = 0
        self.digital_io_outpd = 0
        self.res33 = [0] * 6
        self.general_purp_outputs = 0
        self.res34 = [0] * 3
        self.general_purp_inputs = 0
        self.res35 = [0] * 51
        self.user_ram = [0] * 128


# TESC_REG MEMTYPE * pEsc;
pEsc = TESC_REG()
EscAlEvent = 0
nAlStatus = 0
nAlStatusFailed = 0
nAlStatusCode = 0
nAlControl = 0
nPdInputSize = 0
nPdOutputSize = 0
nEscAddrOutputData = 0
nEscAddrInputData = 0
# u8 *pPdOutputData;
# u8 *pPdInputData;
SendMbxSize = 0
ReceiveMbxSize = 0
EscAddrReceiveMbx = 0
EscAddrSendMbx = 0
# u8 *pMbxWriteData;
# u8 *pMbxReadData;
m_maxsyncman = 0
m_mbxrunning = 0
m_pdooutrun = 0
m_pdoinrun = 0
bEscIntEnabled = 0
bEcatLocalError = True
b3BufferMode = 0
bWdTrigger = 0
bEcatOutputUpdateRunning = 0
bDcSyncActive = False
aPdOutputData = [0] * MAX_PD_OUTPUT_SIZE
aPdInputData = 0
aMbOutputData = 0
aMbInputData = 0
mb_counter = 0
pd_counter = 0


