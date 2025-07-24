import calendar
import datetime
import json
import os
from PIL import Image, ImageDraw, ImageFont

# --- 共通ヘルパー関数 (変更なし) ---

def get_available_font(font_list):
    for font_path in font_list:
        if os.path.exists(font_path):
            return font_path
    return None

def load_schedule(json_path):
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"スケジュール読み込みエラー: {e}")
        return None

def wrap_text(text, font, max_width):
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

    # --- データ準備 (変更なし) ---
    now = datetime.datetime.now()
    today = datetime.date(now.year, now.month, now.day)
    tomorrow = today + datetime.timedelta(days=1)
    two_days = [today, tomorrow]

    try:
        schedule_data = load_schedule('schedule.json')
        current_month_data = None
        if schedule_data:
            for month_data in schedule_data:
                if month_data.get("year") == now.year and month_data.get("month") == now.month:
                    current_month_data = month_data
                    break

        members = ["Member A", "Member B", "Member C", "Member D"]
        if current_month_data and "members" in current_month_data:
            members = current_month_data["members"]

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
            
            # 日付ヘッダーを描画 (例: "今日 24 (木)")
            day_label = "きょう" if i == 0 else "あす"
            day_str = f"{day_label} {date.day} ({weekday_names[date.weekday()]})"
            draw.text((x_start, current_y), day_str, font=font_day_header, fill=0)
            current_y += 60 # ヘッダー下の余白

            date_str_iso = date.strftime("%Y-%m-%d")
            schedule_entry = None
            if current_month_data:
                schedule_entry = next((s for s in current_month_data.get("schedules", []) if s["date"] == date_str_iso), None)
            
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
