from channel_manager import ChannelManager
from data_process import ProcessThread
from threading import Thread
from util import *
import serial
import queue
import time
import util


class ReadThread(Thread):
    """
    专门处理串口数据的读取与解析，分发给各个通道
    """

    def __init__(self, device, comm, data_queue):
        '''
        :device 设备名称
        :comm Serial 串口对象
        :data_queue 传输队列，将读取到的字节一个一个添加进队列，传给数据解析类
        '''
        self.device = device
        self.comm = comm
        self.data_queue = data_queue
        self.status = ThreadStatus.ALIVE
        Thread.__init__(self)

    def run(self):
        print("串口已开启...")
        while(self.status == ThreadStatus.ALIVE and not util.PROGRAM_EXIT):
            try:
                cnt = self.comm.in_waiting
                if(cnt > 0):
                    recv = self.comm.read(cnt)
                    for byte_data in recv:
                        self.data_queue.put(byte_data, timeout=util.TIMEOUT)
                else:
                    time.sleep(0.1)
            except Exception as e:
                util.print_exception(e)
                util.PROGRAM_EXIT = True
                print("Device - "+self.device+" error",
                      "Serial process exit 1.")
                return


class SerialManager():
    """
    串口设备管理类，负责读取串口数据并分发到各个通道管理类
    """

    def __init__(self, device, channels, speed=57600):
        '''
        :device - 设备名称
        :channels - 有效通道数组
        :speed - 波特率
        '''
        self.comm = serial.Serial(device, speed)
        self.channel_managers = [ChannelManager(device,
                                                id=id) for id in channels]
        data_queue = queue.Queue(SERIAL_QUEUE_SIZE)
        self.read_thread = ReadThread(device, self.comm, data_queue)
        self.process_thread = ProcessThread(self.channel_managers, data_queue)
        print("Serial Device : "+device, "Available Channels : ",
              channels, "Initialization complete.")

    def start_read(self):
        '''开始从串口读取数据'''
        self.read_thread.start()
        self.process_thread.start()
        for channel in self.channel_managers:
            channel.start_read()

    def stop_read(self):
        '''停止从串口读取数据'''
        self.read_thread.status = ThreadStatus.DEAD
        self.process_thread.status = ThreadStatus.DEAD
        for channel in self.channel_managers:
            channel.stop_read()

    def start_measurement(self):
        '''向PCAP02发送命令，开始定时测量'''
        if(self.comm.writable()):
            self.comm.write(PCAP_CTRL_START_ORDER)

    def stop_measurement(self):
        '''向PCAP02发送命令，停止定时测量'''
        if(self.comm.writable()):
            self.comm.write(PCAP_CTRL_STOP_ORDER)
