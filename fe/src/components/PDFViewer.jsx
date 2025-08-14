import React from 'react';

// Basic PDFViewer component based on the extracted content preview in the code
const PDFViewer = ({ content }) => {
  return (
    <div style={{
      marginTop: '15px',
      maxHeight: '300px',
      overflow: 'auto',
      padding: '15px',
      background: 'white',
      borderRadius: '8px',
      fontSize: '14px',
      lineHeight: '1.5',
    }}>
      {content || 'No content to display'}
    </div>
  );
};

export default PDFViewer;