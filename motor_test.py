from gpio import *

def power_电机(t1=2):
    # 5r/min，30度/2s
    GPIO.output(po_电机, 0)
    time.sleep(t1)
    GPIO.output(po_电机, 1)

power_电机(5)
time.sleep(3)
power_电机(5)
