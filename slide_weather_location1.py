# This script utilizes assets (icons, font) from the 'weather-crow5.7' repository.
# Copyright (c) 2024 kotamorishi
# Project: https://github.com/kotamorishi/weather-crow5.7
# This asset is licensed under the MIT License.

# ===================================================================
# 1. ライブラリのインポート
# -------------------------------------------------------------------
# これから使う様々な機能を、外部の「ライブラリ」から読み込みます。
# ===================================================================
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageChops
import time
import io
import json
import cairosvg

# ===================================================================
# 2. 定数とグローバル変数の設定
# -------------------------------------------------------------------
# プログラム全体で使う、変わらない値（定数）や設定をここで定義します。
# ===================================================================

# .envファイルに記述されたシークレット情報（APIキーなど）を読み込む
load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY") # .envファイルからAPIキーを取得

# --- 表示とレイアウト関連 ---
SCREEN_WIDTH = 800       # e-paperディスプレイの幅（ピクセル）
SCREEN_HEIGHT = 480      # e-paperディスプレイの高さ（ピクセル）

# --- アセット（外部ファイル）のパス設定 ---
ICON_PATH = os.path.join(os.path.dirname(__file__), 'icons')
FONT_CANDIDATES = [os.path.join(os.path.dirname(__file__), 'fonts', 'ReggaeOne-Regular.ttf')]
FONT_BOLD_CANDIDATES = [os.path.join(os.path.dirname(__file__), 'fonts', 'ReggaeOne-Regular.ttf')]

# --- キャッシュ機能関連 ---
# このロケーション1専用のキャッシュを保存するためのグローバル変数
_weather_cache_loc1 = None
_cache_timestamp_loc1 = 0
CACHE_DURATION = 1800    # キャッシュの有効期間（秒）。1800秒 = 30分

# ===================================================================
# 3. ヘルパー関数定義
# -------------------------------------------------------------------
# 特定の仕事をする小さな「機能のまとまり（関数）」を定義していきます。
# ===================================================================

