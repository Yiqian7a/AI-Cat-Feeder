## 1. 简介

本项目是山东大学威海校区22级数科班第一学年大作业，目标是为流浪猫设计一个户外喂猫机，搭配人工智能实现自动检测猫并投放猫粮。

该项目基于[ncnn高性能神经网络前向计算框架](https://github.com/Tencent/ncnn)和[Nanodet-pytorch目标检测模型](https://github.com/guo-pu/NanoDet-PyTorch)搭建，实际部署使用搭载`Ubuntu22.04`系统的[Orang Pi 3 LTS](http://www.orangepi.cn/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-3-LTS.html)开发版。

## 2. 配置环境

### 2.1 安装miniconda

### 2.2 修改gpio映射

进入OPi库的路径修改

```bash
cd /usr/local/lib/
find . -name "OPi*"
```

进入OPi文件夹下，找到`pin_mappings.py`文件

将下面的映射字典替换原有的字典，注意只要修改`BOARD{ }`中的内容：

```python
_pin_map = {
    BOARD: {
        3: 122,
        5: 121,
        7: 118,
        8: 354,
        10: 355,
        11: 120,
        12: 114,
        13: 119,
        15: 362,
        16: 111,
        18: 112,
        19: 229,
        21: 230,
        22: 117,
        23: 228,
        24: 227,
        26: 360
    },
```

