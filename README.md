# E-Paper Multi-Slide Display

![Built with Gemini](https://img.shields.io/badge/Built%20with-Gemini%202.5%20Pro-4285F4)

これは、Raspberry PiとWaveshare社製の4.26インチ電子ペーパーディスプレイを使用して、天気予報、カレンダー、学習リマインダーなどの情報を表示するためのPythonプロジェクトです。

![images](https://github.com/user-attachments/assets/50668af2-2974-4af2-a059-568ca791a538)

---

## ✨ 主な機能

* **マルチスライド表示:** 複数の情報画面を一定間隔で切り替えて表示します。
    * 天気予報（2地点まで設定可能）
    * 家族のスケジュールカレンダー
    * 日替わりの学習トピック
* **カスタマイズ可能なデザイン:**
    * 都市名の頭文字を大きく表示するドロップキャップ機能
* **設定ファイルによる簡単なカスタマイズ:**
    * `config.json`を編集するだけで、表示する天気予報の場所や、学習スライドの学年設定などを変更できます。
* **APIキャッシュ:** OpenWeatherMap APIへのアクセスを最小限に抑えるためのデータキャッシュ機能を搭載しています。

---

## ⚙️ 必要なもの

### ハードウェア
* Raspberry Pi (Pi Zero 2 Wで動作確認)
* [Waveshare 4.26inch e-paper HAT](https://www.waveshare.com/4.26inch-e-paper-hat.htm)

### ソフトウェア
* Python 3
* OpenWeatherMap APIキー

---

## 🚀 セットアップとインストール

1.  **リポジトリの準備:**
    このプロジェクトのファイルをダウンロードまたは`git clone`します。

2.  **Pythonライブラリのインストール:**
    プロジェクトに必要なライブラリをインストールします。まず、以下の内容で `requirements.txt` というファイルを作成してください。

    **`requirements.txt`:**
    ```
    Pillow
    requests
    python-dotenv
    cairosvg
    ```

    次に、ターミナルで以下のコマンドを実行します。
    ```sh
    pip install -r requirements.txt
    ```

3.  **設定ファイルの準備:**
    このプロジェクトは、3つの`.json.example`ファイルを基に、あなた専用の設定ファイルを作成します。

    * **APIキーの設定:** `.env.example` をコピーして `.env` を作成し、あなたのOpenWeatherMap APIキーを記述します。
    * **表示内容の設定:** `config.json.example` をコピーして `config.json` を作成し、天気予報を表示したい場所の緯度・経度などを設定します。
    * **カレンダーの予定:** `schedule.example.json` をコピーして `schedule.json` を作成し、あなたの予定を書き込みます。
    * **学習コンテンツ:** `learning_content.example.json` をコピーして `learning_content.json` を作成し、表示したい学習内容を記述します。

4.  **フォントの準備:**
    このプロジェクトは`fonts`ディレクトリ内のフォントを使用します。`slide_calendar.py`と`slide_learning.py`で使用されているフォント（例: `NotoSansCJK`, `ipag`）を`fonts`ディレクトリに配置してください。

---

## 実行方法

以下のコマンドでメインスクリプトを実行します。

```sh
python3 main.py
````

`Ctrl + C`でプログラムを終了できます。

-----

## 🙏 謝辞 (Acknowledgements)

このプロジェクトは、以下の素晴らしいプロジェクトやサービスを利用して作成されました。心より感謝申し上げます。

  * **アイコン (Icons):**

      * **ソース:** [weather-crow5.7](https://github.com/kotamorishi/weather-crow5.7) by kotamorishi
      * **ライセンス:** MIT License
      * *(メモ: 元のSVGファイルをPNG形式に変換して使用しています)*

  * **フォント (Fonts):**

      * **`Reggae One`:** (天気スライドで使用)
          * **ソース:** [Google Fonts](https://fonts.google.com/specimen/Reggae+One)
          * **ライセンス:** SIL Open Font License
      * **`Noto Sans CJK JP`:** (カレンダースライドで使用)
          * **ソース:** [Google Fonts](https://www.google.com/search?q=https://fonts.google.com/noto/specimen/Noto-Sans-JP)
          * **ライセンス:** SIL Open Font License

  * **天気データ (Weather Data):**

      * [OpenWeatherMap](https://openweathermap.org/)

  * **開発支援 (Development Assistance):**

      * このプロジェクトのコード生成、デバッグ、およびドキュメント作成の一部は、GoogleのGemini 2.5 Proを活用して行われました。

-----

## 📄 ライセンス (License)

このプロジェクトはMITライセンスの下で公開されています。詳細は`LICENSE`ファイルをご覧ください。
