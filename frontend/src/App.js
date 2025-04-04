import React from 'react';
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">医疗知识问答系统</h1>
            <p className="mt-2 text-sm text-gray-600">基于知识图谱的智能医疗问答</p>
          </div>
          <ChatInterface />
        </div>
      </div>
    </div>
  );
}

export default App; 