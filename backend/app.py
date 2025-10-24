from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import uuid
import jwt
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# CORS configuration
CORS(app, resources={r"/api/*": {
    "origins": "http://localhost:3000",
    "supports_credentials": True,
    "allow_headers": ["Content-Type", "Authorization"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
}})

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# JWT Token functions
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Set current_user for the function
        from flask import g
        g.current_user = User.query.get(user_id)
        return f(*args, **kwargs)
    return decorated

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    author = db.relationship('User', backref='posts')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='post_tags', backref='posts')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# Association table for post-tag many-to-many relationship
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    author = db.relationship('User', backref='comments')

# Create tables
with app.app_context():
    db.create_all()

# API Routes
# Admin Authentication Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('landing_page'))
        else:
            flash('Invalid credentials', 'error')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .login-container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; }
            h2 { text-align: center; color: #333; margin-bottom: 1.5rem; }
            input { width: 100%; padding: 0.8rem; margin: 0.5rem 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; padding: 0.8rem; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; }
            button:hover { background: #0056b3; }
            .error { color: red; text-align: center; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>Admin Login</h2>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <div class="error">Username: admin, Password: admin123</div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/')
def landing_page():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get real statistics from database
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    
    # Get recent posts (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_posts = Post.query.filter(Post.created_at >= week_ago).count()
    
    # Get posts with comments (engagement)
    posts_with_comments = Post.query.filter(Post.comments.any()).count()
    engagement_rate = (posts_with_comments / total_posts * 100) if total_posts > 0 else 0
    
    # Get pending comments (if you add a status field later)
    pending_comments = 0  # For now, all comments are approved
    
    # Get recent comments
    recent_comments = Comment.query.filter(Comment.created_at >= week_ago).count()
    
    stats = {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
        'engagement_rate': round(engagement_rate, 1),
        'pending_comments': pending_comments
    }
    
    return render_template('landing.html', year=datetime.now().year, stats=stats)
    
# Auth Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Generate token for new user
    token = generate_token(user.id)
    
    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        token = generate_token(user.id)
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/user', methods=['GET'])
@token_required
def get_user():
    from flask import g
    return jsonify({
        'id': g.current_user.id,
        'username': g.current_user.username,
        'email': g.current_user.email
    })

# Posts Routes
@app.route('/api/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tag_filter = request.args.get('tag')
    
    query = Post.query
    
    # Filter by tag if provided
    if tag_filter:
        query = query.join(Post.tags).filter(Tag.name == tag_filter)
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'posts': [{
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'image_url': post.image_url,
            'author': {
                'id': post.author.id,
                'username': post.author.username
            },
            'tags': [tag.name for tag in post.tags],
            'comments_count': len(post.comments),
            'created_at': post.created_at.isoformat()
        } for post in posts.items],
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page
    })

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'image_url': post.image_url,
        'author': {
            'id': post.author.id,
            'username': post.author.username
        },
        'tags': [tag.name for tag in post.tags],
        'comments': [{
            'id': comment.id,
            'content': comment.content,
            'author': {
                'id': comment.author.id,
                'username': comment.author.username
            },
            'created_at': comment.created_at.isoformat()
        } for comment in post.comments],
        'created_at': post.created_at.isoformat()
    })

@app.route('/api/posts', methods=['POST'])
@token_required
def create_post():
    from flask import g
    data = request.get_json()
    
    post = Post(
        title=data['title'],
        content=data['content'],
        image_url=data.get('image_url'),
        author_id=g.current_user.id
    )
    
    # Handle tags
    if 'tags' in data:
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            post.tags.append(tag)
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'message': 'Post created successfully',
        'post': {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'image_url': post.image_url,
            'tags': [tag.name for tag in post.tags],
            'created_at': post.created_at.isoformat()
        }
    }), 201

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(post_id):
    from flask import g
    post = Post.query.get_or_404(post_id)
    
    # Check if user owns the post
    if post.author_id != g.current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    data = request.get_json()
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.image_url = data.get('image_url', post.image_url)
    post.updated_at = datetime.utcnow()
    
    # Update tags
    if 'tags' in data:
        post.tags.clear()
        for tag_name in data['tags']:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            post.tags.append(tag)
    
    db.session.commit()
    
    return jsonify({'message': 'Post updated successfully'})

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(post_id):
    from flask import g
    post = Post.query.get_or_404(post_id)
    
    # Check if user owns the post
    if post.author_id != g.current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'})

