import ec_def
import spi_rw


def get_sm(spi, channel):
    temp = ec_def.TSYNCMAN()
    address = 0x0800 + channel * 0x08
    temp.sm_physical_addr = spi_rw.spi_read_16(spi, address)
    temp.sm_length = spi_rw.spi_read_16(spi, address + 2)
    temp.sm_register_control = spi_rw.spi_read_8(spi, address + 4)
    temp.sm_register_status = spi_rw.spi_read_8(spi, address + 5)
    temp.sm_register_activate = spi_rw.spi_read_8(spi, address + 6)
    temp.sm_register_pdictl = spi_rw.spi_read_8(spi, address + 7)
    return temp


def set_intmask(spi, intMask):
    mask = spi_rw.spi_read_16(spi, 0x0204)
    mask = mask | intMask
    spi_rw.spi_write_16(spi, 0x0204, mask)
    return


def reset_intmask(spi, intMask):
    mask = spi_rw.spi_read_16(spi, 0x0204)
    mask = mask & intMask
    spi_rw.spi_write_16(spi, 0x0204, mask)
    return


def enable_syncmanchannel(spi, channel):
    address = 0x0800 + channel * 0x08
    temp = spi_rw.spi_read_8(spi, address + 7)
    temp &= ~ec_def.SM_PDIDISABLE
    spi_rw.spi_write_8(spi, address + 7, temp)
    return


def disable_syncmanchannel(spi, channel):
    address = 0x0800 + channel * 0x08
    temp = spi_rw.spi_read_8(spi, address + 7)
    temp &= ~ec_def.SM_PDIDISABLE
    return


def SetAlStatus(spi, alstatus, alstatuscode):
    spi_rw.spi_write_16(spi, 0x0130, alstatus)
    if alstatuscode != 0xFF:
        spi_rw.spi_write_16(spi, 0x0134, alstatuscode)
    return


def checksmsettings(maxChannel):
    return 0


def mbx_startmailboxhandler(spi):
    pSyncMan = ec_def.TSYNCMAN()
    pSyncMan = get_sm(spi, ec_def.MAILBOX_WRITE)
    ReceiveMbxSize = pSyncMan.sm_length
    EscAddrReceiveMbx = pSyncMan.sm_physical_addr
    pSyncMan = get_sm(spi, ec_def.MAILBOX_READ)
    SendMbxSize = pSyncMan.sm_length
    EscAddrSendMbx = pSyncMan.sm_physical_addr
    enable_syncmanchannel(spi, ec_def.MAILBOX_WRITE)
    enable_syncmanchannel(spi, ec_def.MAILBOX_READ)
    ec_def.m_mbxrunning = True
    return 0


def pdo_startinputhandler(spi):
    nPdInputBuffer = 3
    nPdOutputBuffer = 3
    intMask = 0
    dcControl = 0
    cycleTime = 0
    pSyncMan = ec_def.TSYNCMAN()
    pSyncMan = get_sm(spi, ec_def.PROCESS_DATA_OUT)
    ec_def.nEscAddrOutputData = pSyncMan.sm_physical_addr
    print("pdo_startinputhandler")
    print(ec_def.nEscAddrOutputData)
    ec_def.nPdOutputSize = pSyncMan.sm_length

    if pSyncMan.sm_register_control & ec_def.ONE_BUFFER:
        ec_def.nPdOutputBuffer = 1
    pSyncMan = get_sm(spi, ec_def.PROCESS_DATA_IN)
    ec_def.nEscAddrInputData = pSyncMan.sm_physical_addr
    ec_def.nPdInputSize = pSyncMan.sm_length

    if pSyncMan.sm_register_control & ec_def.ONE_BUFFER:
        ec_def.nPdInputBuffer = 1

    if pSyncMan.sm_length == 0:
        return ec_def.ALSTATUSCODE_NOERROR

    dcControl = spi_rw.spi_read_8(spi, 0x0981)
    if dcControl & (ec_def.DC_SYNC0_ACTIVE | ec_def.DC_SYNC1_ACTIVE):
        intMask = ec_def.DC_EVENT_MASK
        ec_def.bDcSyncActive = True
        cycleTime = spi_rw.spi_read_32(spi, 0x09A0)

    if ec_def.nPdOutputSize != 0:
        intMask |= ec_def.PROCESS_OUTPUT_EVENT
    else:
        intMask |= ec_def.PROCESS_INPUT_EVENT

    if ec_def.nPdInputSize > 0:
        enable_syncmanchannel(spi, ec_def.PROCESS_DATA_IN)
        ec_def.m_pdoinrun = True

    if ec_def.nPdInputSize > 0:
        if ec_def.bEcatLocalError != 0:
            enable_syncmanchannel(spi, ec_def.PROCESS_DATA_OUT)
        ec_def.m_pdoinrun = True
    set_intmask(spi, intMask)
    return 0


