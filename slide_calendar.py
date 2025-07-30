import calendar
import datetime
import json
import os
from PIL import Image, ImageDraw, ImageFont

# ===================================================================
#
# このスクリプトの要約（初心者向け解説）
#
# -------------------------------------------------------------------
# ■ 何をするの？
# -------------------------------------------------------------------
# このプログラムは、「きょう」と「あす」の二日分のスケジュールが
# 書かれた一枚の画像（カレンダーのスライド）を作ります。
#
# 以前のバージョンからデザインが新しくなり、日本語の曜日を使ったり、
# 予定がある人の名前を太字にして、より見やすくなるように工夫されています。
#
#
# -------------------------------------------------------------------
# ■ どうやって動くの？ (処理のステップ)
# -------------------------------------------------------------------
#
# STEP 1: 必要な道具（ライブラリ）を準備する
# --------------------------------------------
# `import` と書かれている部分で、プログラム作りに必要な「道具」を
# Pythonに読み込ませています。
#
# - `datetime`: 「今日」の日付や曜日などを正確に知るための道具
# - `json`    : `schedule.json` というファイルに書かれた予定表を読み解く道具
# - `PIL`     : 画像に文字や図形を描くための、高機能な画材セットのような道具
#
#
# STEP 2: 小さな便利ツール（ヘルパー関数）を定義する
# --------------------------------------------
# プログラムの中で何度も登場する作業は、便利な「関数」としてひとまとめに
# しておきます。
#
# - `load_schedule()`:
#   予定が書かれた `schedule.json` ファイルを開けて、中身を読み込む係です。
#
# - `get_schedule_for_date()`:
#   このスクリプトで最も重要な関数です。たくさんの予定の中から、指定された
#   「たった一日分」の予定だけを正確に見つけ出す、腕利きの探偵のような役割です。
#   月末に明日（翌月）の予定を探すという難しい任務も、この関数が解決してくれます。
#
# - `get_available_font()`, `wrap_text()`:
#   文字を描くためのフォントを探したり、長い予定を読みやすく改行したりする、
#   アシスタント的な関数です。
#
#
# STEP 3: メインの処理でカレンダー画像を組み立てる (`create_calendar_slide`)
# --------------------------------------------
# ここからが、実際にカレンダー画像を一枚の絵として完成させていくメイン作業です。
#
# 1. まっ白なキャンバスを用意する
#    - これから絵を描くための、まっ白な画像（キャンバス）を用意します。
#
# 2. 日付と予定を準備する
#    - 「今日」と「明日」の日付を計算し、`schedule.json` から全データを読み込みます。
#
# 3. キャンバスに描画していく
#    - まず、"2025年7月 スケジュール" のようなタイトルを描きます。
#    - 画面を左右二つに分け、「きょう」と「あす」のエリアを作ります。
#    - それぞれのエリアに、以下の処理を行います。
#
#      a. 日付ヘッダーを描く
#         - "きょう 31 (木)" のような、分かりやすいヘッダーを描きます。
#
#      b. その日の予定を探す
#         - 腕利き探偵 `get_schedule_for_date()` を呼び出し、その日の予定と
#           メンバーリストを正確に受け取ります。
#
#      c. メンバーごとに予定を描く
#         - 家族メンバーを一人ずつ順番に見ていきます。
#         - もし予定があれば、名前を**太字**で描き、その下に予定内容を書きます。
#         - 予定がなければ、名前を普通の太さで描きます。
#
# 4. 完成！
#    - すべて描き終わったら、完成したカレンダー画像を返します。
#
#
# STEP 4: テスト実行 (`if __name__ == "__main__":`)
# --------------------------------------------
# このファイルを直接実行したときだけ動く、テスト用のコードです。
# 作成した画像を `calendar_test.png` という名前で保存し、
# 意図した通りに表示されるか確認するために使います。
#
# ===================================================================


# --- 共通ヘルパー関数 ---

def get_available_font(font_list):
    """指定されたフォントパスのリストから、最初に見つかった有効なパスを返す"""
    for font_path in font_list:
        if os.path.exists(font_path):
            return font_path
    return None

def load_schedule(json_path):
    """スケジュールデータをJSONファイルから読み込む"""
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"スケジュール読み込みエラー: {e}")
        return None

def wrap_text(text, font, max_width):
    """指定された幅でテキストを折り返す"""
    lines = []
    if not text:
        return []
    words = text.split(' ')
    current_line = ''
    for word in words:
        if font.getbbox(current_line + ' ' + word)[2] <= max_width:
            current_line += ' ' + word if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def get_schedule_for_date(schedule_data, target_date):
    """
    指定された日付のスケジュールエントリとメンバーリストを返す。
    月をまたいでも正しく検索する。
    """
    if not schedule_data:
        return None, None

    target_year = target_date.year
    target_month = target_date.month
    target_date_str = target_date.strftime("%Y-%m-%d")

    # 該当する年月のデータブロックを検索
    month_data = next((m for m in schedule_data if m.get("year") == target_year and m.get("month") == target_month), None)
    
    if not month_data:
        return None, None

    # その月のデータから該当日付のスケジュールを検索
    schedule_entry = next((s for s in month_data.get("schedules", []) if s["date"] == target_date_str), None)
    members = month_data.get("members", [])
    
    return schedule_entry, members


