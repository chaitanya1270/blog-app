# Blog Platform with Admin Panel

A full-stack blog platform built with React.js frontend and Flask backend, featuring a classic, clean design with comprehensive admin functionality.

## Features

### Frontend (React.js)
- **Public Blog View**: Clean, responsive design with article listings
- **Admin Panel**: Comprehensive content management system
- **Rich Text Editor**: Full-featured editor for creating and editing posts
- **Comment System**: User comments with admin moderation
- **Tag-based Categorization**: Organize posts with custom tags
- **Responsive Design**: Works on desktop, tablet, and mobile

### Backend (Flask)
- **User Authentication**: Secure login system with session management
- **Blog Post CRUD**: Complete create, read, update, delete operations
- **Comment Moderation**: Admin approval system for comments
- **File Upload**: Image upload functionality for featured images
- **RSS Feed**: Automatic RSS feed generation for blog posts
- **RESTful API**: Clean API endpoints for all operations

## Project Structure

```
blog-platform/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   └── uploads/              # Uploaded images directory
├── frontend/
│   ├── public/
│   │   └── index.html        # HTML template
│   ├── src/
│   │   ├── components/       # Reusable React components
│   │   ├── contexts/         # React context providers
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service functions
│   │   ├── App.js           # Main app component
│   │   ├── index.js         # React entry point
│   │   └── index.css        # Global styles
│   └── package.json         # Node.js dependencies
└── README.md               # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application:**
   ```bash
   python app.py
   ```

   The backend will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

   The frontend will start on `http://localhost:3000`

## Default Admin Credentials

- **Username:** admin
- **Password:** admin123

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/user` - Get current user info

### Posts
- `GET /api/posts` - Get published posts (with pagination and filtering)
- `GET /api/posts/:id` - Get specific post
- `POST /api/posts` - Create new post (admin only)
- `PUT /api/posts/:id` - Update post (admin only)
- `DELETE /api/posts/:id` - Delete post (admin only)
- `GET /api/admin/posts` - Get all posts for admin

### Comments
- `GET /api/comments/:post_id` - Get approved comments for a post
- `POST /api/comments` - Submit new comment
- `GET /api/admin/comments` - Get all comments for moderation
- `POST /api/admin/comments/:id/approve` - Approve comment
- `DELETE /api/admin/comments/:id` - Delete comment

### Other
- `GET /api/tags` - Get all tags
- `POST /api/upload` - Upload image file
- `GET /api/rss` - RSS feed

## Usage

### For Visitors
1. Visit the homepage to browse published blog posts
2. Click on any post to read the full content
3. Leave comments on posts (comments require admin approval)
4. Filter posts by tags using the tag filter

### For Admins
1. Login at `/admin/login` using the default credentials
2. Access the dashboard to view statistics
3. Create, edit, and delete blog posts
4. Moderate comments (approve or delete)
5. Upload images for featured posts

## Features in Detail

### Rich Text Editor
- Full WYSIWYG editing with formatting options
- Support for headers, bold, italic, lists, links, and images
- Clean, intuitive interface

### Comment System
- Public users can leave comments with name and email
- All comments require admin approval before appearing
- Admin can approve or delete comments from the admin panel

### Tag System
- Create custom tags for categorizing posts
- Filter posts by tags on the public site
- Tags are automatically created when used in posts

### File Upload
- Support for image uploads (PNG, JPG, JPEG, GIF, WebP)
- Automatic file naming to prevent conflicts
- Images served from `/uploads/` endpoint

### RSS Feed
- Automatic RSS feed generation at `/api/rss`
- Includes latest 20 published posts
- Standard RSS 2.0 format

## Development

### Adding New Features
1. Backend: Add new routes in `app.py`
2. Frontend: Create new components in `src/components/`
3. API: Add new service functions in `src/services/api.js`

### Styling
- Global styles in `src/index.css`
- Uses CSS Grid and Flexbox for layout
- Responsive design with mobile-first approach
- Clean, modern design with consistent spacing

## Deployment

### Backend Deployment
1. Set up a production WSGI server (Gunicorn)
2. Configure environment variables
3. Set up a production database (PostgreSQL recommended)
4. Configure file upload storage

### Frontend Deployment
1. Build the production bundle: `npm run build`
2. Serve static files from a web server
3. Configure API URL for production backend

## Security Considerations

- All admin routes require authentication
- File uploads are restricted to image types
- Comments require approval before publication
- CSRF protection on forms
- Secure password hashing

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is open source and available under the MIT License.

