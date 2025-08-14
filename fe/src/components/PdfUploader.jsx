import React, { useState, useEffect } from 'react';
import { Upload, X, Send, Plus, FileText, MessageCircle, Bot, User, Sparkles, Zap, Brain } from 'lucide-react';
import './PdfUploader.css'; // New CSS file

// Loader
const Loader = () => (
  <div className="loader-container">
    <div className="loader-spinner"></div>
  </div>
);

// PDF Viewer
const PDFViewer = ({ fileUrl }) => (
  <div className="pdf-viewer">
    <div className="pdf-viewer-text">
      <FileText size={48} className="pdf-icon" />
      <span>PDF Preview</span>
    </div>
  </div>
);

const PdfUploader = ({ onFileUpload = () => {}, uploadedFiles = [], onTopicDetected = () => {} }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [error, setError] = useState(null);
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const [demoFiles] = useState([
    { name: "Machine Learning Basics.pdf", type: "application/pdf", topics: ["Machine Learning"], url: "#" },
    { name: "Data Science Guide.docx", type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", topics: ["Data Science"], url: "#" }
  ]);

  const currentFiles = uploadedFiles.length > 0 ? uploadedFiles : demoFiles;

  useEffect(() => {
    if (selectedFile) {
      const reader = new FileReader();
      reader.onload = (e) => setPreviewUrl(e.target.result);
      reader.readAsDataURL(selectedFile);
    }
  }, [selectedFile]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
      ];
      if (!validTypes.includes(file.type)) {
        setError('Please upload a PDF, DOCX, or TXT file.');
        setSelectedFile(null);
        return;
      }
      setError(null);
      setSelectedFile(file);
      setIsLoading(true);

      setTimeout(() => {
        const fileData = {
          name: file.name,
          type: file.type,
          url: URL.createObjectURL(file),
          topics: [file.name.split('.')[0]]
        };
        onFileUpload(fileData);
        onTopicDetected(fileData.topics[0]);
        setIsLoading(false);
        setSelectedFile(null);
        setPreviewUrl(null);
      }, 2000);
    }
  };

  const handleSend = () => {
    if (input.trim()) {
      const newMessage = { type: 'user', text: input, timestamp: Date.now() };
      setMessages(prev => [...prev, newMessage]);
      setInput('');
      setIsTyping(true);

      setTimeout(() => {
        const responses = [
          "Based on your Machine Learning and Data Science documents, I can see you're exploring foundational concepts. Would you like me to summarize the key algorithms discussed?",
          "I've analyzed your documents and found interesting connections between supervised learning techniques and data preprocessing methods. What specific area would you like to dive deeper into?",
          "Your documents cover essential topics in ML and Data Science. I can help explain concepts like neural networks, decision trees, or statistical analysis. What interests you most?",
          "Great question! From your uploaded materials, I can provide insights on data visualization, model evaluation, or feature engineering. Which topic would be most helpful?"
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        setIsTyping(false);
        setMessages(prev => [...prev, { type: 'ai', text: randomResponse, timestamp: Date.now() }]);
      }, 1500);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
  };

  const getFileIcon = (fileType) => {
    if (fileType.includes('pdf')) return '📄';
    if (fileType.includes('word')) return '📝';
    if (fileType.includes('text')) return '📋';
    return '📁';
  };

  const suggestions = [
    "What are the main topics in my documents?",
    "Can you summarize the key points?",
    "Explain machine learning concepts",
    "Compare different algorithms discussed"
  ];

  return (
    <div className="page-container">
      <div className="content-wrapper">
        
        {/* Header */}
        <div className="header-section">
          <h1 className="header-title">
            <Brain className="header-icon" size={40} />
            Document Intelligence Hub
          </h1>
          <p className="header-subtitle">
            Upload your documents and engage in intelligent conversations powered by AI analysis
          </p>
        </div>

        {/* Upload Section */}
        <div className="upload-section">
          <div className="upload-inner">
            <div className={`upload-box ${isLoading ? 'upload-loading' : ''}`}>
              {isLoading ? (
                <>
                  <Loader />
                  <p className="loading-text">Processing your document...</p>
                </>
              ) : (
                <>
                  <div className="upload-icon-wrapper">
                    <Upload size={48} className="upload-icon" />
                  </div>
                  <h3 className="upload-title">Drop your files here</h3>
                  <p className="upload-subtitle">or click to browse from your device</p>
                  <button className="choose-files-btn">
                    <Upload size={16} className="btn-icon" />
                    Choose Files
                  </button>
                  <p className="upload-hint">
                    Supports PDF, DOCX, and TXT • Max size: 10MB
                  </p>
                </>
              )}
            </div>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
              className="file-input"
            />
          </div>
        </div>

        {/* Files Section */}
        <div className="files-section">
          <div className="files-header">
            <h2 className="files-title">
              <FileText className="files-title-icon" />
              Your Documents ({currentFiles.length})
            </h2>
            <button className="add-more-btn">
              <Plus size={16} />
              Add More
            </button>
          </div>

          <div className="files-list">
            {currentFiles.map((file, index) => (
              <div key={index} className="file-card">
                <div className="file-info">
                  <div className="file-icon">{getFileIcon(file.type)}</div>
                  <div>
                    <h3 className="file-name">{file.name}</h3>
                    <p className="file-meta">
                      {file.type.includes('pdf') ? 'PDF' : file.type.includes('word') ? 'DOCX' : 'TXT'} • 
                      Topic: <span className="file-topic">{file.topics[0]}</span>
                    </p>
                  </div>
                </div>
                <div className="file-actions">
                  <button onClick={() => setShowChat(true)} className="chat-btn">
                    <MessageCircle size={16} />
                  </button>
                  <button className="delete-btn">
                    <X size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="start-analysis-wrapper">
            <button onClick={() => setShowChat(true)} className="start-analysis-btn">
              <Sparkles size={24} />
              Start AI-Powered Analysis
              <Zap size={20} />
            </button>
            <p className="start-analysis-hint">
              Unlock intelligent insights from your documents
            </p>
          </div>
        </div>

        {/* Chat Modal */}
        {showChat && (
          <div className="chat-overlay">
            <div className="chat-modal">
              
              {/* Chat Header */}
              <div className="chat-header">
                <div className="chat-header-overlay"></div>
                <div className="chat-header-content">
                  <div className="chat-header-left">
                    <div className="chat-header-icon-wrapper">
                      <Brain size={24} className="chat-header-icon" />
                    </div>
                    <div>
                      <h3 className="chat-header-title">AI Document Assistant</h3>
                      <p className="chat-header-subtitle">
                        Analyzing {currentFiles.length} document{currentFiles.length !== 1 ? 's' : ''} • Ready to help
                      </p>
                    </div>
                  </div>
                  <button onClick={() => setShowChat(false)} className="chat-close-btn">
                    <X size={20} />
                  </button>
                </div>
              </div>

              {/* Chat Body */}
              <div className="chat-body">
                {messages.length === 0 ? (
                  <div className="chat-empty-state">
                    <div className="chat-empty-icon">
                      <Brain size={32} className="chat-empty-brain" />
                    </div>
                    <h4 className="chat-empty-title">Ready to explore your documents!</h4>
                    <p className="chat-empty-subtitle">
                      I've analyzed your files and I'm ready to provide insights, summaries, and answer your questions.
                    </p>
                    
                    <div className="chat-suggestions">
                      {suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="chat-suggestion-btn"
                        >
                          <div className="chat-suggestion-content">
                            <div className="chat-suggestion-icon">
                              <Sparkles size={14} className="suggestion-sparkle" />
                            </div>
                            <span className="chat-suggestion-text">{suggestion}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="chat-messages">
                    {messages.map((msg, index) => (
                      <div key={index} className={`chat-message ${msg.type === 'user' ? 'user-message' : 'ai-message'}`}>
                        <div className={`chat-avatar ${msg.type === 'user' ? 'user-avatar' : 'ai-avatar'}`}>
                          {msg.type === 'user' ? <User size={16} /> : <Bot size={16} />}
                        </div>
                        <div className={`chat-bubble ${msg.type === 'user' ? 'user-bubble' : 'ai-bubble'}`}>
                          <p className="chat-text">{msg.text}</p>
                          <div className="chat-timestamp">
                            {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    {isTyping && (
                      <div className="chat-message ai-message">
                        <div className="chat-avatar ai-avatar">
                          <Bot size={16} />
                        </div>
                        <div className="chat-bubble ai-bubble typing-bubble">
                          <div className="typing-dots">
                            <div className="dot"></div>
                            <div className="dot delay1"></div>
                            <div className="dot delay2"></div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div className="chat-input-container">
                <div className="chat-input-wrapper">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything about your documents..."
                    className="chat-textarea"
                    rows={1}
                  />
                  <button
                    onClick={handleSend}
                    disabled={!input.trim()}
                    className="send-btn"
                  >
                    <Send size={18} />
                  </button>
                </div>
                <p className="chat-input-hint">Press Enter to send • Shift+Enter for new line</p>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default PdfUploader;
