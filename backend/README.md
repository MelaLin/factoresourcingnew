# FactorESourcing

A content sourcing and matching platform that helps you discover and analyze articles against your investment thesis.

## Features

- **Content Sourcing**: Add individual URLs or upload entire blogs/websites
- **Thesis Matching**: Upload your investment thesis and get AI-powered content matching
- **Article Analysis**: Automatic summarization, keyword extraction, and company identification
- **Blog Upload**: Bulk import articles from entire blogs or websites
- **Real-time Updates**: See matches update as you add content and thesis

## Local Development

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or bun

### Quick Start

1. **Clone and setup:**
   ```bash
   git clone <your-repo-url>
   cd sourcing-factore
   ./setup.sh
   ```

2. **Start both services:**
   ```bash
   ./dev.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:8080
   - Backend API: http://127.0.0.1:8000
   - API Docs: http://127.0.0.1:8000/docs

### Manual Start

**Backend:**
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Deployment

### Render Deployment (Recommended)

The application is configured for Render deployment:

1. **Connect your repository to Render**
2. **Set environment variables in Render:**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `VITE_API_BASE_URL`: Your Render backend URL (e.g., `https://your-app.onrender.com`)

3. **Deploy:**
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Frontend Build:**
   - Run `./deploy.sh` locally to build the frontend
   - This copies the built frontend to `backend/frontend/`
   - Render will serve both frontend and backend from the same URL

### Alternative: Separate Frontend/Backend

You can also deploy frontend and backend separately:

**Frontend (Vercel/Netlify):**
- Build command: `cd frontend && npm run build`
- Output directory: `frontend/dist`

**Backend (Render/Railway):**
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Project Structure

```
sourcing-factore/
├── backend/                 # FastAPI backend + built frontend
│   ├── main.py             # API endpoints + frontend serving
│   ├── scraper.py          # Web scraping
│   ├── ai_utils.py         # AI/ML utilities
│   ├── vector_store.py     # Vector search
│   ├── requirements.txt    # Python dependencies
│   ├── frontend/           # Built React frontend (copied by deploy.sh)
│   │   ├── index.html      # Main HTML file
│   │   └── assets/         # Built CSS/JS files
│   └── deploy.sh           # Frontend build + copy script
├── frontend/               # React/Vite source code
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── main.tsx        # App entry point
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── dev.sh                  # Development script
├── setup.sh                # Setup script
└── README.md               # This file
```

## API Endpoints

- `POST /sources` - Add individual content source
- `POST /blog/upload` - Upload blog/website and discover articles
- `POST /thesis/upload` - Upload thesis file
- `GET /matches` - Get matched content
- `GET /health` - Health check

## Environment Variables

### Frontend
- `VITE_API_BASE_URL`: Backend API URL

### Backend
- `OPENAI_API_KEY`: OpenAI API key (optional, uses mock data if not set)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License
