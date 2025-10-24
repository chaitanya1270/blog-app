import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { postsAPI, commentsAPI } from '../services/api';

const PostDetail = () => {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPost();
  }, [id]);

  const fetchPost = async () => {
    try {
      setLoading(true);
      const response = await postsAPI.getPost(id);
      setPost(response.data);
    } catch (error) {
      console.error('Error fetching post:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setSubmitting(true);
      await commentsAPI.createComment(id, { content: newComment });
      setNewComment('');
      // Refresh the post to get updated comments
      await fetchPost();
    } catch (error) {
      console.error('Error submitting comment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <p>Loading post...</p>
        </div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="container">
        <div className="text-center">
          <h1>Post not found</h1>
          <Link to="/" className="btn btn-primary">Back to Home</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="mb-6">
        <Link to="/" className="btn btn-secondary mb-4">← Back to Posts</Link>
        
        <h1 className="text-3xl font-bold mb-4">{post.title}</h1>
        
        <div className="flex items-center gap-4 mb-6 text-gray-600">
          <span>By <strong>{post.author.username}</strong></span>
          <span>•</span>
          <span>{formatDate(post.created_at)}</span>
        </div>

        {post.image_url && (
          <img 
            src={`http://localhost:8000${post.image_url}`} 
            alt={post.title}
            className="post-image mb-6"
          />
        )}

        <div className="mb-6">
          {post.tags.map(tag => (
            <span key={tag} className="tag bg-blue-100 text-blue-800 mr-2">
              {tag}
            </span>
          ))}
        </div>

        <div className="prose max-w-none">
          <p className="text-lg leading-relaxed whitespace-pre-wrap">{post.content}</p>
        </div>
      </div>

      {/* Comments Section */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-4">Comments ({post.comments.length})</h2>
        
        {/* Add Comment Form */}
        {isAuthenticated ? (
          <form onSubmit={handleSubmitComment} className="mb-6">
            <div className="form-group">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Write a comment..."
                className="form-input"
                rows="3"
                required
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="btn btn-primary"
            >
              {submitting ? 'Posting...' : 'Post Comment'}
            </button>
          </form>
        ) : (
          <div className="mb-6 p-4 bg-gray-100 rounded">
            <p className="text-gray-600">
              <Link to="/login" className="text-blue-600 hover:underline">Login</Link> to post comments
            </p>
          </div>
        )}

        {/* Comments List */}
        {post.comments.length === 0 ? (
          <p className="text-gray-500">No comments yet. Be the first to comment!</p>
        ) : (
          <div className="space-y-4">
            {post.comments.map(comment => (
              <div key={comment.id} className="border-l-4 border-gray-200 pl-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-semibold">{comment.author.username}</span>
                  <span className="text-sm text-gray-500">
                    {formatDate(comment.created_at)}
                  </span>
                </div>
                <p className="text-gray-700">{comment.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PostDetail;