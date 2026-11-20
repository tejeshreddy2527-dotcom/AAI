import { useState } from 'react';
import './App.css';

export default function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hi! Ask me anything.' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMsg = { sender: 'user', text: trimmed };
    const botReply = {
      sender: 'bot',
      text: `You said: "${trimmed}". Connect your backend or AI API here!`
    };

    setMessages((prev) => [...prev, userMsg, botReply]);
    setInput('');
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
      </div>
      <form onSubmit={handleSend} style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          style={{ flex: 1, padding: 8 }}
        />
        <button type="submit" style={{ padding: '8px 16px' }}>Send</button>
      </form>
    </div>
  );
}
