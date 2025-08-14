import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './Resources.css';

const Resources = ({ uploadedFiles, searchQuery = '' }) => {
  const [resources, setResources] = useState([]);
  const [filteredResources, setFilteredResources] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [favorites, setFavorites] = useState([]);
  const [viewMode, setViewMode] = useState('grid'); // grid or list

  // Enhanced resource generation based on topics
  useEffect(() => {
    const generateResources = () => {
      if (uploadedFiles.length > 0) {
        const allTopics = uploadedFiles.flatMap(file => file.topics || []);
        const uniqueTopics = [...new Set(allTopics)];
        
        const generatedResources = [];
        
        uniqueTopics.forEach((topic, topicIndex) => {
          // Videos
          generatedResources.push(
            {
              id: `video-${topicIndex}-1`,
              type: 'video',
              category: 'video',
              title: `${topic} - Complete Tutorial`,
              description: `Comprehensive video tutorial covering all aspects of ${topic}`,
              url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
              thumbnail: `https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg`,
              duration: '45:30',
              difficulty: 'Beginner',
              rating: 4.8,
              views: '2.1M',
              topic: topic,
              author: 'EduTech Academy',
              tags: ['tutorial', 'basics', topic.toLowerCase()]
            },
            {
              id: `video-${topicIndex}-2`,
              type: 'video',
              category: 'video',
              title: `Advanced ${topic} Concepts`,
              description: `Deep dive into advanced concepts and real-world applications of ${topic}`,
              url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
              thumbnail: `https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg`,
              duration: '1:12:45',
              difficulty: 'Advanced',
              rating: 4.9,
              views: '856K',
              topic: topic,
              author: 'Tech Masters',
              tags: ['advanced', 'concepts', topic.toLowerCase()]
            }
          );

          // Articles
          generatedResources.push(
            {
              id: `article-${topicIndex}-1`,
              type: 'article',
              category: 'article',
              title: `Understanding ${topic}: A Comprehensive Guide`,
              description: `In-depth article explaining the fundamentals and applications of ${topic}`,
              url: `https://example.com/${topic.toLowerCase().replace(/\s+/g, '-')}-guide`,
              thumbnail: 'https://via.placeholder.com/300x200?text=Article',
              readTime: '12 min read',
              difficulty: 'Intermediate',
              rating: 4.6,
              topic: topic,
              author: 'Knowledge Hub',
              tags: ['guide', 'fundamentals', topic.toLowerCase()],
              publishDate: '2024-01-15'
            },
            {
              id: `article-${topicIndex}-2`,
              type: 'article',
              category: 'article',
              title: `${topic} Best Practices and Tips`,
              description: `Expert tips and best practices for mastering ${topic}`,
              url: `https://example.com/${topic.toLowerCase().replace(/\s+/g, '-')}-tips`,
              thumbnail: 'https://via.placeholder.com/300x200?text=Tips',
              readTime: '8 min read',
              difficulty: 'Intermediate',
              rating: 4.7,
              topic: topic,
              author: 'Expert Insights',
              tags: ['tips', 'best-practices', topic.toLowerCase()],
              publishDate: '2024-02-20'
            }
          );

          // Interactive Content
          generatedResources.push(
            {
              id: `interactive-${topicIndex}-1`,
              type: 'interactive',
              category: 'interactive',
              title: `${topic} Interactive Simulator`,
              description: `Hands-on interactive tool to practice and experiment with ${topic} concepts`,
              url: `https://simulator.example.com/${topic.toLowerCase()}`,
              thumbnail: 'https://via.placeholder.com/300x200?text=Interactive',
              difficulty: 'All Levels',
              rating: 4.5,
              topic: topic,
              author: 'Interactive Learning',
              tags: ['interactive', 'practice', topic.toLowerCase()],
              features: ['Real-time feedback', 'Multiple scenarios', 'Progress tracking']
            }
          );

          // Books/PDFs
          generatedResources.push(
            {
              id: `book-${topicIndex}-1`,
              type: 'book',
              category: 'book',
              title: `The Complete ${topic} Handbook`,
              description: `Comprehensive reference book covering everything about ${topic}`,
              url: `https://books.example.com/${topic.toLowerCase()}-handbook.pdf`,
              thumbnail: 'https://via.placeholder.com/300x400?text=Book',
              pages: 324,
              difficulty: 'All Levels',
              rating: 4.8,
              topic: topic,
              author: 'Dr. Academic Expert',
              tags: ['reference', 'comprehensive', topic.toLowerCase()],
              isbn: '978-0123456789'
            }
          );
        });

        setResources(generatedResources);
        setFilteredResources(generatedResources);
      } else {
        // Default resources when no files uploaded
        const defaultResources = [
          {
            id: 'default-1',
            type: 'video',
            category: 'video',
            title: 'Getting Started with Learning',
            description: 'Learn how to make the most of your study sessions',
            url: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            thumbnail: 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
            duration: '25:15',
            difficulty: 'Beginner',
            rating: 4.7,
            views: '1.2M',
            topic: 'Study Skills',
            author: 'Learning Academy'
          }
        ];
        setResources(defaultResources);
        setFilteredResources(defaultResources);
      }
      
      setIsLoading(false);
    };

    setTimeout(generateResources, 1000); // Simulate loading time
  }, [uploadedFiles]);

  // Filter resources based on category and search query
  useEffect(() => {
    let filtered = resources;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(resource => resource.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      filtered = filtered.filter(resource =>
        resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        resource.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        resource.topic.toLowerCase().includes(searchQuery.toLowerCase()) ||
        resource.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    setFilteredResources(filtered);
  }, [resources, selectedCategory, searchQuery]);

  const categories = [
    { id: 'all', name: 'All Resources', icon: '📚' },
    { id: 'video', name: 'Videos', icon: '🎥' },
    { id: 'article', name: 'Articles', icon: '📄' },
    { id: 'interactive', name: 'Interactive', icon: '🎮' },
    { id: 'book', name: 'Books', icon: '📖' }
  ];

  const toggleFavorite = (resourceId) => {
    setFavorites(prev => 
      prev.includes(resourceId)
        ? prev.filter(id => id !== resourceId)
        : [...prev, resourceId]
    );
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner': return 'green';
      case 'intermediate': return 'orange';
      case 'advanced': return 'red';
      default: return 'blue';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'video': return '🎥';
      case 'article': return '📄';
      case 'interactive': return '🎮';
      case 'book': return '📖';
      default: return '📚';
    }
  };

  const openResource = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  if (isLoading) {
    return (
      <div className="resources-container resources-loading">
        <div className="resources-loader" />
        <p>Loading resources...</p>
      </div>
    );
  }

  return (
    <div className="resources-container">
      {/* Header */}
      <div className="resources-header">
        <div className="header-content">
          <h1>Learning Resources</h1>
          <p>Curated content to enhance your understanding</p>
        </div>
        
        {/* View Toggle */}
        <div className="view-controls">
          <button
            className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
          >
            <span className="view-icon">⊞</span>
            Grid
          </button>
          <button
            className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
          >
            <span className="view-icon">☰</span>
            List
          </button>
        </div>
      </div>

      {/* Category Filter */}
      <div className="category-filter">
        {categories.map(category => (
          <motion.button
            key={category.id}
            className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category.id)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="category-icon">{category.icon}</span>
            <span className="category-name">{category.name}</span>
            <span className="category-count">
              ({category.id === 'all' ? resources.length : resources.filter(r => r.category === category.id).length})
            </span>
          </motion.button>
        ))}
      </div>

      {/* Resources Grid/List */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`${viewMode}-${selectedCategory}`}
          className={`resources-grid ${viewMode}`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          {filteredResources.length === 0 ? (
            <div className="no-resources">
              <div className="no-resources-icon">🔍</div>
              <h3>No resources found</h3>
              <p>Try adjusting your filters or search terms</p>
            </div>
          ) : (
            filteredResources.map((resource, index) => (
              <motion.div
                key={resource.id}
                className={`resource-card ${resource.type}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                onClick={() => openResource(resource.url)}
              >
                {/* Card Header */}
                <div className="card-header">
                  <div className="type-badge">
                    <span className="type-icon">{getTypeIcon(resource.type)}</span>
                    <span className="type-text">{resource.type}</span>
                  </div>
                  <button
                    className={`favorite-btn ${favorites.includes(resource.id) ? 'active' : ''}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFavorite(resource.id);
                    }}
                  >
                    {favorites.includes(resource.id) ? '❤️' : '🤍'}
                  </button>
                </div>

                {/* Thumbnail */}
                {resource.thumbnail && (
                  <div className="card-thumbnail">
                    <img src={resource.thumbnail} alt={resource.title} />
                    {resource.duration && (
                      <div className="duration-badge">{resource.duration}</div>
                    )}
                    {resource.readTime && (
                      <div className="duration-badge">{resource.readTime}</div>
                    )}
                  </div>
                )}

                {/* Content */}
                <div className="card-content">
                  <h3 className="card-title">{resource.title}</h3>
                  <p className="card-description">{resource.description}</p>
                  
                  <div className="card-meta">
                    <div className="meta-row">
                      <span className="meta-item">
                        <span className="meta-icon">👤</span>
                        {resource.author}
                      </span>
                      {resource.difficulty && (
                        <span className={`difficulty-badge ${getDifficultyColor(resource.difficulty)}`}>
                          {resource.difficulty}
                        </span>
                      )}
                    </div>
                    
                    {resource.rating && (
                      <div className="rating">
                        <div className="stars">
                          {[...Array(5)].map((_, i) => (
                            <span key={i} className={`star ${i < Math.floor(resource.rating) ? 'filled' : ''}`}>
                              ⭐
                            </span>
                          ))}
                        </div>
                        <span className="rating-text">{resource.rating}</span>
                        {resource.views && <span className="views">• {resource.views} views</span>}
                      </div>
                    )}
                  </div>

                  {/* Tags */}
                  {resource.tags && (
                    <div className="card-tags">
                      {resource.tags.slice(0, 3).map(tag => (
                        <span key={tag} className="tag">#{tag}</span>
                      ))}
                    </div>
                  )}

                  {/* Features for interactive content */}
                  {resource.features && (
                    <div className="card-features">
                      <h4>Features:</h4>
                      <ul>
                        {resource.features.map(feature => (
                          <li key={feature}>{feature}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Card Footer */}
                <div className="card-footer">
                  <button className="access-btn">
                    <span className="btn-icon">🔗</span>
                    Access Resource
                  </button>
                  {resource.publishDate && (
                    <span className="publish-date">
                      Published: {new Date(resource.publishDate).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </motion.div>
            ))
          )}
        </motion.div>
      </AnimatePresence>

      {/* Statistics */}
      <div className="resources-stats">
        <div className="stat-item">
          <span className="stat-number">{filteredResources.length}</span>
          <span className="stat-label">Resources Found</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{favorites.length}</span>
          <span className="stat-label">Favorites</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{new Set(resources.map(r => r.topic)).size}</span>
          <span className="stat-label">Topics Covered</span>
        </div>
      </div>
    </div>
  );
};

export default Resources;