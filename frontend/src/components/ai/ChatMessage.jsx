import React from 'react';

const ChatMessage = ({ message, formatTime }) => {
  const isUser = message.role === 'user';
  const normalizeAssistantText = (text) => {
    if (typeof text !== 'string') return text;

    return text
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/`([^`]+)`/g, '$1')
      .replace(/^#{1,6}\s*/gm, '')
      .replace(/\[(.*?)\]\((.*?)\)/g, '$1');
  };
  const displayText = isUser ? message.text : normalizeAssistantText(message.text);
  
  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-content">
        <p className="message-text">{displayText}</p>
        <span className="message-time">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
};

export default ChatMessage;
