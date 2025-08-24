# Render Deployment Guide - Separate Services

This guide explains how to deploy your FactorESourcing application on Render using separate services for frontend and backend.

## 🏗️ **Architecture Overview**

- **Backend Service**: FastAPI server handling API requests, file processing, and AI operations
- **Frontend Service**: React static site served from CDN
- **Communication**: Frontend makes API calls to backend via HTTP

## 🚀 **Deployment Steps**

### **Step 1: Deploy Backend Service**

1. **Go to Render Dashboard** → New → Web Service
2. **Connect Repository**: Select your `factoresourcingnew` repository
3. **Configure Service**:
   - **Name**: `factoresourcing-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**:
   - `PORT`: Auto-set by Render
   - `OPENAI_API_KEY`: Your OpenAI API key (optional)

5. **Click Deploy** and wait for build to complete

6. **Copy the backend URL** (e.g., `https://factoresourcing-backend.onrender.com`)

### **Step 2: Deploy Frontend Service**

1. **Go to Render Dashboard** → New → Static Site
2. **Connect Repository**: Select your `factoresourcingnew` repository
3. **Configure Service**:
   - **Name**: `factoresourcing-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Environment Variables**:
   - `VITE_API_BASE_URL`: Set to your backend URL from Step 1
   - `NODE_VERSION`: `18.17.0`

5. **Click Deploy** and wait for build to complete

6. **Copy the frontend URL** (e.g., `https://factoresourcing-frontend.onrender.com`)

## 🔧 **Manual Configuration (Alternative to render.yaml)**

If you prefer to configure services manually instead of using the `render.yaml` file:

### **Backend Service Settings**
```
Name: factoresourcing-backend
Type: Web Service
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### **Frontend Service Settings**
```
Name: factoresourcing-frontend
Type: Static Site
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

## 🌍 **Environment Variables**

### **Backend Service**
| Variable | Value | Description |
|----------|-------|-------------|
| `PORT` | Auto-set | Port for the service |
| `OPENAI_API_KEY` | Your key | OpenAI API key for AI features |

### **Frontend Service**
| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_BASE_URL` | Backend URL | URL of your backend service |
| `NODE_VERSION` | `18.17.0` | Node.js version for building |

## 🔍 **Testing Your Deployment**

### **1. Test Backend API**
Visit your backend URL to see the API information:
```
https://factoresourcing-backend.onrender.com
```

You should see:
```json
{
  "message": "FactorESourcing API",
  "status": "Backend service running",
  "api_endpoints": {...}
}
```

### **2. Test Frontend**
Visit your frontend URL to see the React app:
```
https://factoresourcing-frontend.onrender.com
```

### **3. Test API Integration**
In the frontend, try:
- Adding a source URL
- Uploading a thesis file
- Checking content matches

## 🐛 **Troubleshooting**

### **Common Issues**

1. **CORS Errors**
   - Ensure backend CORS allows your frontend domain
   - Check that `VITE_API_BASE_URL` is correct

2. **Build Failures**
   - Verify Node.js version (18.17.0+)
   - Check Python version (3.9+)
   - Ensure all dependencies are in requirements.txt

3. **API Connection Issues**
   - Verify backend is running
   - Check environment variables
   - Test API endpoints directly

### **Debug Commands**

```bash
# Check backend logs
# In Render dashboard → Backend Service → Logs

# Check frontend build logs
# In Render dashboard → Frontend Service → Logs

# Test API locally
curl https://factoresourcing-backend.onrender.com/api/health
```

## 🔄 **Updating Your Application**

### **Automatic Deployments**
- Render automatically redeploys when you push to your main branch
- No manual intervention needed

### **Manual Deployments**
- Go to service dashboard
- Click "Manual Deploy"
- Select branch/commit

## 💰 **Cost Optimization**

- **Free Tier**: Both services are free on Render's free tier
- **Scaling**: Upgrade only when you need more resources
- **Monitoring**: Use Render's built-in monitoring tools

## 📚 **Additional Resources**

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Build Optimization](https://create-react-app.dev/docs/production-build/)

## 🎯 **Next Steps After Deployment**

1. **Set up custom domain** (optional)
2. **Configure monitoring and alerts**
3. **Set up CI/CD pipeline**
4. **Add SSL certificates**
5. **Configure backup strategies**

Your application is now deployed with a clean separation of concerns and can scale independently!
