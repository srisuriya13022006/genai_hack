import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, X, Upload, HelpCircle, FileText, BookOpen, ArrowLeft } from 'lucide-react';
import Navbar from './components/Navbar.jsx';
import PdfUploader from './components/PdfUploader.jsx';
import Quiz from './components/Quiz.jsx';
import QuestionPaper from './components/QuestionPaper.jsx';
import Resources from './components/Resources.jsx';
import AnimationWrapper from './components/AnimationWrapper.jsx';
import './global.css';



const QuizSuggestionModal = ({ topic, onAccept, onReject, isOpen }) => {
/*************  ✨ Windsurf Command ⭐  *************/
/**
 * A modal component that suggests a quiz based on the detected topic.
 * 
 * @param {Object} props - The props for the component.
 * @param {string} props.topic - The detected topic to suggest a quiz for.
 * @param {function} props.onAccept - Callback function to execute when the user accepts the quiz suggestion.
 * @param {function} props.onReject - Callback function to execute when the user rejects the quiz suggestion.
 * @param {boolean} props.isOpen - Flag indicating if the modal is open or not.
 * 
 * @returns {JSX.Element|null} The modal component if isOpen is true, otherwise null.
 */

/*******  ca78e915-0762-42b3-868c-e6fcaa1f1e8b  *******/  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 2000,
        }}
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          style={{
            background: 'white',
            borderRadius: '20px',
            padding: '30px',
            maxWidth: '400px',
            margin: '20px',
            textAlign: 'center',
          }}
        >
          <HelpCircle size={48} style={{ color: '#667eea', marginBottom: '20px' }} />
          <h3 style={{ marginBottom: '15px' }}>Topic Detected: {topic}</h3>
          <p style={{ marginBottom: '25px', color: '#666' }}>
            Want to try a quiz?
          </p>
          <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
            <motion.button
              className="btn"
              onClick={onAccept}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Yes
            </motion.button>
            <motion.button
              className="btn btn-secondary"
              onClick={onReject}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              No
            </motion.button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

const Toast = ({ show, message, type, onClose }) => {
  if (!show) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 100 }}
      style={{
        position: 'fixed',
        top: '100px',
        right: '20px',
        background: type === 'success' ? 'rgba(34, 197, 94, 0.95)' : 'rgba(239, 68, 68, 0.95)',
        color: 'white',
        padding: '15px 20px',
        borderRadius: '10px',
        backdropFilter: 'blur(10px)',
        zIndex: 1001,
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        maxWidth: '300px'
      }}
    >
      <CheckCircle size={20} />
      {message}
      <X 
        size={16} 
        onClick={onClose}
        style={{ cursor: 'pointer' }}
      />
    </motion.div>
  );
};

const HomePage = ({ uploadedFiles, handleFileUpload, handleTopicDetected }) => {
  return (
    <div className="container">
      <div className="card">
        <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>Upload Your Study Material</h1>
        <PdfUploader 
          onFileUpload={handleFileUpload}
          uploadedFiles={uploadedFiles}
          onTopicDetected={handleTopicDetected}
        />
      </div>
    </div>
  );
};

const QuizPage = ({ uploadedFiles, detectedTopic, handleQuizComplete }) => {
  const navigate = useNavigate();
  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '30px' }}>
          <motion.button
            onClick={() => navigate('/')}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              color: '#667eea',
              fontSize: '14px'
            }}
            whileHover={{ scale: 1.05 }}
          >
            <ArrowLeft size={20} />
            Back
          </motion.button>
          <h1>Quiz: {detectedTopic || (uploadedFiles.length > 0 ? uploadedFiles[0].topics[0] : 'General Knowledge')}</h1>
        </div>
        
        {uploadedFiles.length > 0 ? (
          <Quiz 
            topic={detectedTopic || uploadedFiles[0].topics[0]}
            onComplete={handleQuizComplete}
          />
        ) : (
          <div style={{ textAlign: 'center' }}>
            <HelpCircle size={64} style={{ color: '#667eea', marginBottom: '20px' }} />
            <h3>No Content Available</h3>
            <p style={{ marginBottom: '20px' }}>Please upload a file first to take a quiz.</p>
            <motion.button
              className="btn"
              onClick={() => navigate('/')}
              whileHover={{ scale: 1.05 }}
            >
              <Upload size={20} />
              Upload File
            </motion.button>
          </div>
        )}
      </div>
    </div>
  );
};

