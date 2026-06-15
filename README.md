# 东南大学千弓楼 3D 重建

本项目基于 **SuperPoint + LightGlue + COLMAP + 3D Gaussian Splatting** 的完整管线，从视频截取的多视角图像重建东南大学千弓楼（Qiangong Building）的三维模型。

## 效果展示

> **TODO**: 插入 Supersplat 渲染截图 / 视频

## 重建流程

```
视频截取 → 特征提取 (SuperPoint) → 特征匹配 (LightGlue)
→ 增量式 SfM (COLMAP) → 去畸变 → 3DGS 辐射场优化
```

## 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.10 | 推荐 |
| PyTorch | 2.2.2 | 含 CUDA 12.1 |
| GPU | RTX 4060 8GB | 已验证可运行 |

### 依赖库

- `hloc` (Hierarchical Localization) — SuperPoint + LightGlue 封装
- `pycolmap` — COLMAP Python 接口
- `gaussian-splatting` — 3DGS 官方实现
- `ffmpeg` — 视频截取帧

```bash
pip install -r requirements.txt
```

### 第三方仓库准备（存放于 ../third_party/）

```bash
cd ../third_party
git clone https://github.com/cvg/Hierarchical-Localization.git
cd Hierarchical-Localization && pip install -e .

git clone https://github.com/cvg/LightGlue.git
cd LightGlue && pip install -e .

git clone https://github.com/graphdeco-inria/gaussian-splatting.git
cd gaussian-splatting && pip install -r requirements.txt
```

## 快速开始

### 1. 视频截取帧

```bash
ffmpeg -i your_video.mp4 -vf "fps=328/153" -q:v 2 ../data/images/frame_%04d.jpg
```

### 2. 特征提取与稀疏重建

```bash
python src/run_LightGlue.py \
    --image_dir ../data/images/SEU_QiangongBuilding \
    --output_dir ../models/SEU_QiangongBuilding_328
```

### 3. COLMAP 去畸变

```bash
colmap image_undistorter \
    --image_path ../data/images/SEU_QiangongBuilding \
    --input_path ../models/SEU_QiangongBuilding_328 \
    --output_path ../models/SEU_QiangongBuilding_328_PINHOLE \
    --output_type COLMAP
```

### 4. 3DGS 训练

```bash
python src/train.py \
    -s ../models/SEU_QiangongBuilding_328_PINHOLE \
    -r 4 \
    --iterations 30000
```

### 5. 查看模型

**SIBR 查看器**（本地，需将 ../tools/ 下的 SIBR 查看器加入 PATH）：
```bash
SIBR_gaussianViewer_app -m ./output/<model_folder>
```

**Supersplat**（在线）：
打开 https://superspl.at/editor，将 `point_cloud.ply` 拖入。

## 项目文件

```
.
├── src/
│   ├── run_LightGlue.py        # SuperPoint + LightGlue + COLMAP 稀疏重建
│   ├── run_baseline.py          # SIFT 基线对比（可选）
│   └── train.py               # 3D Gaussian Splatting 训练（适配相对路径）
├── docs/                       # 文档与截图（待补充）
├── report.md                   # 东南大学数字图像处理课程设计报告
├── requirements.txt            # Python 依赖
└── README.md                   # 本文件
```

## 工作区目录结构（与仓库同级）

```
../data/           # 原始图像、视频（不入 Git）
../models/         # COLMAP 与 3DGS 输出（不入 Git）
../third_party/    # Hierarchical-Localization, LightGlue, gaussian-splatting（子模块/克隆）
../tools/          # SIBR 查看器二进制与资源（不入 Git）
```

## 关键技术参数

| 参数 | 值 | 说明 |
|------|------|------|
| 输入图像数 | 328 | 4K 视频截取 |
| 特征点数 | 2048/图 | max_keypoints |
| 滑动窗口 | 10 | 匹配策略优化 |
| 训练分辨率 | -r 4 | 960×540，适配 RTX 4060 8GB |
| 训练迭代 | 30000 | 3DGS |
| 显存峰值 | ~6.8GB | 含 LightGlue 注意力 + 3DGS |

## 课程报告

详见 `report.md`：基于 LightGlue 特征匹配与 3DGS 的高精度三维重建——以东大千弓楼为例。

## 参考论文

1. Kerbl et al. 3D Gaussian Splatting for Real-Time Radiance Field Rendering. TOG 2023.
2. Schönberger & Frahm. Structure-from-Motion Revisited. CVPR 2016.
3. DeTone et al. SuperPoint: Self-Supervised Interest Point Detection and Description. CVPRW 2018.
4. Lindenberger et al. LightGlue: Local Feature Matching at Light Speed. ICCV 2023.

## 许可

本项目为东南大学数字图像处理课程设计，开源仅供学习交流。
