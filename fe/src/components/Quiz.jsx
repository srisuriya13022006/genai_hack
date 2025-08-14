import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './Quiz.css';

const Quiz = ({ topic, onComplete, difficulty = 'medium', timeLimit = null }) => {
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [score, setScore] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(timeLimit);
  const [isLoading, setIsLoading] = useState(true);
  const [showExplanation, setShowExplanation] = useState(false);
  const [userAnswers, setUserAnswers] = useState([]);
  const [isAnswered, setIsAnswered] = useState(false);

  // Enhanced question generation based on topic and difficulty
  useEffect(() => {
    const generateQuestions = () => {
      const questionBank = {
        easy: [
          {
            id: 1,
            text: `What is the basic definition of ${topic}?`,
            options: ['Option A - Basic concept', 'Option B - Advanced concept', 'Option C - Complex theory', 'Option D - Abstract idea'],
            answer: 'Option A - Basic concept',
            explanation: `${topic} is fundamentally about understanding basic concepts and principles.`,
            type: 'multiple-choice'
          },
          {
            id: 2,
            text: `Which of the following is most related to ${topic}?`,
            options: ['Related concept A', 'Unrelated concept B', 'Different field C', 'Random topic D'],
            answer: 'Related concept A',
            explanation: `Related concept A is directly connected to ${topic} in fundamental ways.`,
            type: 'multiple-choice'
          }
        ],
        medium: [
          {
            id: 1,
            text: `Explain the key principles of ${topic} and their applications.`,
            type: 'short-answer',
            sampleAnswer: `Key principles include understanding core concepts and applying them effectively.`,
            points: 10
          },
          {
            id: 2,
            text: `What are the main advantages and disadvantages of ${topic}?`,
            options: ['Advantages outweigh disadvantages', 'Disadvantages outweigh advantages', 'Balanced pros and cons', 'No clear advantages or disadvantages'],
            answer: 'Balanced pros and cons',
            explanation: `Most topics have both advantages and disadvantages that need to be carefully considered.`,
            type: 'multiple-choice'
          }
        ],
        hard: [
          {
            id: 1,
            text: `Analyze the complex relationship between ${topic} and its broader implications.`,
            type: 'long-answer',
            sampleAnswer: `This requires deep analysis of interconnected concepts and their far-reaching effects.`,
            points: 20
          },
          {
            id: 2,
            text: `Which advanced concept best describes the theoretical framework of ${topic}?`,
            options: ['Advanced Framework A', 'Complex Theory B', 'Integrated Model C', 'Holistic Approach D'],
            answer: 'Integrated Model C',
            explanation: `Integrated models provide the most comprehensive understanding of complex topics.`,
            type: 'multiple-choice'
          }
        ]
      };

      const selectedQuestions = questionBank[difficulty] || questionBank.medium;
      setQuestions(selectedQuestions);
      setIsLoading(false);
    };

    setTimeout(generateQuestions, 1500); // Simulate loading time
  }, [topic, difficulty]);

  // Timer functionality
  useEffect(() => {
    if (timeLimit && timeRemaining > 0 && !showResult) {
      const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0) {
      handleTimeUp();
    }
  }, [timeRemaining, showResult, timeLimit]);

  const handleTimeUp = () => {
    setShowResult(true);
    onComplete({ score, total: questions.length, timeUp: true });
  };

  const handleAnswer = useCallback((answer) => {
    if (isAnswered) return;
    
    setSelectedAnswer(answer);
    setIsAnswered(true);
    
    const currentQ = questions[currentQuestion];
    const isCorrect = currentQ.type === 'multiple-choice' ? answer === currentQ.answer : answer.trim().length > 0;
    
    if (isCorrect) {
      setScore(prev => prev + (currentQ.points || 1));
    }

    setUserAnswers(prev => [...prev, { question: currentQ.text, userAnswer: answer, correct: isCorrect }]);
    setShowExplanation(true);
  }, [currentQuestion, questions, isAnswered]);

  const nextQuestion = () => {
    if (currentQuestion + 1 < questions.length) {
      setCurrentQuestion(prev => prev + 1);
      setSelectedAnswer('');
      setShowExplanation(false);
      setIsAnswered(false);
    } else {
      setShowResult(true);
      onComplete({ 
        score, 
        total: questions.length, 
        userAnswers,
        percentage: Math.round((score / questions.length) * 100)
      });
    }
  };

  const resetQuiz = () => {
    setCurrentQuestion(0);
    setScore(0);
    setSelectedAnswer('');
    setShowResult(false);
    setTimeRemaining(timeLimit);
    setShowExplanation(false);
    setUserAnswers([]);
    setIsAnswered(false);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="quiz-container quiz-loading-state">
        <div className="quiz-loader" />
        <p>Generating questions for {topic}...</p>
      </div>
    );
  }

  if (showResult) {
    const percentage = Math.round((score / questions.length) * 100);
    return (
      <motion.div
        className="quiz-container result"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <h2>🎉 Quiz Complete!</h2>
        <div className="score-display">
          <div className="score-circle">
            <span className="percentage">{percentage}%</span>
            <span className="score-text">{score} / {questions.length}</span>
          </div>
        </div>
        
        <div className="performance-indicator">
          {percentage >= 80 && <p className="excellent">Excellent work! 🌟</p>}
          {percentage >= 60 && percentage < 80 && <p className="good">Good job! 👍</p>}
          {percentage < 60 && <p className="needs-improvement">Keep practicing! 📚</p>}
        </div>

        <div className="quiz-summary">
          <h3>Review Your Answers:</h3>
          {userAnswers.map((answer, index) => (
            <div key={index} className={`answer-review ${answer.correct ? 'correct' : 'incorrect'}`}>
              <p><strong>Q{index + 1}:</strong> {answer.question}</p>
              <p><strong>Your Answer:</strong> {answer.userAnswer}</p>
              <span className={`result-indicator ${answer.correct ? 'correct' : 'incorrect'}`}>
                {answer.correct ? '✓' : '✗'}
              </span>
            </div>
          ))}
        </div>

        <div className="action-buttons">
          <button className="btn primary" onClick={resetQuiz}>
            Retake Quiz
          </button>
          <button className="btn secondary" onClick={() => onComplete({ score, total: questions.length })}>
            Finish
          </button>
        </div>
      </motion.div>
    );
  }

  const question = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className="quiz-container">
      {/* Header */}
      <div className="quiz-header">
        <div className="quiz-info">
          <h1>{topic} Quiz</h1>
          <span className="difficulty-badge">{difficulty}</span>
        </div>
        {timeLimit && (
          <div className={`timer ${timeRemaining <= 30 ? 'warning' : ''}`}>
            ⏱️ {formatTime(timeRemaining)}
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="progress-container">
        <div className="progress-bar">
          <motion.div
            className="progress-fill"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
        <span className="progress-text">
          Question {currentQuestion + 1} of {questions.length}
        </span>
      </div>

      {/* Question */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestion}
          className="question-container"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.3 }}
        >
          <h2 className="question-text">{question.text}</h2>

          {question.type === 'multiple-choice' ? (
            <div className="options-container">
              {question.options.map((option, index) => (
                <motion.button
                  key={index}
                  className={`option-btn ${selectedAnswer === option ? 'selected' : ''} ${isAnswered && option === question.answer ? 'correct' : ''} ${isAnswered && selectedAnswer === option && option !== question.answer ? 'incorrect' : ''}`}
                  onClick={() => handleAnswer(option)}
                  disabled={isAnswered}
                  whileHover={!isAnswered ? { scale: 1.02, x: 5 } : {}}
                  whileTap={!isAnswered ? { scale: 0.98 } : {}}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <span className="option-letter">{String.fromCharCode(65 + index)}</span>
                  <span className="option-text">{option}</span>
                </motion.button>
              ))}
            </div>
          ) : (
            <div className="text-answer-container">
              <textarea
                className="text-input"
                placeholder="Type your answer here..."
                value={selectedAnswer}
                onChange={(e) => setSelectedAnswer(e.target.value)}
                disabled={isAnswered}
                rows={question.type === 'long-answer' ? 6 : 3}
              />
              {!isAnswered && (
                <button
                  className="btn submit-btn"
                  onClick={() => handleAnswer(selectedAnswer)}
                  disabled={!selectedAnswer.trim()}
                >
                  Submit Answer
                </button>
              )}
            </div>
          )}

          {/* Explanation */}
          <AnimatePresence>
            {showExplanation && question.explanation && (
              <motion.div
                className="explanation"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
              >
                <h4>💡 Explanation:</h4>
                <p>{question.explanation}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Next Button */}
          {isAnswered && (
            <motion.button
              className="btn primary next-btn"
              onClick={nextQuestion}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {currentQuestion + 1 === questions.length ? 'View Results' : 'Next Question'} →
            </motion.button>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Score Display */}
      <div className="current-score">
        Current Score: {score} / {questions.length}
      </div>
    </div>
  );
};

export default Quiz;