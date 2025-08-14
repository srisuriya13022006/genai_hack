import React, { useState } from 'react';
import { Download, FileText, Settings, Zap, Brain, Target, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import './QuestionPaper.css';

const QuestionPaper = ({ uploadedFiles = [], difficulty = 'medium', onGenerate = () => {}, setDifficulty = () => {} }) => {
  const [paper, setPaper] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [questionCount, setQuestionCount] = useState({ mcq: 10, short: 5, long: 3 });
  const [timeLimit, setTimeLimit] = useState(120);

  const generatePaper = () => {
    setIsGenerating(true);
    
    // Simulate paper generation
    setTimeout(() => {
      const samplePaper = {
        title: `${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)} Level Question Paper`,
        subject: selectedTopics.length > 0 ? selectedTopics.join(', ') : 'General Studies',
        timeLimit: timeLimit,
        totalMarks: calculateTotalMarks(),
        generatedAt: new Date().toLocaleDateString(),
        sections: [
          {
            part: 'A',
            title: 'Multiple Choice Questions',
            instructions: 'Choose the correct answer from the given options.',
            questions: Array.from({ length: questionCount.mcq }, (_, i) => ({
              id: i + 1,
              question: `Sample MCQ ${i + 1} based on ${selectedTopics[0] || 'uploaded content'}?`,
              options: ['Option A', 'Option B', 'Option C', 'Option D'],
              marks: 1,
              difficulty: difficulty
            })),
            totalMarks: questionCount.mcq
          },
          {
            part: 'B',
            title: 'Short Answer Questions',
            instructions: 'Answer in 2-3 sentences.',
            questions: Array.from({ length: questionCount.short }, (_, i) => ({
              id: i + 1,
              question: `Short answer question ${i + 1} about ${selectedTopics[0] || 'document content'}.`,
              marks: 3,
              difficulty: difficulty
            })),
            totalMarks: questionCount.short * 3
          },
          {
            part: 'C',
            title: 'Long Answer Questions',
            instructions: 'Answer in detail with examples.',
            questions: Array.from({ length: questionCount.long }, (_, i) => ({
              id: i + 1,
              question: `Detailed question ${i + 1} requiring comprehensive analysis of ${selectedTopics[0] || 'uploaded material'}.`,
              marks: 10,
              difficulty: difficulty
            })),
            totalMarks: questionCount.long * 10
          }
        ]
      };
      setPaper(samplePaper);
      onGenerate(samplePaper);
      setIsGenerating(false);
    }, 3000);
  };

  const calculateTotalMarks = () => {
    return (questionCount.mcq * 1) + (questionCount.short * 3) + (questionCount.long * 10);
  };

  const downloadPDF = () => {
    // Simulate PDF download
    alert(`Downloading ${paper.title} as PDF...`);
    console.log('Downloading PDF for', difficulty);
  };

  const handleTopicToggle = (topic) => {
    setSelectedTopics(prev => 
      prev.includes(topic) 
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  const getDifficultyIcon = (level) => {
    switch(level) {
      case 'easy': return <Target className="difficulty-icon easy" />;
      case 'medium': return <Brain className="difficulty-icon medium" />;
      case 'hard': return <Zap className="difficulty-icon hard" />;
      default: return <Target className="difficulty-icon" />;
    }
  };

  const getDifficultyColor = (level) => {
    switch(level) {
      case 'easy': return '#48bb78';
      case 'medium': return '#ed8936';
      case 'hard': return '#e53e3e';
      default: return '#4299e1';
    }
  };

  // Extract topics from uploaded files
  const availableTopics = uploadedFiles.flatMap(file => file.topics || [file.name.split('.')[0]]);

  return (
    <div className="question-paper-container">
      <div className="main-content">
        {/* Header */}
        <div className="header-section">
          <h1 className="main-title">📝 Question Paper Generator</h1>
          <p className="main-subtitle">
            Create customized question papers from your uploaded documents with AI-powered content generation
          </p>
        </div>

        {/* Configuration Section */}
        <div className="config-section">
          <div className="config-header">
            <h2 className="section-title">
              <Settings className="section-icon" />
              Configuration Settings
            </h2>
          </div>

          <div className="config-grid">
            {/* Difficulty Selection */}
            <div className="config-card">
              <h3 className="config-title">
                {getDifficultyIcon(difficulty)}
                Difficulty Level
              </h3>
              <div className="difficulty-options">
                {['easy', 'medium', 'hard'].map((level) => (
                  <label key={level} className="difficulty-option">
                    <input
                      type="radio"
                      name="difficulty"
                      value={level}
                      checked={difficulty === level}
                      onChange={(e) => setDifficulty(e.target.value)}
                    />
                    <span className={`difficulty-label ${level}`}>
                      {getDifficultyIcon(level)}
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Question Count */}
            <div className="config-card">
              <h3 className="config-title">
                <FileText className="config-icon" />
                Question Distribution
              </h3>
              <div className="question-inputs">
                <div className="input-group">
                  <label>MCQ Questions (1 mark each)</label>
                  <input
                    type="number"
                    min="0"
                    max="50"
                    value={questionCount.mcq}
                    onChange={(e) => setQuestionCount(prev => ({ ...prev, mcq: parseInt(e.target.value) || 0 }))}
                    className="number-input"
                  />
                </div>
                <div className="input-group">
                  <label>Short Questions (3 marks each)</label>
                  <input
                    type="number"
                    min="0"
                    max="20"
                    value={questionCount.short}
                    onChange={(e) => setQuestionCount(prev => ({ ...prev, short: parseInt(e.target.value) || 0 }))}
                    className="number-input"
                  />
                </div>
                <div className="input-group">
                  <label>Long Questions (10 marks each)</label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={questionCount.long}
                    onChange={(e) => setQuestionCount(prev => ({ ...prev, long: parseInt(e.target.value) || 0 }))}
                    className="number-input"
                  />
                </div>
              </div>
              <div className="total-marks">
                Total Marks: <span className="marks-value">{calculateTotalMarks()}</span>
              </div>
            </div>

            {/* Time Limit */}
            <div className="config-card">
              <h3 className="config-title">
                <Clock className="config-icon" />
                Time Limit
              </h3>
              <div className="time-input-group">
                <input
                  type="range"
                  min="30"
                  max="300"
                  value={timeLimit}
                  onChange={(e) => setTimeLimit(parseInt(e.target.value))}
                  className="time-slider"
                />
                <div className="time-display">{timeLimit} minutes</div>
              </div>
            </div>
          </div>

          {/* Topics Selection */}
          {availableTopics.length > 0 && (
            <div className="topics-section">
              <h3 className="topics-title">Select Topics to Include</h3>
              <div className="topics-grid">
                {availableTopics.map((topic, index) => (
                  <label key={index} className="topic-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedTopics.includes(topic)}
                      onChange={() => handleTopicToggle(topic)}
                    />
                    <span className="topic-label">{topic}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Generate Button */}
          <div className="generate-section">
            {uploadedFiles.length === 0 ? (
              <div className="no-files-warning">
                <AlertCircle className="warning-icon" />
                <p>Please upload documents first to generate questions</p>
              </div>
            ) : (
              <button 
                onClick={generatePaper} 
                disabled={isGenerating}
                className="generate-btn"
              >
                {isGenerating ? (
                  <>
                    <div className="spinner-small"></div>
                    Generating Questions...
                  </>
                ) : (
                  <>
                    <Zap size={20} />
                    🚀 Generate Question Paper
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Generated Paper Display */}
        {paper && (
          <div className="paper-display-section">
            <div className="paper-header">
              <div className="paper-header-content">
                <h2 className="paper-title">
                  <CheckCircle className="success-icon" />
                  {paper.title}
                </h2>
                <div className="paper-meta">
                  <div className="meta-item">
                    <strong>Subject:</strong> {paper.subject}
                  </div>
                  <div className="meta-item">
                    <strong>Time:</strong> {paper.timeLimit} minutes
                  </div>
                  <div className="meta-item">
                    <strong>Total Marks:</strong> {paper.totalMarks}
                  </div>
                  <div className="meta-item">
                    <strong>Generated:</strong> {paper.generatedAt}
                  </div>
                </div>
              </div>
              <button onClick={downloadPDF} className="download-btn">
                <Download size={18} />
                Download PDF
              </button>
            </div>

            {/* Paper Content */}
            <div className="paper-content">
              {paper.sections.map((section, index) => (
                <div key={index} className="paper-section">
                  <div className="section-header">
                    <h3 className="section-title">
                      Part {section.part}: {section.title}
                    </h3>
                    <div className="section-info">
                      <span className="section-marks">{section.totalMarks} marks</span>
                      <span 
                        className="section-difficulty"
                        style={{ color: getDifficultyColor(section.difficulty) }}
                      >
                        {getDifficultyIcon(section.difficulty)}
                        {section.difficulty}
                      </span>
                    </div>
                  </div>
                  
                  <p className="section-instructions">{section.instructions}</p>
                  
                  <div className="questions-list">
                    {section.questions.map((question, qIndex) => (
                      <div key={qIndex} className="question-item">
                        <div className="question-number">
                          Q{qIndex + 1}.
                        </div>
                        <div className="question-content">
                          <p className="question-text">{question.question}</p>
                          {question.options && (
                            <div className="question-options">
                              {question.options.map((option, oIndex) => (
                                <div key={oIndex} className="option-item">
                                  {String.fromCharCode(97 + oIndex)}) {option}
                                </div>
                              ))}
                            </div>
                          )}
                          <div className="question-marks">({question.marks} mark{question.marks !== 1 ? 's' : ''})</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Paper Footer */}
            <div className="paper-footer">
              <div className="footer-info">
                <p>📋 Paper generated from {uploadedFiles.length} uploaded document{uploadedFiles.length !== 1 ? 's' : ''}</p>
                <p>🤖 Powered by AI content analysis</p>
              </div>
              <div className="footer-actions">
                <button onClick={() => setPaper(null)} className="btn-secondary">
                  Generate New Paper
                </button>
                <button onClick={downloadPDF} className="download-btn-large">
                  <Download size={20} />
                  Download PDF
                </button>
              </div>
            </div>
          </div>
        )}

        {/* No Files State */}
        {uploadedFiles.length === 0 && !paper && (
          <div className="empty-state">
            <div className="empty-state-content">
              <div className="empty-animation">📄</div>
              <h3 className="empty-title">No documents available</h3>
              <p className="empty-subtitle">
                Upload some documents first to generate intelligent question papers
              </p>
              <div className="empty-features">
                <div className="feature-item">🎯 Customizable difficulty levels</div>
                <div className="feature-item">⚡ AI-powered question generation</div>
                <div className="feature-item">📊 Multiple question formats</div>
                <div className="feature-item">📱 PDF export ready</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionPaper;