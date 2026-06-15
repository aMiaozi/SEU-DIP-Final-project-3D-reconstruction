import argparse
import os
import pycolmap
from pathlib import Path
from hloc import extract_features, match_features, reconstruction
import torch
import gc


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="基于 SuperPoint + LightGlue 的图像特征提取与增量式 SfM 三维重建"
    )
    parser.add_argument(
        "--image_dir", type=str, required=True,
        help="输入图像目录（如 ./images/SEU_QiangongBuilding）"
    )
    parser.add_argument(
        "--output_dir", type=str, required=True,
        help="输出目录（如 ./outputs/SEU_QiangongBuilding_328）"
    )
    parser.add_argument(
        "--window", type=int, default=10,
        help="滑动窗口大小，控制匹配对数量（默认 10）"
    )
    parser.add_argument(
        "--max_keypoints", type=int, default=2048,
        help="每张图像最大特征点数（默认 2048，降低可节省显存）"
    )
    parser.add_argument(
        "--resize_max", type=int, default=1200,
        help="预处理最长边尺寸（默认 1200）"
    )
    args = parser.parse_args()

    image_dir = Path(args.image_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    feature_path = output_dir / "features.h5"
    match_path = output_dir / "matches.h5"
    sfm_pairs = output_dir / "pairs-exhaustive.txt"

    feature_conf = {
        'output': 'superpoint',
        'model': {
            'name': 'superpoint',
            'nms_radius': 4,
            'max_keypoints': args.max_keypoints
        },
        'preprocessing': {
            'grayscale': True,
            'resize_max': args.resize_max
        }
    }

    matcher_conf = {
        'output': 'lightglue',
        'model': {
            'name': 'lightglue',
            'features': 'superpoint',
            'flash': False,
            'mp': True,
            'depth_confidence': 0.9,
            'width_confidence': 0.95
        }
    }

    print(f"🚀 启动 SuperPoint + LightGlue 特征提取与重建...")
    print(f"   图像目录: {image_dir}")
    print(f"   输出目录: {output_dir}")
    print(f"   滑动窗口: {args.window}")

    # 1. 提取特征
    print("\n[1/4] 使用 SuperPoint 提取深度特征...")
    extract_features.main(feature_conf, image_dir, feature_path=feature_path)

    print("\n🧹 清理 GPU 缓存...")
    gc.collect()
    torch.cuda.empty_cache()

    # 2. 滑动窗口生成配对
    print(f"\n[2/4] 滑动窗口生成配对（窗口大小={args.window}）...")
    image_list = sorted([
        f for f in os.listdir(image_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])
    pairs = []
    num_images = len(image_list)
    for i in range(num_images):
        for j in range(1, args.window + 1):
            idx = (i + j) % num_images  # 环绕闭环
            pairs.append(f"{image_list[i]} {image_list[idx]}")
    with open(sfm_pairs, "w", encoding="utf-8") as f:
        f.write("\n".join(pairs))
    print(f"-> 配对数量: {len(pairs)} 对")

    # 3. 特征匹配
    print("\n[3/4] 使用 LightGlue 进行特征匹配...")
    match_features.main(matcher_conf, sfm_pairs, features=feature_path, matches=match_path)

    # 4. 增量式 SfM 重建
    print("\n[4/4] 进行增量式三维重建...")
    model = reconstruction.main(output_dir, image_dir, sfm_pairs, feature_path, match_path)

    if model is not None:
        print("\n✅ 重建成功！")
        print(f"   注册图像数: {model.num_reg_images()}")
        print(f"   三维点数: {model.num_points3D()}")
        print(f"   模型保存至: {output_dir}")
    else:
        print("\n❌ 重建失败，请检查图像或配置。")
