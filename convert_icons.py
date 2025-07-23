import os
import cairosvg

print("Icon conversion script started.")

# OpenWeatherMapで使われるアイコンコードのリスト
OWM_CODES = [f"{i:02d}{s}" for i in [1, 2, 3, 4, 9, 10, 11, 13, 50] for s in ['d', 'n']]

# パス設定
base_dir = os.path.dirname(__file__)
source_dir = os.path.join(base_dir, 'weather-crow5.7', 'svg', 'weatherConditions')
dest_dir = os.path.join(base_dir, 'icons')

# 保存先ディレクトリがなければ作成
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
    print(f"Created directory: {dest_dir}")

# 変換処理
for code in OWM_CODES:
    svg_filename = f"icon-{code}.svg"
    png_filename = f"{code}.png"
    
    source_path = os.path.join(source_dir, svg_filename)
    dest_path = os.path.join(dest_dir, png_filename)

    if os.path.exists(source_path):
        print(f"Converting {svg_filename} -> {png_filename}...")
        try:
            # SVGをPNGに変換して保存（200x200ピクセルのサイズで）
            cairosvg.svg2png(url=source_path, write_to=dest_path, output_width=200, output_height=200)
        except Exception as e:
            print(f"  Error converting {svg_filename}: {e}")
    else:
        # 元のリポジトリに存在しないアイコンコードはスキップ
        pass

print("\nIcon conversion complete.")
