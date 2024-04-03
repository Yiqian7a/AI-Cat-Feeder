from gpio import *

def open_light(t1):
    GPIO.output(po_灯带, 0)
    time.sleep(t1)
    GPIO.output(po_灯带, 1)

open_light(5)
time.sleep(3)
open_light(5)