import cv2, os, time, torch, argparse, datetime
from nanodet.util import cfg, load_config, Logger
from nanodet.model.arch import build_model
from nanodet.util import load_model_weight
from nanodet.data.transform import Pipeline
import OPi.GPIO as GPIO

''' 指示灯：
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

GPIO.output(po_电机, 1)
GPIO.output(po_灯带, 1)

class Predictor(object):
    def __init__(self, cfg, model_path, logger, device='cpu'):
        self.cfg = cfg
        self.device = device
        model = build_model(cfg.model)
        ckpt = torch.load(model_path, map_location=lambda storage, loc: storage)
        load_model_weight(model, ckpt, logger)
        self.model = model.to(device).eval()
        self.pipeline = Pipeline(cfg.data.val.pipeline, cfg.data.val.keep_ratio)

    def inference(self, img):
        img_info = {}
        height, width = img.shape[:2]
        img_info['height'] = height
        img_info['width'] = width
        meta = dict(img_info=img_info,
                    raw_img=img,
                    img=img)
        meta = self.pipeline(meta, self.cfg.data.val.input_size)
        meta['img'] = torch.from_numpy(meta['img'].transpose(2, 0, 1)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            results = self.model.inference(meta)
        return meta, results

    # 通过修改参数选择保存或者显示带标记框的输出图片
    def visualize(self, dets, meta, class_names, score_thres, save_path='', wait=0):
        time1 = time.time()
        self.model.head.show_result(meta['raw_img'], dets, class_names, score_thres=score_thres, show=False,save_path=save_path)
        print('viz time: {:.3f}s'.format(time.time()-time1))

# 调用摄像头拍一张照片
def take_photo(rank=1):
    # 摄像头的分辨率宽高组合，根据摄像头需要调整
    rank_ls = ((1024, 768), (1280, 720), (1600, 1200), (1920, 1080),
               (2048, 1536), (2592, 1944), (3264, 2448), (3840, 2160), (3840, 3104))
    w,h = rank_ls[rank]
    cap.set(3,w)
    cap.set(4,h)
    print(f"分辨率:{cap.get(3)}x{cap.get(4)}")
    ret,image = cap.read()
    if ret:
        return image

def power_电机(t1):
    global food
    # open
    GPIO.output(po_电机, 0)
    time.sleep(t1)

    # close
    GPIO.output(po_电机, 1)
    food = 5

food = 5
def remain_food():
    global food
    GPIO.output(power_红外, 1)
    for i in range(10):
        time.sleep(0.1)
        if GPIO.input(pi_红外) == 1:
            print('remain')
            break
    else:
        print('not remain')
        GPIO.output(power_红外, 0)
        return False
    GPIO.output(power_红外, 0)
    return True

def find_something():
    GPIO.output(po_灯带,0)
    GPIO.output(power_光敏电阻,1)
    for i in range(20):
        time.sleep(0.1)
        if GPIO.input(pi_光敏电阻) == 1:
            print('?')
            break
    else:
        print('X')
        GPIO.output(power_光敏电阻, 0)
        GPIO.output(po_灯带, 1)
        return False
    GPIO.output(power_光敏电阻, 0)
    GPIO.output(po_灯带, 1)
    return True

def led(color,mode,t1 = 0):
    if not t1:
        if mode == 'heartbeat':
            os.system(f"sudo echo {mode} > /sys/devices/platform/leds/leds/{color}-led/trigger")
        else:
            os.system(f"sudo echo {mode} > /sys/devices/platform/leds/leds/{color}-led/brightness")
    else:
        if mode == 'heartbeat':
            os.system(f"sudo echo {mode} > /sys/devices/platform/leds/leds/{color}-led/trigger")
            time.sleep(t1)
            os.system(f"sudo echo 'none' > /sys/devices/platform/leds/leds/{color}-led/trigger")
        else:
            os.system(f"sudo echo {mode} > /sys/devices/platform/leds/leds/{color}-led/brightness")
            time.sleep(t1)
            os.system(f"sudo echo '0' > /sys/devices/platform/leds/leds/{color}-led/brightness")

def find_cat():
    # 开始推理时黄灯闪烁，发现猫黄灯常亮2-3s；未发现猫红灯常亮3s(所有推理结束后）
    led('green','heartbeat')
    raw_image = take_photo(3)

    # 整理由nanodet模型推理出的结果
    def sort_result(dets, score_thresh):
        for bbox in dets[15]:
            score = bbox[-1]
            if score > score_thresh:
                return True
        return False

    logger.log('开始推理')
    meta, res = predictor.inference(raw_image)
    if sort_result(res, 0.6):
        led('green', '1')
        print('cat!cat!cat!')
        power_电机(2)
        predictor.visualize(res, meta, cfg.class_names, 0.6, save_path=f'{path_dir}/{i}_findcat.jpg')
        return True
    else:
        print('no cat')
        cv2.imwrite(f'{path_dir}/{i}.jpg',raw_image)
        return False
# -------------------------------------------------------------------------------------------------------------------


# 加载推理模型
load_config(cfg, './config/nanodet-m.yml')
logger = Logger(-1, use_tensorboard=False)
predictor = Predictor(cfg, 'model/nanodet_m.pth', logger)
led('green','1')
while 1: # 每隔10秒检测一次
    time.sleep(6)
    print(food)
    if find_something() and (not remain_food() or food == 0):
        # 摄像头初始化
        # torch.backends.cudnn.enabled = True
        # torch.backends.cudnn.benchmark = True
        cap = cv2.VideoCapture(1)
        dir = f'./capture/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
        if cap.isOpened():
            path_dir = dir + '/'
            os.makedirs(path_dir, exist_ok=True)

            for i in range(10):
                if find_cat():
                    cap.release()
                    os.renames(dir,dir + '_findcat')
                    find = True

                    # print('冷却600s...')
                    # led('green', '0')
                    # time.sleep(600)
                    # led('green', '1')
                    break
            else:
                cap.release()
                os.renames(dir,dir + '_no')
                # 红灯常亮3s
                led('green', '0')
                led('red', '1',3)

                # print('冷却60s...')
                # led('green', '0')
                # time.sleep(60)
                # led('green', '1')
        else:
            with open(f'{dir}_camera_missed', 'w'):
                pass
            led('red','heartbeat',4)
    else:
        time.sleep(3)
