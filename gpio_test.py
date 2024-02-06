import cv2, os, time
import OPi.GPIO as GPIO

'''
    开始检测前黄灯闪烁3s;
    正常运行时黄灯常亮，待机冷却状态只有充电宝亮灯；
    推理时黄灯闪烁，发现猫黄灯常亮2-3s；未发现猫红灯常亮3s(所有推理结束后）；
    出现错误红灯闪烁；
'''

# 引脚定义
power_光敏电阻 = 16;    pi_光敏电阻 = 18          # GND_光敏电阻 = 14
power_红外 = 5;        pi_红外 = 3              # GND_红外 = 6
po_电机 = 8          # power_电机 = 5v 2        GND_电机 = 9
po_灯带 = 19         # power_灯带 = 5v 4       GND_灯带 = 20


# GND = 6,9,14,20,25
# 5v = 2,4
# 3.3v = 1,17

# gpio初始化
GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(power_光敏电阻, GPIO.OUT);   GPIO.setup(pi_光敏电阻, GPIO.IN)
GPIO.setup(power_红外, GPIO.OUT);      GPIO.setup(pi_红外, GPIO.IN)
GPIO.setup(po_电机, GPIO.OUT)
GPIO.setup(po_灯带, GPIO.OUT)


def power_电机(t1=2):
    global food
    # 5r/min，30度/2s
    # open
    GPIO.output(po_电机, 0)
    time.sleep(t1)

    # close
    GPIO.output(po_电机, 1)


    # food = 5
# 初始化关闭
GPIO.output(po_电机, 1)
GPIO.output(po_灯带, 1)

power_电机(60)

#
# while True:
#
#
#     for i in range(10):
#         GPIO.output(po_灯带, 0)
#         time.sleep(2)
#         GPIO.output(po_灯带, 1)