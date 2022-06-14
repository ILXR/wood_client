from serial_manager import SerialManager
import time
import json
import util
import os

serial_managers = []


def wait():
    while not util.PROGRAM_EXIT:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            util.PROGRAM_EXIT = True
            print("检测到 ctrl-c; 程序退出...")
            os._exit(0)


def init():
    with open(util.WORK_PATH+"/config.json", 'r') as f:
        config = json.load(f)
        for dev in config['DeviceInfo']:
            serial_managers.append(SerialManager(
                dev['device'], dev['channels']))


def start():
    for dev in serial_managers:
        dev.start_read()


def main():
    # if not test_internet():
    #     print("网络未连通，程序退出")
    #     return
    # 初始化串口管理
    init()
    # 线程开始工作
    start()
    # 等待线程
    wait()


if __name__ == "__main__":
    main()
