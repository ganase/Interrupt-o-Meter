# Interrupt-o-Meter App (Prototype)

Outlook 予定とカメラ静止画を使って「話しかけてOK度」をジョーク表示する FastAPI アプリです。

## この仕組みは PC ローカルで動く？
はい。**初期版は PC ローカル実行が前提**です（開発用サーバーをローカルで起動し、同一 PC のブラウザで利用）。

また、同一ネットワーク内からアクセスできるように起動すれば、スマートフォンをブラウザクライアントとして使うことも可能です。

---

## 動作環境条件（デバイス / OS / クラウドサービス）

### 1) デバイス
- **必須**: カメラ付きデバイス（PC 内蔵カメラ or 外付け USB カメラ）
- **推奨**: 開発実行は PC、閲覧のみならスマートフォンブラウザも可
- **注意**: カメラ利用にはブラウザ権限の許可が必要

### 2) OS
- **推奨**: Linux / macOS / Windows 11
- Python 仮想環境を作成できること
- ブラウザ（Chrome / Edge / Safari など）で `getUserMedia` が使えること

### 3) ランタイム / ミドルウェア
- **Python**: 3.11 以上（設計想定）
- 依存パッケージ: `requirements.txt` の内容
- **DB**: SQLite（ローカルファイル `data/app.db`）

### 4) 必要な外部クラウドサービス
- **Microsoft Graph (Outlook Calendar)**
  - Azure アプリ登録済みであること
  - `Calendars.ReadBasic` など必要スコープが設定済みであること
  - delegated auth（初期版は device code flow）を利用可能であること
- **OpenAI API**
  - 画像入力対応モデルを利用できる API キーがあること
  - ネットワークから `api.openai.com` へ到達できること

### 5) ネットワーク / セキュリティ条件
- 外部 API（Microsoft Graph / OpenAI）へ HTTPS 接続できること
- `.env` に API キー・クレデンシャルを設定し、Git 管理に含めないこと
- カメラ権限はブラウザ側で明示許可すること

### 6) クラウドデプロイ時の補足
このプロトタイプはローカル前提ですが、将来的に Render / Railway / Fly.io / Azure App Service へ移行可能な構成です。

ただし以下の追加対応が必要です。
- 本番向け ASGI 起動（gunicorn/uvicorn 設定）
- HTTPS 前提でのカメラアクセス設計
- 認証コールバック URL / CORS / シークレット管理
- SQLite の代替（必要なら PostgreSQL など）

---

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
