from gpio_test import *

open_light(5)
time.sleep(3)
slowly_light(on=True)
open_light(5)
slowly_light(on=False)

