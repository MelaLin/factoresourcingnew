# 🚀 Single Service Deployment Guide

## Overview
This deployment approach serves both the **FastAPI backend** and **React frontend** from a single service on Render. The backend serves the frontend static files directly, eliminating the need for separate services.

## 🏗️ Architecture
```
Single Service (factoresourcing)
├── FastAPI Backend (Port 8000)
│   ├── API Endpoints (/api/*)
│   ├── Frontend Static Files (/)
│   └── SPA Routing (/*)
└── Frontend Assets
    ├── index.html
    ├── CSS files
    └── JavaScript files
```

## 📋 Prerequisites
- GitHub repository with the updated code
- Render account (free tier works)
- OpenAI API key (optional, for AI features)

## 🚀 Deployment Steps

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Single service deployment: backend serves frontend"
git push origin main
```

### 2. Deploy on Render
1. **Go to [Render Dashboard](https://dashboard.render.com)**
2. **Click "New +" → "Blueprint"**
3. **Connect your GitHub repository**: `MelaLin/factoresourcingnew`
4. **Select the main branch**
5. **Review the render.yaml configuration**:
   ```yaml
   services:
     - type: web
       name: factoresourcing
       env: python
       plan: starter
       rootDir: backend
       buildCommand: python -m pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
       startCommand: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
6. **Click "Apply" to deploy**

### 3. Environment Variables (Optional)
If you have an OpenAI API key, add it in Render:
- **Key**: `OPENAI_API_KEY`
- **Value**: `your-openai-api-key-here`

## 🔧 How It Works

### Backend Serves Frontend
- **Root route (`/`)**: Serves `frontend/index.html`
- **Asset routes (`/assets/*`)**: Serves CSS, JS, images
- **API routes (`/api/*`)**: FastAPI endpoints
- **SPA routes (`/*`)**: Serves `frontend/index.html` for client-side routing

### Frontend Configuration
- **API calls**: Use relative paths (e.g., `/api/sources`)
- **No CORS issues**: Same domain for frontend and backend
- **Simplified deployment**: Single service to manage

## 🌐 Access Your App
- **Main URL**: `https://factoresourcing.onrender.com`
- **API Docs**: `https://factoresourcing.onrender.com/api/docs`
- **Health Check**: `https://factoresourcing.onrender.com/api/health`

## 🧪 Testing
1. **Frontend**: Visit the main URL
2. **API**: Test endpoints at `/api/docs`
3. **File Upload**: Try uploading a thesis
4. **Content Matching**: Add sources and test matching

## 🔍 Troubleshooting

### Build Issues
- **Python version**: Ensure Python 3.11+ is used
- **Dependencies**: Check `requirements.txt` is up to date
- **Build logs**: Review Render build logs for errors

### Runtime Issues
- **Port binding**: Ensure `$PORT` environment variable is set
- **File paths**: Verify frontend files are in `backend/frontend/`
- **API endpoints**: Check `/api/health` for backend status

## 💰 Cost
- **Free tier**: ✅ Available
- **Starter plan**: $7/month (if you need more resources)
- **Single service**: More cost-effective than separate services

## 🔄 Updates
- **Automatic**: Code changes trigger auto-deploy
- **Manual**: Push to GitHub main branch
- **Rollback**: Available in Render dashboard

## 📚 Benefits
1. **Simplified deployment**: One service instead of two
2. **No CORS issues**: Same domain for everything
3. **Cost effective**: Single service pricing
4. **Easier maintenance**: One codebase, one deployment
5. **Better performance**: No cross-origin requests

## 🎯 Next Steps
1. Deploy using the Blueprint
2. Test all functionality
3. Add your OpenAI API key if needed
4. Customize the frontend as desired

---

**Need help?** Check the Render logs or review the backend code for any issues.
