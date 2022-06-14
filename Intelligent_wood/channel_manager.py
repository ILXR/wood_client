from threading import Thread
import numpy as np
from util import *
import util
import queue

# 检测按压参数
'''
maxvalue                   ---------
                           |       |                                                                              ----------
action start             ->|       |   ->   cur_value = baseline * ACTION_START_THRESHOLD                         |        |
                           |       |                                                                              |        |
action end                 |     ->|   ->   cur_value = baseline + (maxvalue - baseline) * ACTION_END_THRESHOLD   |        |
                           |       |                                                                              |        |
baseline     --------------         -------------------------- >= ACTION_INTERVAL --------------------------------          ------
'''
ACTION_START_VAL = 20         # 和稳定值相差一定值时，按压动作开始
ACTION_END_THRESHOLD = 1/2    # 当电容相较于触发值的变化值降低为一定阈值时，按压动作结束
STABLE_THRESHOLD = 5          # 动态调整基准值（baseline）的最大极差
ACTION_INTERVAL = 5           # 每两次动作之间的最小间隔
CACHE_SIZE = 40               # 用于获取基准值的数据量


class DetectThread(Thread):
    """动作检测类（算法模块）"""

    def __init__(self, id, data_queue, callback=None):
        ''' 实现动作检测，需要读入的数据队列以及回调函数'''
        self.status = ThreadStatus.ALIVE
        self.id = id
        self.data_queue = data_queue
        self.callback = callback
        self.cache = []
        self.in_action = False
        self.baseline = None
        self.max_action_val = 0
        self.min_stable_val = 0
        self.action_interval = 0
        self.start_action_val = 0
        self.prev_val = 0
        Thread.__init__(self)

    def run(self):
        while (self.status == ThreadStatus.ALIVE and not util.PROGRAM_EXIT):
            try:
                self.process(self.data_queue.get(timeout=5))
            except Exception as e:
                util.print_exception(e)
                print("Action detector exit 1")
                return

    def process(self, val):
        if len(self.cache) == CACHE_SIZE:
            # 获取通道稳定基准值
            if self.baseline is None or (np.max(self.cache) - np.min(self.cache) <= STABLE_THRESHOLD):
                self.baseline = np.mean(self.cache)
                # print("channel ", self.id, " baseline: ", self.baseline)
            self.cache.pop(0)
        self.cache.append(val)
        self.action_interval += 1
        if(self.baseline is None):
            return
        min_start_val = min(
            self.baseline, self.min_stable_val) + ACTION_START_VAL
        if not self.in_action and (val > min_start_val) and self.action_interval > ACTION_INTERVAL \
                and val > self.prev_val:
            # 超出阈值，判断为Action
            self.in_action = True
            self.start_action_val = val
            print("Channel ", self.id, " action start.")
        if self.in_action:
            # 记录动作最大值
            self.max_action_val = max(self.max_action_val, val)
            # if(val < self.baseline + (self.max_action_val - self.baseline) * ACTION_END_THRESHOLD):
            if (val < self.start_action_val):
                # 下降沿，Action结束
                self.min_stable_val = val
                self.in_action = False
                self.max_action_val = 0
                self.action_interval = 0
                # TODO 动作结束，调用回调
                print("Channel ", self.id, " action end.")
                if self.callback is not None:
                    self.callback()
        else:
            self.min_stable_val = min(self.min_stable_val, val)
        self.prev_val = val


class ChannelManager():
    """
    通道管理类，负责解析单个通道的数据
    :保存了所属串口的设备名称
    :保存了所管理通道的id
    :保存了通讯所需的数据队列
    """

    def __init__(self, device, id):
        '''
        :device 所属的设备名称
        :id 通道的物理序号
        '''
        self.device = device
        self.id = id
        self.data_queue = queue.Queue(util.CHANNEL_QUEUE_SIZE)
        self.detect_thread = DetectThread(self.id, self.data_queue)

    def index(self):
        return self.id

    def put(self, value):
        self.data_queue.put(value)

    def start_read(self):
        print("Channel ", self.id, " start read")
        self.detect_thread.start()

    def stop_read(self):
        self.detect_thread.status = ThreadStatus.DEAD
