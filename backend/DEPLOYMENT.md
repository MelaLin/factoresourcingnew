# 🚀 FactorESourcing Deployment Guide

This guide explains how to deploy your FastAPI backend and React frontend together on Render using a single URL.

## 📁 **Updated Project Structure**

After deployment preparation, your project will have this structure:

```
project-root/
├── backend/                    # Root directory for Render
│   ├── main.py                # FastAPI app (updated to serve frontend)
│   ├── scraper.py
│   ├── requirements.txt       # Updated dependencies
│   ├── frontend/              # Copied from frontend/dist/ during build
│   │   ├── index.html
│   │   ├── static/
│   │   └── ...
│   └── ... (other backend files)
├── frontend/                   # Source code for development
│   ├── package.json
│   ├── src/
│   └── dist/                  # Built files (generated)
├── deploy.sh                   # Deployment preparation script
└── DEPLOYMENT.md              # This file
```

## 🔧 **Backend Changes Made**

### 1. **API Routes Moved to `/api/*`**
- All API endpoints now use `/api/` prefix to avoid conflicts with frontend routes
- Example: `/sources` → `/api/sources`

### 2. **Frontend Serving**
- FastAPI now serves React static files
- All non-API routes serve the frontend (React Router handles client-side routing)
- Static files mounted at `/static/`

### 3. **New Endpoints Added**
- `GET /api/hello` - Example endpoint
- `GET /api/history` - History endpoints for the frontend

## 🚀 **Deployment Steps**

### **Step 1: Prepare for Deployment**
```bash
# Run the deployment preparation script
./deploy.sh
```

This script will:
- Install frontend dependencies
- Build the React frontend (`npm run build`)
- Copy built files to `backend/frontend/`
- Prepare the unified structure

### **Step 2: Render Configuration**

Create a new **Web Service** on Render with these settings:

#### **Basic Settings**
- **Name**: `sourcing-factore` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users

#### **Build & Deploy Settings**
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### **Environment Variables**
Add these if needed:
```
OPENAI_API_KEY=your_openai_api_key
```

### **Step 3: Deploy**
1. Connect your GitHub repository
2. Click "Create Web Service"
3. Render will automatically build and deploy

## 🌐 **How It Works**

### **Production URL Structure**
- **Frontend**: `https://your-app.onrender.com/` (any route)
- **API**: `https://your-app.onrender.com/api/*`
- **Static Files**: `https://your-app.onrender.com/static/*`

### **Request Flow**
1. **API Requests** (`/api/*`) → FastAPI backend
2. **Static Files** (`/static/*`) → React build files
3. **All Other Routes** → React frontend (handled by React Router)

## 🔄 **Development vs Production**

### **Development**
- Frontend runs on Vite dev server (e.g., `http://localhost:5173`)
- Backend runs on FastAPI (e.g., `http://localhost:8000`)
- Frontend calls backend APIs directly

### **Production**
- Both frontend and backend served from same domain
- Frontend built and served by FastAPI
- No CORS issues (same origin)

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **Frontend Not Loading**
   - Check if `backend/frontend/` directory exists
   - Verify `npm run build` completed successfully
   - Check Render build logs

2. **API Endpoints Not Working**
   - Ensure all routes use `/api/` prefix
   - Check FastAPI logs in Render dashboard

3. **Static Files 404**
   - Verify static files are in `backend/frontend/static/`
   - Check if `app.mount("/static", ...)` is working

### **Debug Commands**
```bash
# Check if frontend is built
ls -la frontend/dist/

# Check if files are copied to backend
ls -la backend/frontend/

# Test backend locally
cd backend
uvicorn main:app --reload
```

## 📝 **API Endpoints Reference**

### **Content Management**
- `POST /api/sources` - Add content source
- `POST /api/thesis/upload` - Upload thesis file
- `POST /api/blog/upload` - Upload blog/website
- `GET /api/matches` - Get matched content

### **Utility**
- `GET /api/hello` - Example endpoint
- `GET /api/health` - Health check
- `GET /api/history` - Get history
- `GET /api/docs` - API documentation

## 🔄 **Updating the Deployment**

To update your deployment:

1. **Make changes** to your code
2. **Run deployment script**: `./deploy.sh`
3. **Commit and push** to GitHub
4. **Render auto-deploys** the changes

## 🎯 **Benefits of This Setup**

✅ **Single URL** for both frontend and backend
✅ **No CORS issues** in production
✅ **Simplified deployment** (one service)
✅ **Cost effective** (single Render service)
✅ **Easy updates** (unified deployment)

## 🚀 **Ready to Deploy!**

Your project is now configured for unified deployment. Run `./deploy.sh` and follow the Render setup steps above.

Happy deploying! 🎉
