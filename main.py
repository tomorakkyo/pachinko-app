# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import requests
from supabase import create_client, Client

app = FastAPI()

# フロントエンドからの通信を許可する設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ 【重要】ここをご自身の情報に必ず書き換えてください！
SUPABASE_URL = "https://qerfyxzrxporqkquwzxg.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_publishable_L5N9XZG9tO8pjlLyGQ5-rQ_YnLWoHAa"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1505877167169343609/_dgQPU0jnYG5s3PRq1z6eLgNXOqOzwMlafqKoeb0S-PzNtZ8UE_d6V0nZ4LBM_lsMUQm"

# Supabase金庫と接続する設定
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Record(BaseModel):
    user_name: str
    date: date
    investment: int
    income: int

# Discord通知用の関数
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
    balance = record.income - record.investment
    
    # Supabaseに保存する形にデータを整える
    new_data = {
        "user_name": record.user_name,
        "date": record.date.isoformat(),
        "investment": record.investment,
        "income": record.income,
        "balance": balance
    }
    
    # 【変更】データをSupabase金庫に直接保存（インサート）する
    supabase.table("records").insert(new_data).execute()
    
    # 【変更】最新の集計をするために、Supabase金庫からすべてのデータを一度取り出す
    response = supabase.table("records").select("*").execute()
    all_records = response.data
    
    # このユーザーの全記録だけを絞り込んで計算
    user_records = [r for r in all_records if r["user_name"] == record.user_name]
    total_balance = sum(r["balance"] for r in user_records)
    
    # このユーザーの今月の記録だけを絞り込んで計算
    target_month_prefix = f"{record.date.year}-{record.date.month:02d}"
    monthly_records = [r for r in user_records if r["date"].startswith(target_month_prefix)]
    monthly_balance = sum(r["balance"] for r in monthly_records)
    
    # Discordへ通知
    send_to_discord(record.user_name, record.investment, record.income, balance, monthly_balance, total_balance, record.date)
    
    return new_data

@app.get("/api/records")
def get_records():
    # 【変更】画面を開いたときは、Supabase金庫から全データを持ってきてフロントに渡す
    response = supabase.table("records").select("*").execute()
    return response.data