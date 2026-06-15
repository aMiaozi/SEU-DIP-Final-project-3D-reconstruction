import argparse
import pycolmap
import os
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="传统 SIFT 基线三维重建"
    )
    parser.add_argument(
        "--image_dir", type=str, required=True,
        help="输入图像目录"
    )
    parser.add_argument(
        "--output_dir", type=str, required=True,
        help="输出目录"
    )
    args = parser.parse_args()

    image_dir = Path(args.image_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    database_path = output_dir / "database.db"

    print("🚀 开始传统三维重建基线测试 (SIFT)...")
    print(f"   图像目录: {image_dir}")
    print(f"   输出目录: {output_dir}")

    # 提取特征
    print("-> 正在提取特征...")
    pycolmap.extract_features(database_path, image_dir)

    # 特征匹配
    print("-> 正在匹配特征...")
    pycolmap.match_exhaustive(database_path)

    # 三维重建 (增量式)
    print("-> 正在进行增量式重建，这可能需要几分钟...")
    maps = pycolmap.incremental_mapping(database_path, image_dir, output_dir)

    # 输出结果
    if len(maps) > 0:
        best_model = maps[0]
        print("\n✅ 重建成功！")
        print(f"-> 成功注册(对齐)的照片数量: {best_model.num_reg_images()}")
        print(f"-> 生成的三维空间点数量: {best_model.num_points3D()}")

        best_model.write(output_dir)
        print(f"-> 模型文件已保存至: {output_dir}")
    else:
        print("\n❌ 重建失败：可能是照片重叠度不够，或者环境光线太暗。")
