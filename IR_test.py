from gpio import *

GPIO.output(power_红外, 1)

while 1:
    print(GPIO.input(pi_红外))
    time.sleep(0.1)