def load_config(location_key):
    """設定ファイル(config.json)から指定されたロケーションの設定を読み込む"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load()
        # config.jsonの中から、引数で指定されたキー(例: 'weather_slide_loc1')の部分だけを返す
        return config.get(location_key, {})
    except Exception as e:
        print(f"設定ファイル読み込みエラー: {e}")
        return {} # エラーの場合は空の設定を返す

def get_available_font(font_list):
    """利用可能なフォントを探す"""
    for font_path in font_list:
        if os.path.exists(font_path): return font_path
    return None

def get_weather_data(lat, lon):
    """緯度(lat)と経度(lon)に基づいてAPIから天気データを取得する"""
    try:
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=en"
        current_response = requests.get(current_url); current_response.raise_for_status()
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=en"
        forecast_response = requests.get(forecast_url); forecast_response.raise_for_status()
        return {"current": current_response.json(), "forecast": forecast_response.json()}
    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}"); return None

def process_weather_data(data, city_name):
    """APIから取得した生のデータを、画面表示に使いやすい形に整理・加工する"""
    if not data: return None
    current = data['current']
    current_info = {
        "temp": round(current["main"]["temp"]), "description": current["weather"][0]["description"].title(),
        "icon": current["weather"][0]["icon"], "feels_like": round(current["main"]["feels_like"]),
        "humidity": current["main"]["humidity"],
    }
    hourly_forecasts = [
        {"time": datetime.fromtimestamp(h['dt']).strftime('%H:00'), "temp": round(h['main']['temp']), 
         "icon": h['weather'][0]['icon'], "pop": int(h.get('pop', 0) * 100)}
        for h in data['forecast']['list'][:4]
    ]
    return {"current": current_info, "hourly": hourly_forecasts, "city": city_name, "last_updated": datetime.now().strftime("%b %d, %H:%M")}

def get_icon_image(icon_code, size):
    """天気アイコンのPNGファイルを読み込み、e-paper表示用に変換する"""
    icon_file_path = os.path.join(ICON_PATH, f"{icon_code}.png")
    if not os.path.exists(icon_file_path): return None
    with Image.open(icon_file_path) as icon_img:
        icon_img = icon_img.convert("RGBA")
        resized_image = icon_img.resize((size, size), Image.Resampling.LANCZOS)
        background = Image.new('RGBA', resized_image.size, (255, 255, 255, 255))
        background.paste(resized_image, (0, 0), resized_image)
        final_image = background.convert('1', dither=Image.FLOYDSTEINBERG)
        return final_image

def create_celsius_icon(height):
    """摂氏（℃）のSVGアイコンを読み込み、高品質な白黒画像に変換する"""
    svg_path = os.path.join(os.path.dirname(__file__), 'weather-crow5.7', 'svg', 'degree', 'degrees.svg')
    if not os.path.exists(svg_path): return None
    try:
        # SVGを指定された高さでPNGデータに変換
        png_data = cairosvg.svg2png(url=svg_path, output_height=height * 5)
        # PNGデータをグレースケール画像として読み込み
        high_res_image = Image.open(io.BytesIO(png_data)).convert("L")
        # アスペクト比を維持してリサイズ
        aspect_ratio = high_res_image.width / high_res_image.height
        target_width = int(height * aspect_ratio)
        resized_image = high_res_image.resize((target_width, height), Image.Resampling.LANCZOS)
        # しきい値処理でくっきりとした白黒画像（1bit）に変換
        return resized_image.point(lambda p: 0 if p < 128 else 255, '1')
    except Exception as e:
        print(f"摂氏アイコンの処理エラー: {e}"); return None

# ===================================================================
# 4. メインの描画関数
# -------------------------------------------------------------------
# このスクリプトの本体。天気情報を取得し、一枚の画像（スライド）を生成します。
# ===================================================================

def create_weather_slide_loc1():
    """ロケーション1の天気スライドを生成する"""
    # この関数専用のキャッシュをグローバル変数として扱うことを宣言
    global _weather_cache_loc1, _cache_timestamp_loc1

    # --- 1. 設定ファイルからこのロケーション専用の情報を読み込む ---
    config = load_config('weather_slide_loc1')
    # .get()を使うと、もし設定がなくてもプログラムが止まらず、第2引数のデフォルト値が使われる
    lat = config.get('latitude', 35.6895) # デフォルト: 東京
    lon = config.get('longitude', 139.6917)
    city_name = config.get('city_name', 'Location 1')

    # --- 2. 天気データの取得（キャッシュを賢く利用） ---
    now = time.time()
    weather_data = None
    if _weather_cache_loc1 and (now - _cache_timestamp_loc1 < CACHE_DURATION):
        print(f"{city_name}: 天気データをキャッシュから使用します。")
        weather_data = _weather_cache_loc1
        weather_data['last_updated'] = datetime.now().strftime("%b %d, %H:%M")
    else:
        print(f"{city_name}: 新しい天気データをAPIから取得します。")
        raw_data = get_weather_data(lat, lon)
        if raw_data:
            weather_data = process_weather_data(raw_data, city_name)
            _weather_cache_loc1 = weather_data
            _cache_timestamp_loc1 = now
    
    # --- 3. 描画の準備 ---
    image = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255); draw = ImageDraw.Draw(image)
    regular_font = get_available_font(FONT_CANDIDATES); bold_font = get_available_font(FONT_BOLD_CANDIDATES)
    
    if not regular_font or not bold_font:
        draw.text((10, 10), "Font files not found.", fill=0); return image
        
    try:
        # --- 4. 使用するフォントの種類を定義 ---
        font_city_large = ImageFont.truetype(regular_font, 108)
        font_city_regular = ImageFont.truetype(regular_font, 36)
        font_temp = ImageFont.truetype(bold_font, 168)
        font_desc = ImageFont.truetype(regular_font, 32)
        font_detail = ImageFont.truetype(regular_font, 26)
        font_hourly_time = ImageFont.truetype(regular_font, 28)
        font_hourly_temp = ImageFont.truetype(bold_font, 28)
        font_hourly_pop = ImageFont.truetype(regular_font, 20)
    except IOError:
        draw.text((10, 10), "Font loading failed.", fill=0); return image
        
    if not weather_data:
        draw.text((50, 50), "Could not get data", font=font_city_regular, fill=0); return image
        
    # --- 5. レイアウトの基準となる座標を定義 ---
    margin = 48; divider_x = int(SCREEN_WIDTH * 0.46); left_center_x = divider_x // 2; city_y = margin + 8
    icon_y = city_y + 110; temp_y = icon_y + 100
    right_column_x_start = divider_x + 40; right_column_x_end = SCREEN_WIDTH - margin
    hourly_y_start = margin + 20; hourly_item_height = 68
    
    # --- 6. 各要素の描画 ---

    # 都市名（ドロップキャップ）
    city_text = weather_data['city']; first_letter = city_text[0]; rest_of_text = city_text[1:]
    fl_bbox = font_city_large.getbbox(first_letter); rot_bbox = font_city_regular.getbbox(rest_of_text)
    fl_width = fl_bbox[2] - fl_bbox[0]; rot_width = rot_bbox[2] - rot_bbox[0]
    total_width = fl_width + rot_width; start_x = left_center_x - (total_width // 2)
    fl_ascent, _ = font_city_large.getmetrics(); rot_ascent, _ = font_city_regular.getmetrics()
    y_offset_for_large_letter = rot_ascent - fl_ascent
    draw.text((start_x, city_y + y_offset_for_large_letter), first_letter, font=font_city_large, fill=0)
    draw.text((start_x + fl_width, city_y), rest_of_text, font=font_city_regular, fill=0)
    
    # メインの天気アイコン
    if icon := get_icon_image(weather_data['current']['icon'], 140): 
        image.paste(icon, (left_center_x - 70, icon_y))
        
    # 現在気温
    temp_text = f"{weather_data['current']['temp']}"; temp_bbox = font_temp.getbbox(temp_text)
    draw.text((left_center_x - (temp_bbox[2] - temp_bbox[0]) // 2, temp_y), temp_text, font=font_temp, fill=0)

    # 摂氏アイコン
    if celsius_icon := create_celsius_icon(height=80):
        celsius_x = left_center_x + (temp_bbox[2] - temp_bbox[0]) // 2 + 10
        celsius_y = temp_y + 30
        mask = ImageChops.invert(celsius_icon) # アイコンの黒い部分だけを貼り付けるためのマスクを作成
        image.paste(celsius_icon, (celsius_x, celsius_y), mask)
            
    # 時間別予報（4時間分をループで描画）
    for i, hour in enumerate(weather_data['hourly']):
        y = hourly_y_start + i * hourly_item_height; draw.text((right_column_x_start, y), hour['time'], font=font_hourly_time, fill=0)
        if icon := get_icon_image(hour['icon'], 44): 
            image.paste(icon, (right_column_x_start + 88, y - 2))
            
        temp_text_hourly = f"{hour['temp']}°"; temp_hourly_bbox = font_hourly_temp.getbbox(temp_text_hourly)
        draw.text((right_column_x_end - (temp_hourly_bbox[2] - temp_hourly_bbox[0]), y), temp_text_hourly, font=font_hourly_temp, fill=0)
        
        pop_text = f"{hour['pop']}%"; pop_bbox = font_hourly_pop.getbbox(pop_text)
        draw.text((right_column_x_end - (pop_bbox[2] - pop_bbox[0]), y + 32), pop_text, font=font_hourly_pop, fill=0)
        
    # 区切り線
    separator_y = hourly_y_start + len(weather_data['hourly']) * hourly_item_height + 8
    draw.line((right_column_x_start, separator_y, right_column_x_end, separator_y), fill=0, width=1)
    
    # 詳細情報（体感温度と湿度）
    details_y_start = separator_y + 24
    draw.text((right_column_x_start, details_y_start), f"Feels like {weather_data['current']['feels_like']}°C", font=font_detail, fill=0)
    
    # 下揃えのテキスト（天気概況と湿度）
    bottom_align_y = details_y_start + 60
    draw.text((right_column_x_start, bottom_align_y + font_detail.getmetrics()[1]), f"Humidity {weather_data['current']['humidity']}%", font=font_detail, fill=0, anchor="lb")
    # draw.text((left_center_x, bottom_align_y + font_desc.getmetrics()[1]), weather_data['current']['description'], font=font_desc, fill=0, anchor="mb")
    
    # 最終的に完成した画像を返す
    return image