def pdo_startoutputhandler(spi):
    result = 0
    if ec_def.nPdOutputSize > 0:
        if ec_def.bEcatLocalError & (result == 0 | ec_def.NOERROR_INWORK):
            enable_syncmanchannel(spi, ec_def.PROCESS_DATA_OUT)
            ec_def.bEcatLocalError = False
        if result != 0:
            if result != ec_def.NOERROR_INWORK:
                ec_def.bEcatLocalError = True
                return result
        ec_def.m_pdooutrun = True
    ec_def.bEcatOutputUpdateRunning = True
    return 0


def mbx_stopmailboxhandler(spi):
    ec_def.m_mbxrunning = False
    disable_syncmanchannel(spi, ec_def.MAILBOX_WRITE)
    disable_syncmanchannel(spi, ec_def.MAILBOX_READ)
    return


def pdo_stopinputhandler(spi):
    disable_syncmanchannel(spi, ec_def.PROCESS_DATA_OUT)
    reset_intmask(spi, (ec_def.SYNC0_EVENT | ec_def.SYNC1_EVENT
                        | ec_def.PROCESS_INPUT_EVENT | ec_def.PROCESS_OUTPUT_EVENT))
    ec_def.bEscIntEnabled = False
    ec_def.m_pdoinrun = False
    disable_syncmanchannel(spi, ec_def.PROCESS_DATA_IN)
    return 0


def pdo_stopoutputhandler():
    ec_def.bEcatOutputUpdateRunning = False
    return 0


