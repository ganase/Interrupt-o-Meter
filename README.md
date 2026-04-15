# Interrupt-o-Meter

デバイスのカメラ、画像、動画を読み込み、AI に「今この人に話しかけて大丈夫そうか」をジョーク判定させる FastAPI アプリです。

## Features

- ブラウザのカメラ入力
- 画像ファイルの読み込み
- 動画ファイルの読み込みとフレーム指定
- OpenAI Responses API による LLM 画像判定
- 赤・黄・青の信号表示
- 8 秒ごとの実況モード

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

`.env` に `OPENAI_API_KEY` を設定してください。

## Run

```bash
uvicorn app.main:app --reload
```

ブラウザで `http://127.0.0.1:8000` を開きます。

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_MODEL`: 既定は `gpt-5.4-mini`
- `OPENAI_TIMEOUT_SEC`: API タイムアウト秒数
- `FRAME_INTERVAL_SEC`: 実況モードの参考値
- `IMAGE_MAX_WIDTH`: クライアントで切り出す画像の最大辺
- `IMAGE_JPEG_QUALITY`: クライアントで送る JPEG 品質

## API

- `GET /api/health`: ヘルスチェック
- `POST /api/score`: 画像データ URL を受け取り、赤黄青の信号つきスコアを返す
- `POST /api/analyze/frame`: 既存互換の画像分析 API

## Notes

- 動画そのものを API に送るのではなく、現在フレームを切り出して画像として判定します。
- 判定は visible cues ベースの軽いジョーク用途です。重要な判断には使わないでください。
