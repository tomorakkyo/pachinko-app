# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import requests

app = FastAPI()

# フロントエンドからの通信を許可する設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ DiscordのWebhook URLをここに必ず貼り付けてください
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1505829735706525776/4O_ergSWnOHL6UyDwCXI25cQd3u21L-tY1721beN-uirxXG9ABBjJX-74abcGSJULzMy"

class Record(BaseModel):
    user_name: str
    date: date
    investment: int
    income: int

db_records = []

# 通知用の関数（今月の収支と通算収支を受け取れるように機能追加）
def send_to_discord(user_name, investment, income, balance, monthly_balance, total_balance, record_date):
    icon = "📈" if balance >= 0 else "📉"
    monthly_icon = "🔵" if monthly_balance >= 0 else "🔴"
    total_icon = "🏆" if total_balance >= 0 else "💀"
    
    content = (
        f"📢 **{user_name}** さんが収支を記録しました！\n"
        f"📅 日付: {record_date.strftime('%Y/%m/%d')}\n"
        f"💸 投資: {investment:,}円\n"
        f"💰 回収: {income:,}円\n"
        f"{icon} **本日の収支: {balance:,}円**\n"
        f"---\n"
        f"{monthly_icon} **今月({record_date.month}月)の収支: {monthly_balance:,}円**\n"
        f"{total_icon} **通算収支: {total_balance:,}円**"
    )
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
    except Exception as e:
        print(f"Discord通知エラー: {e}")

@app.post("/api/records")
def create_record(record: Record):
    # 1日の収支計算
    balance = record.income - record.investment
    new_data = {
        "id": len(db_records) + 1,
        "user_name": record.user_name,
        "date": record.date.isoformat(),
        "investment": record.investment,
        "income": record.income,
        "balance": balance
    }
    # データベース(配列)に保存
    db_records.append(new_data)
    
    # --- ここから追加：個人の集計を計算する ---
    
    # 1. このユーザーの全記録だけを取り出す
    user_records = [r for r in db_records if r["user_name"] == record.user_name]
    
    # 2. このユーザーの通算収支を計算
    total_balance = sum(r["balance"] for r in user_records)
    
    # 3. このユーザーの今月の記録だけをさらに取り出して計算
    target_month_prefix = f"{record.date.year}-{record.date.month:02d}" # 例: "2026-05"
    monthly_records = [r for r in user_records if r["date"].startswith(target_month_prefix)]
    monthly_balance = sum(r["balance"] for r in monthly_records)
    
    # Discordへ通知（計算した結果も渡す）
    send_to_discord(record.user_name, record.investment, record.income, balance, monthly_balance, total_balance, record.date)
    
    return new_data

@app.get("/api/records")
def get_records():
    return db_records