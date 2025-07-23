import calendar
import datetime
import json
import os
from PIL import Image, ImageDraw, ImageFont

def get_available_font(font_list):
    """
    フォント候補のリストを受け取り、システム内に存在する最初のフォントファイルのパスを返す関数。
    """
    for font_path in font_list:
        if os.path.exists(font_path):
            return font_path
    return None

def load_schedule(json_path):
    """
    スケジュールJSONファイルを読み込んで返す関数。
    """
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            return None
    except Exception as e:
        print(f"スケジュール読み込みエラー: {e}")
        return None

def wrap_text(text, font, max_width):
    """
    テキストをフォントと最大幅に基づいて折り返す。
    """
    lines = []
    if not text:
        return []

    words = text.split(' ')
    current_line = ''
    for word in words:
        # 単語を追加して幅をチェック
        if font.getbbox(current_line + ' ' + word)[2] <= max_width:
            current_line += ' ' + word if current_line else word
        else:
            # 幅を超えるなら改行
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def create_calendar_slide():
    """
    固定セル高さでレイアウトを安定させたカレンダースライドを生成する。
    """
    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 480

    image = Image.new('1', (IMAGE_WIDTH, IMAGE_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    # --- フォント定義 ---
    # ★★★ 修正: プロジェクト内のフォントを相対パスで参照 ★★★
    # プロジェクトのルートに'fonts'ディレクトリがあることを想定
    font_path_regular = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansCJK-Regular.otf')
    font_path_bold = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansCJK-Bold.otf')
    
    # フォントが見つからない場合の代替パスも用意
    font_candidates_regular = [font_path_regular, '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']
    font_candidates_bold = [font_path_bold, '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']

    font_regular = get_available_font(font_candidates_regular)
    font_bold = get_available_font(font_candidates_bold)

    # フォントが見つからない場合はエラーを描画して終了
    if not font_regular or not font_bold:
        draw.text((20, 20), "Font not found.", fill=0)
        return image

    title_font = ImageFont.truetype(font_regular, 30)
    day_font = ImageFont.truetype(font_regular, 26)
    name_font = ImageFont.truetype(font_bold, 20)
    schedule_font = ImageFont.truetype(font_regular, 20)
    small_font = ImageFont.truetype(font_regular, 16)


    now = datetime.datetime.now()
    today = datetime.date(now.year, now.month, now.day)
    tomorrow = today + datetime.timedelta(days=1)
    two_days = [today, tomorrow]

    try:
        # ★★★ 修正: ファイル名を一般化 ★★★
        schedule_data = load_schedule('schedule.json')
        current_month_data = None
        if schedule_data:
            for month_data in schedule_data:
                if month_data.get("year") == now.year and month_data.get("month") == now.month:
                    current_month_data = month_data
                    break

        # ★★★ 修正: 個人名をサンプルデータに変更 ★★★
        # スケジュールファイルにメンバー情報がなければ、このサンプル名が使われる
        members = ["Member A", "Member B", "Member C", "Member D"]
        if current_month_data and "members" in current_month_data:
            members = current_month_data["members"]

        header = f"{now.year}年{now.month}月 今日・明日のスケジュール"
        draw.text((20, 10), header, font=title_font, fill=0)

        weekday_names = ["月", "火", "水", "木", "金", "土", "日"]

        # --- レイアウト設定 ---
        table_x = 20
        table_y = 55
        day_width = 380
        header_height = 45
        padding = 8
        cell_height = 88

        for i, date in enumerate(two_days):
            x = table_x + i * day_width
            current_y = table_y

            day_name = weekday_names[date.weekday()]
            date_str = f"{date.day}日({day_name})"
            label = "今日" if i == 0 else "明日"
            date_str_iso = date.strftime("%Y-%m-%d")

            header_rect = [(x, current_y), (x + day_width - 10, current_y + header_height)]
            draw.rectangle(header_rect, outline=0)
            draw.text((x + padding, current_y + padding), f"{label}: {date_str}", font=day_font, fill=0)
            current_y += header_height

            schedule_entry = None
            if current_month_data:
                schedule_entry = next((s for s in current_month_data.get("schedules", []) if s["date"] == date_str_iso), None)

            for member in members:
                # セルの枠を描画
                cell_rect = [(x, current_y), (x + day_width - 10, current_y + cell_height)]
                draw.rectangle(cell_rect, outline=0)

                # メンバー名を描画
                name_y = current_y + padding
                draw.text((x + padding, name_y), f"{member}:", font=name_font, fill=0)

                # スケジュールテキストの処理
                schedule_text = ""
                if schedule_entry and member in schedule_entry:
                    schedule_text = schedule_entry.get(member, "")

                if not schedule_text:
                    schedule_lines = ["予定なし"]
                else:
                    # 幅に基づいてテキストを折り返す
                    max_text_width = day_width - (padding * 5)
                    schedule_lines = wrap_text(schedule_text, schedule_font, max_text_width)

                content_y = name_y + 26
                line_height = 24
                # セル内に表示できる最大行数を計算
                max_lines = (cell_height - (name_y - current_y) - padding) // line_height -1

                visible_lines = schedule_lines
                # 行数があふれる場合は省略記号(...)をつける
                if len(schedule_lines) > max_lines:
                    visible_lines = schedule_lines[:max_lines]
                    if len(visible_lines) > 0:
                        visible_lines[-1] = visible_lines[-1] + "..."

                # テキストを描画
                for line in visible_lines:
                    draw.text((x + padding * 3, content_y), line, font=schedule_font, fill=0)
                    content_y += line_height

                current_y += cell_height

    except Exception as e:
        draw.text((20, 20), "カレンダーの表示に失敗しました", font=day_font, fill=0)
        draw.text((20, 60), f"エラー: {str(e)}", font=small_font, fill=0)

    return image

if __name__ == "__main__":
    image = create_calendar_slide()
    image.save("calendar_test.png")
    image.show()
