import { useState } from 'react';
import './App.css';

const API_URL = 'https://aai-apic.onrender.com';

export default function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hi! Ask me anything.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { sender: 'user', text: trimmed }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed })
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      const replyText = data.reply ?? data.response ?? data.message ?? JSON.stringify(data);

      setMessages((prev) => [...prev, { sender: 'bot', text: replyText }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: `Request failed: ${err.message}` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', padding: 16, fontFamily: 'sans-serif' }}>
      <h2>AAI Chatbot</h2>
      <div style={{ border: '1px solid #ccc', borderRadius: 8, padding: 12, minHeight: 260, marginBottom: 12 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 8, textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <strong>{msg.sender === 'user' ? 'You' : 'Bot'}:</strong> {msg.text}
          </div>
        ))}
        {loading && <div style={{ opacity: 0.7 }}>Bot is typing...</div>}
      </div>
      <form onSubmit={handleSend} style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          style={{ flex: 1, padding: 8 }}
          disabled={loading}
        />
        <button type="submit" style={{ padding: '8px 16px' }} disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}