# ===================================================================
# ★★★ ここからが新しいデザインのコードです ★★★
# ===================================================================

def create_calendar_slide():
    """
    視覚的階層と余白を重視したカレンダースライドを生成する。
    """
    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 480
    image = Image.new('1', (IMAGE_WIDTH, IMAGE_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    # --- フォント定義 (より意図的に) ---
    font_path_regular = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansCJK-Regular.otf')
    font_path_bold = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansCJK-Bold.otf')

    font_candidates_regular = [font_path_regular, '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']
    font_candidates_bold = [font_path_bold, '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']

    font_regular = get_available_font(font_candidates_regular)
    font_bold = get_available_font(font_candidates_bold)

    if not font_regular or not font_bold:
        draw.text((20, 20), "Font not found.", fill=0)
        return image

    # 階層を意識したフォントサイズ
    font_title = ImageFont.truetype(font_regular, 24)
    font_day_header = ImageFont.truetype(font_bold, 36)
    font_member_active = ImageFont.truetype(font_bold, 24)
    font_member_inactive = ImageFont.truetype(font_regular, 24) # 予定がないメンバー用
    font_schedule = ImageFont.truetype(font_regular, 22)
    font_small = ImageFont.truetype(font_regular, 16)

    # --- データ準備 ---
    now = datetime.datetime.now()
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    two_days = [today, tomorrow]

    try:
        # スケジュールデータを最初に一括で読み込むだけにする
        schedule_data = load_schedule('schedule.json')

        # --- 新しいレイアウトでの描画 ---

        # 1. 全体のタイトル (少し控えめに)
        header = f"{now.year}年{now.month}月 スケジュール"
        draw.text((40, 30), header, font=font_title, fill=0)

        # 2. レイアウト設定値
        y_start = 90
        column_width = 400
        padding = 40
        indicator_width = 5 # 予定ありを示すバーの幅

        weekday_names = ["月", "火", "水", "木", "金", "土", "日"]

        # 3. 「今日」と「明日」の2つのカラムを描画
        for i, date in enumerate(two_days):
            x_start = padding + i * column_width
            current_y = y_start

            # 日付ヘッダーを描画 (例: "きょう 24 (木)")
            day_label = "きょう" if i == 0 else "あす"
            day_str = f"{day_label} {date.day} ({weekday_names[date.weekday()]})"
            draw.text((x_start, current_y), day_str, font=font_day_header, fill=0)
            current_y += 60 # ヘッダー下の余白

            # 新しいヘルパー関数を使い、日付ごとにスケジュールとメンバーを検索
            schedule_entry, members = get_schedule_for_date(schedule_data, date)
            
            # もしその日のデータがJSONになければ、デフォルトのメンバーリストを使う
            if not members:
                members = ["Member A", "Member B", "Member C", "Member D"]

            # 4. 各メンバーのスケジュールを描画
            for member in members:
                schedule_text = schedule_entry.get(member, "") if schedule_entry else ""

                # 予定がある場合とない場合で、見た目を明確に変える
                if schedule_text:
                    # 【予定あり】
                    # 左側にインジケータバーを描画
                    draw.rectangle([(x_start, current_y), (x_start + indicator_width, current_y + 60)], fill=0)

                    # メンバー名をボールドで描画
                    draw.text((x_start + indicator_width + 15, current_y), member, font=font_member_active, fill=0)
                    current_y += 35 # メンバー名と予定内容の間の余白

                    # 予定内容を折り返して描画
                    max_text_width = column_width - padding - (indicator_width + 15)
                    schedule_lines = wrap_text(schedule_text, font_schedule, max_text_width)
                    for line in schedule_lines:
                        draw.text((x_start + indicator_width + 15, current_y), line, font=font_schedule, fill=0)
                        current_y += 30 # 予定の行間
                    current_y += 20 # 次のメンバーとの間の余白
                else:
                    # 【予定なし】
                    # メンバー名を通常の太さで静かに表示
                    draw.text((x_start, current_y), member, font=font_member_inactive, fill=0)
                    current_y += 55 # 次のメンバーとの間の余白

    except Exception as e:
        draw.text((40, 40), "カレンダーの表示に失敗しました", font=font_day_header, fill=0)
        draw.text((40, 100), f"エラー: {str(e)}", font=font_small, fill=0)

    return image

if __name__ == "__main__":
    image = create_calendar_slide()
    image.save("calendar_test.png")
    image.show()
