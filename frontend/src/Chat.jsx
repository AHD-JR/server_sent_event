import React, { useState } from 'react';
import './Chat.css';

const Chat = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResponse('');
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ prompt }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.error);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setResponse((prev) => prev + chunk);
      }
    } catch (error) {
      setError('An error occurred. Please try again later.');
      console.error('Request failed:', error);
    }
  };

  return (
    <div className="chat-container">
      <h1 className="chat-title">My SSE App</h1>
      <div className="chat-box">
        <div className="message-container">
          {error ? (
            <div className="error-message">{error}</div>
          ) : (
            <>
              <div className="user-message">{prompt && `You: ${prompt}`}</div>
              <div className="gpt-message">{response && `ChatGPT: ${response}`}</div>
            </>
          )}
        </div>
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type your message..."
            className="input-field"
            required
          />
          <button type="submit" className="send-button">Send</button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
