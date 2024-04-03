import cv2, os, time, torch, argparse, datetime
from NanoDet_PyTorch_CPU.nanodet.util import cfg, load_config, Logger
from NanoDet_PyTorch_CPU.nanodet.model.arch import build_model
from NanoDet_PyTorch_CPU.nanodet.util import load_model_weight
from NanoDet_PyTorch_CPU.nanodet.data.transform import Pipeline

from gpio import *


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
        self.model.head.show_result(meta['raw_img'], dets, class_names, score_thres=score_thres, show=False,
                                    save_path=save_path)
        print('viz time: {:.3f}s'.format(time.time() - time1))


# 调用摄像头拍一张照片
def take_photo():
    led('red',t1 = 0.2)

    cap = cv2.VideoCapture(1)
    cap.set(3,w)
    cap.set(4,h)
    ret, image = cap.read()
    print(f"分辨率: {cap.get(3)}x{cap.get(4)}")

    cap.release()
    if ret:
        return image
    else:
        raise ValueError('Could not take camera image')

led_trigger_mode = ['none', 'usb-gadget', 'usb-host', 'kbd-scrolllock', 'kbd-numlock', 'kbd-capslock', 'kbd-kanalock', 'kbd-shiftlock', 'kbd-altgrlock', 'kbd-ctrllock', 'kbd-altlock', 'kbd-shiftllock', 'kbd-shiftrlock', 'kbd-ctrlllock', 'kbd-ctrlrlock', 'usbport', 'disk-activity', 'disk-read', 'disk-write', 'ide-disk', 'mtd', 'nand-disk', 'heartbeat', 'cpu', 'cpu0', 'cpu1', 'cpu2', 'cpu3', 'activity', 'default-on', 'panic', 'mmc0', 'mmc2', 'mmc1', 'rfkill-any', 'rfkill-none', 'rfkill0', 'rc-feedback', 'rfkill1', 'bluetooth-power', 'hci0-power', 'rfkill2', 'stmmac-0:01:link', 'stmmac-0:01:1Gbps', 'stmmac-0:01:100Mbps', 'stmmac-0:01:10Mbps']
def led(color, mode='default-on', t1=0):
    if not t1:
        if mode in led_trigger_mode:
            os.system(f"sudo echo {mode} > /sys/devices/platform/leds/leds/{color}-led/trigger")
        else:
            print(f'{mode} is not supported led-mode')
    else:
        if mode in led_trigger_mode:
            os.system(f"sudo echo {mode} > /sys/devices/platform/leds/leds/{color}-led/trigger")
            time.sleep(t1)
            os.system(f"sudo echo none > /sys/devices/platform/leds/leds/{color}-led/trigger")
        else:
            print(f'{mode} is not supported led-mode')

def find_cat():
    # 开始推理时黄灯闪烁，发现猫黄灯常亮2-3s；未发现猫红灯常亮3s(所有推理结束后）
    led('green', 'heartbeat')
    raw_image = take_photo()

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
        led('green')
        print('cat!cat!cat!')
        power_motor(2)
        predictor.visualize(res, meta, cfg.class_names, 0.6, save_path=f'{path_dir}/{i}_findcat.jpg')
        return True
    else:
        print('no cat')
        cv2.imwrite(f'{path_dir}/{i}.jpg', raw_image)
        return False


# -------------------------------------------------------------------------------------------------------------------

led('green')
led('red', mode='none')
# 加载推理模型
load_config(cfg, './NanoDet_PyTorch_CPU/config/nanodet-m.yml')
logger = Logger(-1, use_tensorboard=False)
predictor = Predictor(cfg, 'NanoDet_PyTorch_CPU/model/nanodet_m.pth', logger)

# 摄像头的分辨率宽高组合，根据摄像头需要调整
rank_ls = ((1024, 768), (1280, 720), (1600, 1200), (1920, 1080),
           (2048, 1536), (2592, 1944), (3264, 2448), (3840, 2160), (3840, 3104))
w, h = rank_ls[3]


while 1:  # 每隔10秒检测一次
    if find_something() and not remain_food():
        dir = f'./capture/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
        path_dir = dir + '/'
        os.makedirs(path_dir, exist_ok=True)

        for i in range(10):
            if find_cat():
                os.renames(dir, dir + '_findcat')
                find = True

                # print('冷却10min...')
                led('green', '0')
                # time.sleep(600)
                led('green', '1')
                break
        else:
            os.renames(dir, dir + '_no')
            # 红灯常亮3s
            led('red', t1=3)

            # print('冷却60s...')
            # led('green', '0')
            # time.sleep(60)
            # led('green', '1')
    else:
        time.sleep(3)
