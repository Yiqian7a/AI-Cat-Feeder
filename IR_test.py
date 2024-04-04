from gpio_test import *

# 接收到红外光输出0，否则输出1
GPIO.output(power_红外, 1)

while 1:
    print(GPIO.input(pi_红外))
    time.sleep(0.1)
