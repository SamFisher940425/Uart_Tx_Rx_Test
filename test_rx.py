import serial
from time import sleep
import crcmod

ser = serial.Serial()

send_i = 0
start_trigger = 0  # 触发标志位


def port_open_recv():  # 对串口的参数进行配置
    ser.port = "COM4"
    ser.baudrate = 115200
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
    ser.dtr = True  # DTR控制
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


head = b"\x01\x00"  # 头部
len_data = 0  # 数据长度
data_raw = "12345678123456781234567812345678123456781234567812345678123456781234567812345678123456781234567812345678123456781234567812345678"
crc = b"\x00\x00"  # CRC校验位

if __name__ == "__main__":
    len_data = len(data_raw)  # 头部长度
    len_data = len_data.to_bytes(1, byteorder="little")  # 转换为字节
    data = data_raw.encode("utf-8")  # 编码数据
    crc16modbus_func = crcmod.predefined.Crc("modbus")  # CRC16-MODBUS校验
    crc = crc16modbus_func.new(head + len_data + data).crcValue  # 计算CRC校验
    crc = crc.to_bytes(2, byteorder="little")  # 转换为字节
    port_open_recv()
    for i in range(512):
        if start_trigger == 1:
            send(head + len_data + data + crc)
            start_trigger = 0
        else:
            while True:
                recv = ser.read(data.__len__() + 5)  # 接收数据
                print("rx_", str(recv))
                recv_data = recv[3:-2]
                recv_data = recv_data.decode("utf-8")
                # print("rx_", recv_data)
                if recv_data == data_raw:
                    break
            start_trigger = 1
    sleep(1)
    port_close()
