from gpio import *

def power_电机(t1=2):
    # 5r/min，30度/2s
    # open
    GPIO.output(po_电机, 0)
    time.sleep(t1)

    # close
    GPIO.output(po_电机, 1)
power_电机(60)