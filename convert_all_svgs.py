import os
import cairosvg

print("Icon conversion script started.")

# --- パス設定 ---
base_dir = os.path.dirname(__file__)
icons_dest_dir = os.path.join(base_dir, 'icons') # PNGの保存先

# --- 天気アイコンの変換 ---
weather_source_dir = os.path.join(base_dir, 'weather-crow5.7', 'svg', 'weatherConditions')
OWM_CODES = [f"{i:02d}{s}" for i in [1, 2, 3, 4, 9, 10, 11, 13, 50] for s in ['d', 'n']]

if not os.path.exists(icons_dest_dir):
    os.makedirs(icons_dest_dir)
    print(f"Created directory: {icons_dest_dir}")

print("\n--- Converting Weather Icons ---")
for code in OWM_CODES:
    svg_filename = f"icon-{code}.svg"
    png_filename = f"{code}.png"
    source_path = os.path.join(weather_source_dir, svg_filename)
    dest_path = os.path.join(icons_dest_dir, png_filename)

    if os.path.exists(source_path):
        print(f"Converting {svg_filename} -> {png_filename}...")
        try:
            cairosvg.svg2png(url=source_path, write_to=dest_path, output_width=200, output_height=200)
        except Exception as e:
            print(f"  Error converting {svg_filename}: {e}")

# --- 摂氏アイコンの変換 ---
print("\n--- Converting Celsius Icon ---")
celsius_source_path = os.path.join(base_dir, 'weather-crow5.7', 'svg', 'degree', 'degrees.svg')
celsius_dest_path = os.path.join(icons_dest_dir, 'celsius.png') # celsius.pngとして保存

if os.path.exists(celsius_source_path):
    print("Converting degrees.svg -> celsius.png...")
    try:
        cairosvg.svg2png(url=celsius_source_path, write_to=celsius_dest_path, output_height=400) # 高さを基準に高品質で変換
    except Exception as e:
        print(f"  Error converting degrees.svg: {e}")

print("\nIcon conversion complete.")
