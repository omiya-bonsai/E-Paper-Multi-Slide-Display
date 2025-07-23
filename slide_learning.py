import json
import datetime
import random
import os
from PIL import Image, ImageDraw, ImageFont

# --- ヘルパー関数 ---

def load_config():
    """設定ファイル(config.json)を読み込む"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('learning_slide', {})
    except Exception:
        return {} # エラーの場合は空の設定を返す

def get_available_font(font_list):
    """利用可能なフォントを探す"""
    for font_path in font_list:
        if os.path.exists(font_path):
            return font_path
    return None

def get_current_grade(entrance_year):
    """現在の学年を計算する"""
    now = datetime.datetime.now()
    current_school_year = now.year if now.month >= 4 else now.year - 1
    grade = current_school_year - entrance_year + 1
    return max(1, min(3, grade))

def load_learning_content(content_file):
    """JSONファイルから学習コンテンツを読み込む"""
    try:
        with open(content_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"学習コンテンツの読み込みエラー: {e}")
        return None

def get_daily_topic(config):
    """設定に基づいて、今日の学習トピックをランダムに一つ選ぶ"""
    content = load_learning_content(config.get('content_file', 'learning_content.json'))
    entrance_year = config.get('entrance_year', 2022) # デフォルト値
    grade = get_current_grade(entrance_year)
    grade_key = f"grade{grade}"

    if not content or grade_key not in content:
        return None, None

    weekday = datetime.datetime.now().weekday()
    subjects = list(content[grade_key].keys())

    # ★★★ 以下の3行を追加 ★★★
    # もし科目が一つも登録されていなければ、エラーを返して終了
    if not subjects:
        return "エラー", {"title": "学習コンテンツエラー", "body": f"{grade_key}に科目が登録されていません。"}

    subject_key = subjects[weekday % len(subjects)]
    topic = random.choice(content[grade_key][subject_key])

    subject_map = {"math": "数学", "science": "理科", "social": "社会", "english": "英語", "japanese": "国語"}
    return subject_map.get(subject_key, "学習"), topic

def wrap_text_by_width(text, font, max_width):
    """禁則処理を考慮して、テキストを描画幅に基づいて自動で折り返す"""
    kinsoku_start = "、。）」』】っゃゅょッャュョ,.!?ー～)"
    lines = []
    for original_line in text.split('\n'):
        current_line = ""
        for char in original_line:
            if font.getbbox(current_line + char)[2] <= max_width:
                current_line += char
            else:
                if char in kinsoku_start and len(current_line) > 0:
                    lines.append(current_line[:-1])
                    current_line = current_line[-1] + char
                else:
                    lines.append(current_line)
                    current_line = char
        lines.append(current_line)
    return lines

# --- メインの描画関数 ---

def create_learning_slide():
    """学習支援スライドを、洗練されたレイアウトで生成する"""
    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 480
    image = Image.new('1', (IMAGE_WIDTH, IMAGE_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    # --- 設定とコンテンツの読み込み ---
    config = load_config()
    subject, topic = get_daily_topic(config)

    # --- フォント定義（相対パス化） ---
    font_path_regular = os.path.join(os.path.dirname(__file__), 'fonts', 'ipag.ttf')
    font_path_bold = os.path.join(os.path.dirname(__file__), 'fonts', 'ipagp.ttf')
    
    font_regular = get_available_font([font_path_regular, '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'])
    font_bold = get_available_font([font_path_bold, '/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf'])
    
    if not font_regular or not font_bold:
        draw.text((10, 10), "Font file not found.", fill=0)
        return image
    
    font_header = ImageFont.truetype(font_regular, 28)
    font_title = ImageFont.truetype(font_bold, 40)
    font_body = ImageFont.truetype(font_regular, 32)

    # --- 描画処理 ---
    margin = 45
    current_y = 35

    if not topic:
        draw.text((margin, margin), "学習コンテンツが見つかりません。", font=font_title, fill=0)
        return image

    # ヘッダー（設定ファイルからテンプレートを読み込み）
    header_template = config.get('header_template', "今日の学習: {subject}")
    header_text = header_template.format(subject=subject)
    draw.text((margin, current_y), header_text, font=font_header, fill=0)
    current_y += 55

    # タイトル
    title = topic.get("title", "")
    title_lines = wrap_text_by_width(title, font_title, IMAGE_WIDTH - margin * 2)
    for line in title_lines:
        draw.text((margin, current_y), line, font=font_title, fill=0)
        current_y += 50
    current_y += 10

    # 区切り線
    draw.line((margin, current_y, IMAGE_WIDTH - margin, current_y), fill=0, width=2)
    current_y += 25

    # 本文
    body = topic.get("body", "")
    body_lines = wrap_text_by_width(body, font_body, IMAGE_WIDTH - margin * 2)
    line_spacing = 18
    for line in body_lines:
        draw.text((margin, current_y), line, font=font_body, fill=0)
        current_y += font_body.size + line_spacing
        if current_y > IMAGE_HEIGHT - margin:
            break

    return image

if __name__ == '__main__':
    # このスクリプト単体で実行した際のテスト用
    # config.jsonとlearning_content.jsonを先に作成してください
    learning_image = create_learning_slide()
    learning_image.show()
