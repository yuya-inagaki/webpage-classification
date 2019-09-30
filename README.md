
# Pictorial, Mixed, Textの分類
- Pictorial, Mixed, Textの分類をするためのプログラム
- `/input/webList-input.csv` に分類するサイトのURLデータを作成する
- `python main.py` で実行

## ログ
- 2019.09.09 Backgroundに指定した画像を無視した実装
- 2019.09.30 

## まとめ
- CSSで設定されている `background-image` はSelenium Webdriverで検出するのは難しい
- 一枚の背景画像でたくさんの領域をカバーしているものは特に難しい（例：Yahoo!のPCサイトのアイコン）