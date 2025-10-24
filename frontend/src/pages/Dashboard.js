import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { dashboardAPI, postsAPI } from '../services/api';

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated) {
      fetchDashboard();
    }
  }, [isAuthenticated]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getDashboard();
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="container">
        <div className="text-center">
          <h1>Please login to view dashboard</h1>
          <Link to="/login" className="btn btn-primary">Login</Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container">
        <div className="text-center">
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Welcome, {user?.username}!</h1>
        <p className="text-gray-600">Here's your blog activity overview</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card text-center">
          <h3 className="text-2xl font-bold text-blue-600">{dashboard?.stats?.posts_count || 0}</h3>
          <p className="text-gray-600">Posts Created</p>
        </div>
        <div className="card text-center">
          <h3 className="text-2xl font-bold text-green-600">{dashboard?.stats?.comments_made || 0}</h3>
          <p className="text-gray-600">Comments Made</p>
        </div>
        <div className="card text-center">
          <h3 className="text-2xl font-bold text-purple-600">{dashboard?.stats?.comments_received || 0}</h3>
          <p className="text-gray-600">Comments Received</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card mb-8">
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="flex gap-4">
          <Link to="/posts/create" className="btn btn-primary">
            Create New Post
          </Link>
          <Link to="/" className="btn btn-secondary">
            View All Posts
          </Link>
        </div>
      </div>

      {/* Recent Posts */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Your Recent Posts</h2>
        {dashboard?.recent_posts?.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">You haven't created any posts yet</p>
            <Link to="/posts/create" className="btn btn-primary">
              Create Your First Post
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {dashboard?.recent_posts?.map(post => (
              <div key={post.id} className="border-b border-gray-200 pb-4 last:border-b-0">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{post.title}</h3>
                    <p className="text-sm text-gray-500">
                      Created on {formatDate(post.created_at)}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Link 
                      to={`/posts/${post.id}`} 
                      className="btn btn-secondary btn-sm"
                    >
                      View
                    </Link>
                    <Link 
                      to={`/posts/edit/${post.id}`} 
                      className="btn btn-primary btn-sm"
                    >
                      Edit
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
