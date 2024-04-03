import os, time
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
po_电机 = 8          # power_电机 = 5v 2        # GND_电机 = 9
po_灯带 = 19         # power_灯带 = 5v 4        # GND_灯带 = 20


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

# 初始化关闭
GPIO.output(po_电机, 1)
GPIO.output(po_灯带, 1)

def open_light(t1=2):
    GPIO.output(po_灯带, 0)
    time.sleep(t1)
    GPIO.output(po_灯带, 1)

def power_motor(t1=2):
    # 5r/min，30度/2s
    GPIO.output(po_电机, 0)
    time.sleep(t1)
    GPIO.output(po_电机, 1)

def remain_food():
    GPIO.output(power_红外, 1)
    for i in range(10):
        if GPIO.input(pi_红外) == 1:
            print('猫粮还有剩余')
            break
        time.sleep(0.1)
    else:
        print('猫粮所剩无几')
        GPIO.output(power_红外, 0)
        return False
    GPIO.output(power_红外, 0)
    return True

nonlinear_list = [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120, 136, 153, 171, 190, 210, 231, 253, 276, 300, 325, 351, 378, 406, 435, 465, 496, 528, 561, 595, 630, 666, 703, 741, 780, 820, 861, 903, 946, 990, 1035, 1081, 1128, 1176, 1225, 1275, 1326, 1378, 1431, 1485, 1540, 1596, 1653, 1711, 1770, 1830, 1891, 1953, 2016, 2080, 2145, 2211, 2278, 2346, 2415, 2485, 2556, 2628, 2701, 2775, 2850, 2926, 3003, 3081, 3160, 3240, 3321, 3403, 3486, 3570, 3655, 3741, 3828, 3916, 4005, 4095, 4186, 4278, 4371, 4465, 4560, 4656, 4753, 4851, 4950]
def slowly_light(on=True, f=500000):
    # False渐暗，True渐亮
    for i in range(100):
        GPIO.output(po_灯带, on)
        time.sleep((5000 - nonlinear_list[i]) / f)
        GPIO.output(po_灯带, not on)
        time.sleep(nonlinear_list[i] / f)

def find_something():
    slowly_light(on=True)

    GPIO.output(po_灯带, 0)
    GPIO.output(power_光敏电阻, 1)

    for i in range(20):
        if GPIO.input(pi_光敏电阻) == 1:
            print('光敏电阻有发现！')
            break
        time.sleep(0.1)
    else:
        print('X')
        GPIO.output(power_光敏电阻, 0)
        slowly_light(on=False)
        return False

    slowly_light(on=False)
    return True


if __name__ == '__main__':
    while 1:
        if find_something() and not remain_food():
            print('假装开始识别猫')
            time.sleep(5)
        else:
            print('没开始识别猫')
            time.sleep(3)