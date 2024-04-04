from gpio_test import *

# 有光照输出0，无光照输出1
GPIO.output(power_光敏电阻, 1)

while 1:
    print(GPIO.input(pi_光敏电阻))
    time.sleep(0.1)
