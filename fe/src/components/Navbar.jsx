import React from 'react';
import { Link } from 'react-router-dom';
import { Upload, FileText, BookOpen, HelpCircle } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">StudyMaster</div>
      <div className="navbar-links">
        <Link to="/" className="nav-link">
          <Upload size={20} />
          <span>Home</span>
        </Link>
        <Link to="/question-paper" className="nav-link">
          <FileText size={20} /> {/* 📄 Icon */}
          <span>Question Paper</span>
        </Link>
        <Link to="/quiz" className="nav-link">
          <HelpCircle size={20} /> {/* 🎯 Icon */}
          <span>Quiz</span>
        </Link>
        <Link to="/resources" className="nav-link">
          <BookOpen size={20} /> {/* 📚 Icon */}
          <span>Resources</span>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;