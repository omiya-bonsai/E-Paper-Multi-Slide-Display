# This script utilizes assets (icons, font) from the 'weather-crow5.7' repository.
#
# Copyright (c) 2024 kotamorishi
# Project: https://github.com/kotamorishi/weather-crow5.7
#
# This asset is licensed under the MIT License.

import time
from PIL import Image
# --- ファイル名と関数名を一般化 ---
from slide_weather_location1 import create_weather_slide_loc1
from slide_calendar import create_calendar_slide
from slide_learning import create_learning_slide
from slide_weather_location2 import create_weather_slide_loc2

# e-Paper表示用のユーティリティをインポート
from utils.epaper import init_display, display_image, sleep_display, full_refresh_cycle

# グローバル変数
REFRESH_INTERVAL = 180  # 更新間隔（秒）
FULL_REFRESH_COUNT = 12 # スライドが4枚になったため、完全更新の閾値を調整

def main():
    try:
        # ディスプレイの初期化
        epd = init_display()

        # 表示カウンター
        display_count = 0

        # スライドを順番に表示するループ
        while True:
            # 一定回数表示したら完全リフレッシュ
            if display_count >= FULL_REFRESH_COUNT:
                print("完全リフレッシュサイクルを実行")
                full_refresh_cycle(epd)
                display_count = 0

            # --- スライド0: 天気予報 (ロケーション1) ---
            print("スライド0: 天気予報 (ロケーション1)")
            weather_image = create_weather_slide_loc1()
            rotated_image = weather_image.transpose(Image.ROTATE_180)
            display_image(epd, rotated_image)
            display_count += 1
            sleep_display(epd)
            time.sleep(REFRESH_INTERVAL)
            epd.init()

            # --- スライド1: カレンダーの表示 ---
            print("スライド1: カレンダーの表示")
            calendar_image = create_calendar_slide()
            rotated_calendar_image = calendar_image.transpose(Image.ROTATE_180)
            display_image(epd, rotated_calendar_image)
            display_count += 1
            sleep_display(epd)
            time.sleep(REFRESH_INTERVAL)
            epd.init()

            # --- スライド2: 今日の学習ポイントの表示 ---
            print("スライド2: 今日の学習ポイントの表示")
            learning_image = create_learning_slide()
            rotated_learning_image = learning_image.transpose(Image.ROTATE_180)
            display_image(epd, rotated_learning_image)
            display_count += 1
            sleep_display(epd)
            time.sleep(REFRESH_INTERVAL)
            epd.init()

            # --- スライド3: 天気予報 (ロケーション2) ---
            print("スライド3: 天気予報 (ロケーション2)")
            weather_image_yomitan = create_weather_slide_loc2()
            rotated_image_yomitan = weather_image_yomitan.transpose(Image.ROTATE_180)
            display_image(epd, rotated_image_yomitan)
            display_count += 1
            sleep_display(epd)
            time.sleep(REFRESH_INTERVAL)
            epd.init()

    except KeyboardInterrupt:
        print("プログラムを終了します")
        white_image = Image.new('1', (epd.width, epd.height), 255)
        epd.display(epd.getbuffer(white_image))
        sleep_display(epd)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        if 'epd' in locals() and epd:
            sleep_display(epd)

if __name__ == "__main__":
    main()
