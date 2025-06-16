import serial
from time import sleep
import crcmod

import time

ser = serial.Serial()

send_i = 0
start_trigger = 0  # 触发标志位


def port_open_recv():  # 对串口的参数进行配置
    ser.port = "COM10"
    ser.baudrate = 50000000
    ser.bytesize = 8
    ser.stopbits = 1
    ser.parity = "N"  # 奇偶校验位
    ser.dsrdtr = True  # DSR/DTR控制
    ser.open()
    if ser.isOpen():
        print("串口打开成功！")
    else:
        print("串口打开失败！")
    sleep(0.5)  # 等待串口稳定
    ser.dtr = True  # DTR信号
    sleep(0.5)  # 等待串口稳定


# isOpen()函数来查看串口的开闭状态


def port_close():
    ser.close()
    if ser.isOpen():
        print("串口关闭失败！")
    else:
        print("串口关闭成功！")


def send(send_data):
    if ser.isOpen():
        ser.write(send_data)  # 编码
        global send_i
        send_i = send_i + 1
        print("tx_" + str(send_i), send_data.hex())
    else:
        print("发送失败！")


head = b"\x00\x01"  # 头部
len_data = 0
data_raw = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
crc = b"\x00\x00"  # CRC校验位

if __name__ == "__main__":
    len_data = len(data_raw)  # 头部长度
    len_data = len_data.to_bytes(1, byteorder="little")  # 转换为字节
    data = data_raw.encode("utf-8")  # 编码数据
    crc16modbus_func = crcmod.predefined.Crc("modbus")  # CRC16-MODBUS校验
    crc = crc16modbus_func.new(head + len_data + data).crcValue  # 计算CRC校验
    crc = crc.to_bytes(2, byteorder="little")  # 转换为字节
    port_open_recv()
    start_trigger = 1
    start_time = time.perf_counter()  # 记录开始时间
    for i in range(2048):
        if start_trigger == 1:
            send(head + len_data + data + crc)
            start_trigger = 0
        else:
            while True:
                recv = ser.read(data.__len__() + 5)  # 接收数据
                recv_data = recv[3:-2]
                recv_data = recv_data.decode("utf-8")
                # print("rx_", recv_data.decode("utf-8"))
                if recv_data == data_raw:
                    break
            start_trigger = 1
    end_time = time.perf_counter()  # 记录结束时间
    print(f"Total time taken: {end_time - start_time:.3f} seconds")
    sleep(1)
    port_close()