const QuestionPaperPage = ({ uploadedFiles, handleQuestionPaperGenerate }) => {
  const navigate = useNavigate();
  const [difficulty, setDifficulty] = useState('medium');
  const generatePaper = () => {
    if (uploadedFiles.length > 0) {
      handleQuestionPaperGenerate({ difficulty, files: uploadedFiles });
    }
  };

  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '30px' }}>
          <motion.button
            onClick={() => navigate('/')}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              color: '#667eea',
              fontSize: '14px'
            }}
            whileHover={{ scale: 1.05 }}
          >
            <ArrowLeft size={20} />
            Back
          </motion.button>
          <h1>Question Paper Generator</h1>
        </div>
        
        {uploadedFiles.length > 0 ? (
          <QuestionPaper 
            uploadedFiles={uploadedFiles}
            difficulty={difficulty}
            onGenerate={generatePaper}
            setDifficulty={setDifficulty}
          />
        ) : (
          <div style={{ textAlign: 'center' }}>
            <HelpCircle size={64} style={{ color: '#667eea', marginBottom: '20px' }} />
            <h3>No Content Available</h3>
            <p style={{ marginBottom: '20px' }}>Please upload a file first to generate a question paper.</p>
            <motion.button
              className="btn"
              onClick={() => navigate('/')}
              whileHover={{ scale: 1.05 }}
            >
              <Upload size={20} />
              Upload File
            </motion.button>
          </div>
        )}
      </div>
    </div>
  );
};

const ResourcesPage = ({ uploadedFiles }) => {
  const navigate = useNavigate();
  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '30px' }}>
          <motion.button
            onClick={() => navigate('/')}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              color: '#667eea',
              fontSize: '14px'
            }}
            whileHover={{ scale: 1.05 }}
          >
            <ArrowLeft size={20} />
            Back
          </motion.button>
          <h1>Study Resources</h1>
        </div>
        
        <Resources uploadedFiles={uploadedFiles} />
      </div>
    </div>
  );
};

const App = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [showQuizSuggestion, setShowQuizSuggestion] = useState(false);
  const [detectedTopic, setDetectedTopic] = useState('');
  const [showToast, setShowToast] = useState({ show: false, message: '', type: 'success' });

  useEffect(() => {
    let timer;
    if (uploadedFiles.length > 0) {
      timer = setTimeout(() => {
        setShowQuizSuggestion(true);
      }, 5000); // Auto-suggest after 5 seconds
    }
    return () => clearTimeout(timer);
  }, [uploadedFiles]);

  const handleFileUpload = (fileData) => {
    setUploadedFiles((prevFiles) => [...prevFiles, fileData]);
    displayToast('File uploaded and processed successfully!', 'success');
  };

  const handleTopicDetected = (topic) => {
    setDetectedTopic(topic);
  };

  const handleQuizAccept = () => {
    setShowQuizSuggestion(false);
    navigate('/quiz');
  };

  const handleQuizReject = () => {
    setShowQuizSuggestion(false);
  };

  const handleQuizComplete = () => {
    // Handle quiz completion
  };

  const handleQuestionPaperGenerate = (data) => {
    displayToast(`Question paper generated for ${data.difficulty} difficulty!`, 'success');
    // Simulate PDF download (replace with actual logic)
    console.log('Download PDF:', data);
  };

  const displayToast = (message, type = 'success') => {
    setShowToast({ show: true, message, type });
    setTimeout(() => {
      setShowToast({ show: false, message: '', type: 'success' });
    }, 3000);
  };

  return (
    <Router>
      <div className="app">
        <Navbar />
        <AnimationWrapper>
          <Routes>
            <Route 
              path="/" 
              element={
                <HomePage 
                  uploadedFiles={uploadedFiles}
                  handleFileUpload={handleFileUpload}
                  handleTopicDetected={handleTopicDetected}
                />
              } 
            />
            <Route 
              path="/quiz" 
              element={
                <QuizPage 
                  uploadedFiles={uploadedFiles}
                  detectedTopic={detectedTopic}
                  handleQuizComplete={handleQuizComplete}
                />
              } 
            />
            <Route 
              path="/question-paper" 
              element={
                <QuestionPaperPage 
                  uploadedFiles={uploadedFiles}
                  handleQuestionPaperGenerate={handleQuestionPaperGenerate}
                />
              } 
            />
            <Route 
              path="/resources" 
              element={<ResourcesPage uploadedFiles={uploadedFiles} />} 
            />
            <Route 
              path="*" 
              element={
                <div className="container">
                  <div className="card">
                    <h1>Page Not Found</h1>
                  </div>
                </div>
              } 
            />
          </Routes>
        </AnimationWrapper>
        <QuizSuggestionModal
          topic={detectedTopic}
          onAccept={handleQuizAccept}
          onReject={handleQuizReject}
          isOpen={showQuizSuggestion}
        />
        <Toast
          show={showToast.show}
          message={showToast.message}
          type={showToast.type}
          onClose={() => setShowToast({ show: false, message: '', type: 'success' })}
        />
      </div>
    </Router>
  );
};

export default App;
