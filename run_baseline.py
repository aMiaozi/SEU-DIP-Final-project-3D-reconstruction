import pycolmap
import os
from pathlib import Path

# 1. 设置路径
project_dir = Path(".")
image_dir = project_dir / "images"/ "Lighthouse"#/"selected_50"
output_dir = project_dir / "outputs" / "baseline"/ "baseline_lighthouse"

output_dir.mkdir(parents=True, exist_ok=True)
database_path = output_dir / "database.db"

print("🚀 开始传统三维重建基线测试 (SIFT)...")

# 2. 提取特征
print("-> 正在提取特征...")
pycolmap.extract_features(database_path, image_dir)

# 3. 特征匹配
print("-> 正在匹配特征...")
pycolmap.match_exhaustive(database_path)

# 4. 三维重建 (增量式)
print("-> 正在进行增量式重建，这可能需要几分钟...")
maps = pycolmap.incremental_mapping(database_path, image_dir, output_dir)

# 5. 输出结果
if len(maps) > 0:
    best_model = maps[0]
    print("\n✅ 重建成功！")
    print(f"-> 成功注册(对齐)的照片数量: {best_model.num_reg_images()}")
    print(f"-> 生成的三维空间点数量: {best_model.num_points3D()}")

    # 将稀疏点云导出为 .ply 文件以便查看
    best_model.write(output_dir)
    print(f"-> 模型文件已保存至: {output_dir}")
else:
    print("\n❌ 重建失败：可能是照片重叠度不够，或者环境光线太暗。")