# Comments Routes
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def create_comment(post_id):
    from flask import g
    data = request.get_json()
    
    comment = Comment(
        content=data['content'],
        author_id=g.current_user.id,
        post_id=post_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'message': 'Comment added successfully',
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': {
                'id': comment.author.id,
                'username': comment.author.username
            },
            'created_at': comment.created_at.isoformat()
        }
    }), 201

# Tags Routes
@app.route('/api/tags', methods=['GET'])
def get_tags():
    tags = Tag.query.all()
    return jsonify([{'id': tag.id, 'name': tag.name} for tag in tags])

# Upload Routes
@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        # Add timestamp to make filename unique
        filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'url': f'/uploads/{filename}'
        })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Dashboard Routes
@app.route('/api/dashboard', methods=['GET'])
@token_required
def get_dashboard():
    from flask import g
    user = g.current_user
    
    # Get user's posts count
    posts_count = Post.query.filter_by(author_id=user.id).count()
    
    # Get user's comments count
    comments_made = Comment.query.filter_by(author_id=user.id).count()
    
    # Get comments on user's posts
    user_posts = Post.query.filter_by(author_id=user.id).all()
    comments_received = 0
    for post in user_posts:
        comments_received += Comment.query.filter_by(post_id=post.id).count()
    
    # Get recent posts
    recent_posts = Post.query.filter_by(author_id=user.id).order_by(Post.created_at.desc()).limit(5).all()
    
    return jsonify({
        'stats': {
            'posts_count': posts_count,
            'comments_made': comments_made,
            'comments_received': comments_received
        },
        'recent_posts': [{
            'id': post.id,
            'title': post.title,
            'created_at': post.created_at.isoformat()
        } for post in recent_posts]
    })

# RSS Feed Route
@app.route('/api/rss')
def rss_feed():
    # Get recent posts (last 20)
    posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
    
    # Create RSS XML
    rss = ET.Element("rss")
    rss.set("version", "2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    
    channel = ET.SubElement(rss, "channel")
    
    # Channel information
    ET.SubElement(channel, "title").text = "Blog Platform RSS Feed"
    ET.SubElement(channel, "description").text = "Latest blog posts from our platform"
    ET.SubElement(channel, "link").text = "http://localhost:8000"
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Add atom:link for self-reference
    atom_link = ET.SubElement(channel, "atom:link")
    atom_link.set("href", "http://localhost:8000/api/rss")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")
    
    # Add posts as items
    for post in posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post.title
        ET.SubElement(item, "description").text = post.content[:500] + "..." if len(post.content) > 500 else post.content
        ET.SubElement(item, "link").text = f"http://localhost:8000/api/posts/{post.id}"
        ET.SubElement(item, "guid").text = f"http://localhost:8000/api/posts/{post.id}"
        ET.SubElement(item, "pubDate").text = post.created_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
        ET.SubElement(item, "author").text = post.author.username
        
        # Add tags as categories
        for tag in post.tags:
            ET.SubElement(item, "category").text = tag.name
    
    # Convert to string
    rss_str = ET.tostring(rss, encoding='unicode', method='xml')
    
    return Response(rss_str, mimetype='application/rss+xml')

# Admin API Routes
@app.route('/api/admin/users')
def admin_get_users():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat(),
        'posts_count': len(user.posts),
        'comments_count': len(user.comments)
    } for user in users])

@app.route('/api/admin/posts')
def admin_get_posts():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
        'author': post.author.username,
        'created_at': post.created_at.isoformat(),
        'comments_count': len(post.comments),
        'tags': [tag.name for tag in post.tags],
        'image_url': post.image_url
    } for post in posts])

@app.route('/api/admin/comments')
def admin_get_comments():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return jsonify([{
        'id': comment.id,
        'content': comment.content,
        'author': comment.author.username,
        'post_title': comment.post.title,
        'created_at': comment.created_at.isoformat()
    } for comment in comments])

@app.route('/api/admin/stats')
def admin_get_stats():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    
    # Get recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_posts = Post.query.filter(Post.created_at >= week_ago).count()
    recent_comments = Comment.query.filter(Comment.created_at >= week_ago).count()
    
    # Get engagement rate
    posts_with_comments = Post.query.filter(Post.comments.any()).count()
    engagement_rate = (posts_with_comments / total_posts * 100) if total_posts > 0 else 0
    
    return jsonify({
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
        'engagement_rate': round(engagement_rate, 1),
        'pending_comments': 0  # All comments are approved for now
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)