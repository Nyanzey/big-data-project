import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import VideoDetails from './pages/VideoDetails';
import './index.css';

function App() {
  return (
    <Router>
    <Layout>

    <Routes>

    <Route path="/" element={
      <Home />
    } />
    <Route path="/video/:id" element={<VideoDetails />} />

    </Routes>
    </Layout>

    </Router>
  );
}

export default App;
