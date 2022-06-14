"""global variabal"""

# from net_process import NetworkManager
from enum import Enum
import traceback
import os

# Mem size
SERIAL_QUEUE_SIZE = 1024*2
CHANNEL_QUEUE_SIZE = 1024/2

# httpclient
# network_man = NetworkManager()

# Global flag
WRITE_TO_FILE = True  # 开启后，每个串口设备单独写入一个文件
WORK_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = WORK_PATH+"/../Log/"
PROGRAM_EXIT = False  # 程序退出标志

# Alogrithm param
WAIT_TIME = 0.1  # 串口空闲时线程休眠时间，减小cpu占用
TIMEOUT = 5  # 最大队列等待时间
MAX_CHANNEL_NUM = 7  # 芯片理想通道数
CACHE_SIZE = 100
AVERAGE = 4


class ThreadStatus(Enum):  # 控制线程运行
    ALIVE = 1
    DEAD = 0


# 格式：前导字+长度+命令+数据+校验（CRC8，格式 8541）
# 前导字，2Byte，固定的字符，收发不同；
# 长度：1Byte，是命令+数据+校验的所有字节数
# 命令：1Byte
# 校验：1Byte，是对命令+数据部分进行 CRC8 校验。
# Order
PCAP_ERROR = 0x50
PCAP_SINGLE = 0x54
PCAP_CTRL = 0x55
PCAP_DATA = 0x56
PCAP_START = 0x01
PCAP_STOP = 0x00

# Head
PCAP_HEAD_SEND = [0x68, 0xA9]
PCAP_HEAD_RECV = [0x63, 0xF3]

# Single measurement order
PCAP_SINGLE_ORDER = PCAP_HEAD_SEND.extend([0x03, PCAP_SINGLE, 0x55, 0xA8])
# Timing measurement control order
PCAP_CTRL_START_ORDER = PCAP_HEAD_SEND.extend(
    [0x03, PCAP_CTRL, PCAP_START, 0x8A])
PCAP_CTRL_STOP_ORDER = PCAP_HEAD_SEND.extend(
    [0x03, PCAP_CTRL, PCAP_STOP, 0x4E])

# Exception Info
PCAP_ERROR_DICT = {
    0x01: "接收到的数据校验不正确",
    0x02: "接收到的数据包长度不正",
    0x03: "功能不存在",
    0x04: "返回的长度不正确",
    0x05: "采样频率过快"
}

# Recv data type
PCAP_RECV_ERROR = -1
PCAP_RECV_CTRL_INFO = 0
PCAP_RECV_DATA = 1

# Process value
DIVISOR = 1 << 20
RELA_CAP = 5


def print_exception(e):
    '''打印异常信息'''
    print(str(Exception))
    print(str(e))
    print(traceback.format_exc())
