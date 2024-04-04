from gpio_test import *

print('长亮5s')
open_light(5)
print('熄灭3s')
time.sleep(3)

print('渐亮渐暗')
slowly_light(on=True)
open_light(2)
slowly_light(on=False)

