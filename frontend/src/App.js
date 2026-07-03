// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import './App.css';

function App() {
  const [records, setRecords] = useState([]);
  const [userName, setUserName] = useState('');
  const [investment, setInvestment] = useState('');
  const [machineName, setMachineName] = useState('');
  const [income, setIncome] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date());

  // バックエンドからこれまでのデータを取得する
  const fetchRecords = async () => {
    try {
      const res = await fetch('https://pachinko-app-r7jd.onrender.com/api/records');
      const data = await res.json();
      setRecords(data);
    } catch (err) {
      console.log("データ取得エラー:", err);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  // データを登録する
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userName || !investment || !income) return alert("すべて入力してください");

    const formattedDate = selectedDate.toISOString().split('T')[0];
    
    try {
      await fetch('https://pachinko-app-r7jd.onrender.com/api/records', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_name: userName,
          date: formattedDate,
          investment: parseInt(investment),
          income: parseInt(income)
          machine_name: machineName || "未記入"
        })
      });
      alert("記録しました！Discordを確認してください。");
      setInvestment('');
      setIncome('');
      setMachineName('');
      fetchRecords(); // データを再読み込み
    } catch (err) {
      alert("送信に失敗しました");
    }
  };

  // 【全体の総収支を計算】
  const totalBalance = records.reduce((sum, r) => sum + r.balance, 0);

  // 【★新機能：メンバーごとの通算収支を自動でグループ分けして計算】
  const userBalances = records.reduce((acc, r) => {
    if (!acc[r.user_name]) {
      acc[r.user_name] = 0;
    }
    acc[r.user_name] += r.balance;
    return acc;
  }, {});

  // カレンダーの日付マスに収支を表示するための関数
  const tileContent = ({ date, view }) => {
    if (view === 'month') {
      const dateString = date.toISOString().split('T')[0];
      const dayRecords = records.filter(r => r.date === dateString);
      if (dayRecords.length > 0) {
        const dayTotal = dayRecords.reduce((sum, r) => sum + r.balance, 0);
        const isPlus = dayTotal >= 0;
        return (
          <div style={{ color: isPlus ? 'blue' : 'red', fontSize: '10px', fontWeight: 'bold' }}>
            {isPlus ? `+${dayTotal}` : dayTotal}
          </div>
        );
      }
    }
    return null;
  };

  return (
    <div style={{ padding: '20px', maxWidth: '500px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>パチンコ収支管理</h2>
      
      {/* 収支表示エリア */}
      <div style={{ background: '#f0f0f0', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
        <h3 style={{ margin: '0 0 10px 0' }}>🏆 全体の通算総収支: <span style={{ color: totalBalance >= 0 ? 'blue' : 'red' }}>{totalBalance.toLocaleString()} 円</span></h3>
        
        <hr style={{ border: '0', borderTop: '1px solid #ccc', margin: '15px 0' }} />
        
        {/* ★新機能：個人別の収支一覧をここに表示 */}
        <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>👤 メンバーごとの通算収支:</h4>
        {Object.keys(userBalances).length === 0 ? (
          <p style={{ fontSize: '14px', color: '#666', margin: 0 }}>まだデータがありません</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {Object.entries(userBalances).map(([name, balance]) => (
              <li key={name} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px dashed #eee' }}>
                <span><strong>{name}</strong> さん</span>
                <span style={{ color: balance >= 0 ? 'blue' : 'red', fontWeight: 'bold' }}>
                  {balance >= 0 ? `+${balance.toLocaleString()}` : balance.toLocaleString()} 円
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <form onSubmit={handleSubmit} style={{ marginBottom: '30px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <h3>【収支を入力】</h3>
        <label>メンバー名:
          <input type="text" value={userName} onChange={(e) => setUserName(e.target.value)} style={{ width: '100%', padding: '8px' }} placeholder="例: たろう" />
        </label>
        <label>打った台（任意）:
          <input type="text" value={machineName} onChange={(e) => setMachineName(e.target.value)} style={{ width: '100%', padding: '8px' }} placeholder="例: エヴァ15" />
        </label>
        <label>投資 (円):
          <input type="number" value={investment} onChange={(e) => setInvestment(e.target.value)} style={{ width: '100%', padding: '8px' }} />
        </label>
        <label>回収 (円):
          <input type="number" value={income} onChange={(e) => setIncome(e.target.value)} style={{ width: '100%', padding: '8px' }} />
        </label>
        <button type="submit" style={{ padding: '10px', background: '#007bff', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>収支を記録してDiscordに通知</button>
      </form>

      <h3>【収支カレンダー】</h3>
      <p style={{ fontSize: '12px', color: '#666' }}>※日付を選択してから上のフォームで入力してください</p>
      <Calendar 
        onChange={setSelectedDate} 
        value={selectedDate} 
        tileContent={tileContent}
      />
    </div>
  );
}

export default App;