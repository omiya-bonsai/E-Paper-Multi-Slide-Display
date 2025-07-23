from waveshare_epd import epd4in26
from PIL import Image  # PILのImageモジュールを直接インポート

def init_display():
    """e-Paperディスプレイを初期化"""
    epd = epd4in26.EPD()
    epd.init()
    return epd

def full_refresh_cycle(epd):
    """完全なリフレッシュサイクル（黒→白→表示）を実行"""
    # ディスプレイを黒で塗りつぶし
    black_image = Image.new('1', (epd.width, epd.height), 0)  # PILのImageを使用
    epd.display(epd.getbuffer(black_image))
    
    # ディスプレイを白で塗りつぶし
    white_image = Image.new('1', (epd.width, epd.height), 255)  # PILのImageを使用
    epd.display(epd.getbuffer(white_image))

def display_image(epd, image):
    """画像をe-Paperディスプレイに表示"""
    # 完全なリフレッシュサイクルを実行
    full_refresh_cycle(epd)
    
    # その後に画像を表示
    epd.display(epd.getbuffer(image))

def sleep_display(epd):
    """ディスプレイをスリープモードに"""
    epd.sleep()
