import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { postsAPI } from '../services/api';

const Home = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [availableTags, setAvailableTags] = useState([]);
  const [selectedTag, setSelectedTag] = useState('');

  useEffect(() => {
    fetchPosts();
    fetchTags();
  }, [currentPage, selectedTag]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const params = { page: currentPage, per_page: 10 };
      if (selectedTag) {
        params.tag = selectedTag;
      }
      const response = await postsAPI.getPosts(params);
      setPosts(response.data.posts);
      setTotalPages(response.data.pages);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const response = await postsAPI.getTags();
      setAvailableTags(response.data.map(tag => tag.name));
    } catch (error) {
      console.error('Error fetching tags:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <p>Loading posts...</p>
        </div>
      </div>
    );
  }

  const handleTagFilter = (tag) => {
    setSelectedTag(tag);
    setCurrentPage(1); // Reset to first page when filtering
  };

  const clearFilter = () => {
    setSelectedTag('');
    setCurrentPage(1);
  };

  return (
    <div className="container">
      <div className="flex justify-between items-center mb-6">
        <h1>Blog Posts</h1>
        <Link to="/login" className="btn btn-primary">
          Login to Create Posts
        </Link>
      </div>

      {/* Tag Filter */}
      <div className="tag-filter-section">
        <div className="tag-filter-header">
          <div className="tag-filter-title">
            <h3>Filter by Tags</h3>
            <p>Click on any tag to filter posts</p>
          </div>
          {selectedTag && (
            <button
              onClick={clearFilter}
              className="clear-filter-btn"
            >
              ✕ Clear Filter
            </button>
          )}
        </div>
        
        <div className="tag-filter-container">
          {availableTags.length > 0 ? (
            <div className="tag-grid">
              {availableTags.map(tag => (
                <button
                  key={tag}
                  onClick={() => handleTagFilter(tag)}
                  className={`tag-filter-item ${selectedTag === tag ? 'tag-filter-active' : ''}`}
                >
                  <span className="tag-icon">🏷️</span>
                  <span className="tag-text">{tag}</span>
                </button>
              ))}
            </div>
          ) : (
            <div className="no-tags">
              <p>No tags available</p>
            </div>
          )}
        </div>
        
        {selectedTag && (
          <div className="filter-status">
            <div className="filter-status-content">
              <span className="filter-icon">🔍</span>
              <span>Showing posts tagged with: <strong>{selectedTag}</strong></span>
            </div>
          </div>
        )}
      </div>

      {posts.length === 0 ? (
        <div className="card text-center">
          <h2>No posts found</h2>
          <p>Be the first to create a blog post!</p>
        </div>
      ) : (
        <div className="grid gap-6">
          {posts.map(post => (
            <div key={post.id} className="card">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold">{post.title}</h2>
                <span className="text-sm text-gray-500">
                  {formatDate(post.created_at)}
                </span>
              </div>
              
              {post.image_url && (
                <img 
                  src={`http://localhost:8000${post.image_url}`} 
                  alt={post.title}
                  className="post-image-thumbnail mb-4"
                />
              )}
              
              <div className="mb-4">
                <p className="text-gray-700">{post.content.substring(0, 200)}...</p>
              </div>
              
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-500">
                    By <span className="font-semibold">{post.author.username}</span>
                  </p>
                  <div className="flex gap-2 mt-2">
                    {post.tags.map(tag => (
                      <span key={tag} className="tag bg-blue-100 text-blue-800">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-500">
                    {post.comments_count} comments
                  </span>
                  <Link 
                    to={`/posts/${post.id}`} 
                    className="btn btn-secondary"
                  >
                    Read More
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-center mt-8">
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="btn btn-secondary"
            >
              Previous
            </button>
            <span className="flex items-center px-4">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="btn btn-secondary"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;