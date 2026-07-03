# 🎰 パチンコ・スロット収支管理アプリ (共有版)

複数人のメンバーで日々の収支を記録・共有し、Discordへリアルタイムで通知を送ることができるフルスタックWebアプリケーションです。

## 🌟 主な機能
- **収支の記録機能:** カレンダーから日付を選択し、投資額と回収額を記録。
- **自動集計＆可視化:**
  - アプリ全体の「通算総収支」を自動計算。
  - メンバーごとの「通算収支」を一覧表示。
  - カレンダー上に日々のプラスマイナスを表示。
- **Discordリアルタイム通知:** 記録した瞬間に、本日の収支、今月の収支、通算収支をDiscordの指定チャンネルに自動送信。
- **データの永続化:** クラウドデータベースを利用し、データを安全に長期保存。

## 🛠️ 使用技術 (Tech Stack)
- **Frontend:** React.js
- **Backend:** Python, FastAPI
- **Database:** Supabase (PostgreSQL)
- **Infrastructure / Hosting:**
  - Frontend: Vercel
  - Backend: Render

## 🏗️ システム構成 (Architecture)
1. **ユーザー**がVercel上のReactアプリ（ブラウザ/スマホ）から収支を入力。
2. データがRender上のFastAPI（Python）サーバーに送信される。
3. FastAPIが**Supabase**（データベース）へアクセスし、データの保存とこれまでの全履歴の取得を行う。
4. FastAPIが通算収支や月間収支を計算し、**Discord Webhook**を経由してグループへ通知を送信。

## 🚀 ローカル環境での動かし方 (Local Development)

このプロジェクトを自分のPCで動かすための手順です。

### 1. リポジトリのクローン
```bash
git clone [https://github.com/あなたのユーザー名/pachinko-app.git](https://github.com/あなたのユーザー名/pachinko-app.git)
cd pachinko-app

2. バックエンド (Python) の起動
必要なライブラリをインストールします。

Bash
pip install -r requirements.txt
main.py 内の以下の環境変数をご自身の情報に書き換えてください。

SUPABASE_URL:https://qerfyxzrxporqkquwzxg.supabase.co

SUPABASE_KEY:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFlcmZ5eHpyeHBvcnFrcXV3enhnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkwOTM5OTYsImV4cCI6MjA5NDY2OTk5Nn0.YHSJKbn7TawyUTTExbnvlIoD7cLiC5cpLeBK279p39c

DISCORD_WEBHOOK_URL: https://discord.com/api/webhooks/1506587620648550450/hAMU60DiWAEuc-8rGuSmVwrkDt7yi9hl9HEm0ALGbRBZ02IvxxElkdgrmfHAG7hdxKqz

サーバーを起動します。

Bash
python -m uvicorn main:app --reload
（デフォルトでは http://127.0.0.1:8000 で立ち上がります）

3. フロントエンド (React) の起動
バックエンドとは別の新しいターミナルを開き、以下のコマンドを実行します。

Bash
cd frontend
npm install
npm start
自動的にブラウザが開き、http://localhost:3000 でアプリが起動します。