def al_statemachine(spi, alcontrolvar):
    result = 0
    statetrans = 0
    val = 0
    al = alcontrolvar

    if alcontrolvar & ec_def.STATE_ERRACK:
        ec_def.nAlStatus &= ~ec_def.STATE_ERROR
    elif (ec_def.nAlStatus & ec_def.STATE_ERROR
          & (alcontrolvar & ec_def.STATE_MASK) >
          (ec_def.nAlStatus & ec_def.STATE_MASK)):
        return
    alcontrolvar &= ec_def.STATE_MASK
    statetrans = ec_def.nAlStatus
    statetrans <<= 4
    statetrans += alcontrolvar

    if statetrans & ec_def.INIT_2_OP:
        pass
    if statetrans & ec_def.OP_2_PREOP:
        pass
    if statetrans & ec_def.SAFEOP_2_PREOP:
        pass
    if statetrans & ec_def.PREOP_2_PREOP:
        val = ec_def.MAILBOX_READ + 1
        result = checksmsettings(val)
        
    if statetrans & ec_def.PREOP_2_SAFEOP:
        pass
    if statetrans & ec_def.SAFEOP_2_OP:
        pass
    if statetrans & ec_def.OP_2_SAFEOP:
        pass
    if statetrans & ec_def.SAFEOP_2_SAFEOP:
        pass
    if statetrans & ec_def.OP_2_OP:
        result = checksmsettings(ec_def.m_maxsyncman)
        

    if result == 0:
        if statetrans == ec_def.INIT_2_PREOP:
            result = mbx_startmailboxhandler(spi)
        elif statetrans == ec_def.PREOP_2_SAFEOP:
            result = pdo_startinputhandler(spi)
        elif statetrans == ec_def.SAFEOP_2_OP:
            result = pdo_startoutputhandler(spi)
        elif statetrans == ec_def.PREOP_2_INIT:
            mbx_stopmailboxhandler(spi)
        elif statetrans == ec_def.SAFEOP_2_PREOP:
            result = pdo_startinputhandler(spi)
        elif statetrans == ec_def.OP_2_OP:
            result = ec_def.NOERROR_NOSTATECHANGE
        elif statetrans == ec_def.PREOP_2_OP:
            result = ec_def.ALSTATUSCODE_INVALIDALCONTROL
        else:
            result = ec_def.ALSTATUSCODE_UNKNOWNALCONTROL
    else:
        if statetrans == ec_def.STATE_OP:
            pdo_stopoutputhandler()

        elif statetrans == ec_def.STATE_SAFEOP:
            pdo_stopinputhandler(spi)
          
        elif statetrans == ec_def.STATE_PREOP:
            if result == ec_def.ALSTATUSCODE_INVALIDMBXCFGINPRE:
                mbx_stopmailboxhandler(spi)
                ec_def.nAlStatus = ec_def.STATE_INIT
               
            else:
                ec_def.nAlStatus = ec_def.STATE_PREOP
             

    if alcontrolvar != (ec_def.nAlStatus & ec_def.STATE_MASK):
        if result != 0:
            ec_def.nAlStatusFailed = ec_def.nAlStatus
            ec_def.nAlStatus |= ec_def.STATE_CHANGE
        else:
            if ec_def.nAlStatusCode != 0:
                result = ec_def.nAlStatusCode
                ec_def.nAlStatusFailed = alcontrolvar
                alcontrolvar |= ec_def.STATE_CHANGE
            elif alcontrolvar <= ec_def.nAlStatusFailed:
                result = 0xFF
            else:
                ec_def.nAlStatusFailed = 0
            ec_def.nAlStatus = alcontrolvar
        SetAlStatus(spi, ec_def.nAlStatus, result)
        ec_def.nAlStatusCode = 0
    else:
        SetAlStatus(spi, ec_def.nAlStatus, 0xFF)

    return


def ECAT_init(spi):
    spi_rw.spi_write_16(spi, 0x0204, 0x0000) # 0x10 0x28 0x00 0x00
    spi_rw.spi_write_16(spi, 0x0206, 0x0000) # 0x10 0x34 0x00 0x00
    ec_def.m_maxsyncman = 0
    ec_def.m_maxsyncman = spi_rw.spi_read_8(spi, 0x0005)
    print(ec_def.m_maxsyncman)
    ec_def.nAlStatus = ec_def.STATE_INIT
    SetAlStatus(spi, ec_def.nAlStatus, 0)
    ec_def.nPdInputSize = 0
    ec_def.nPdOutputSize = 0
    ec_def.bEcatLocalError = 0
    ec_def.bEscIntEnabled = 0
    return


def free_run(spi):
    #print("free run")
    if (ec_def.EscAlEvent >> 8) & (ec_def.PROCESS_OUTPUT_EVENT >> 8):
        if ec_def.bEcatOutputUpdateRunning == True:
            spi_rw.readoutputdata(spi)
        spi_rw.writeinputdata(spi)
        print("free run")
    return


def mb_process():
    return


def al_event(spi):
    print("al_event working")
    alcontrol = 0
    ec_def.EscAlEvent = spi_rw.spi_read_32(spi, 0x0220)
    print(ec_def.EscAlEvent)
    if ec_def.EscAlEvent & ec_def.AL_CONTROL_EVENT | ec_def.EscAlEvent & 16:
        alcontrol = spi_rw.spi_read_16(spi, 0x0120)
        ec_def.nAlControl = alcontrol
        al_statemachine(spi, alcontrol)
        print("al_statemachine finish")
    else:
        pass
    if ec_def.m_mbxrunning:
        if (ec_def.EscAlEvent >> 8 &
                ec_def.MAILBOX_WRITE_EVENT >> 8):
            mb_process()
    return
