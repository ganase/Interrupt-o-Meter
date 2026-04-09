# Interrupt-o-Meter App (Prototype)

Outlook 予定とカメラ静止画を使って「話しかけてOK度」をジョーク表示する FastAPI アプリです。

## 機能
- `GET /api/health`: ヘルスチェック
- `POST /api/calendar/fetch`: Microsoft Graph から期間指定で予定取得して SQLite 保存
- `GET /api/calendar/events`: 保存済み予定を取得
- `GET /api/calendar/events.csv`: 保存済み予定を CSV 出力
- `POST /api/analyze/frame`: 画像 + 予定から `talk_ok_score` を算出
- ブラウザ UI（`/`）でカメラ表示と定期解析

## セットアップ
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` を設定してください（OpenAI / Graph）。未設定時は画像判定を中立値 fallback で処理します。

## 起動
```bash
uvicorn app.main:app --reload
```

ブラウザで `http://127.0.0.1:8000` を開いて利用します。

## テスト
```bash
pytest -q
```

## 注意
- 本アプリはジョーク用途です。判定の正確性を保証しません。
- 秘密情報は `.env` で管理し、GitHub へコミットしないでください。
- 画像の永続保存は初期版では無効です。
