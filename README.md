# FactorESourcing

A content sourcing and matching platform for investment thesis analysis. This platform helps investors and researchers find relevant content from various sources and match it against their investment thesis.

## Features

- **Content Scraping**: Scrape articles, blog posts, and web content
- **Thesis Upload**: Upload and analyze investment thesis documents (PDF, Word, text)
- **Content Matching**: AI-powered matching between content and thesis using vector embeddings
- **Blog Monitoring**: Discover and monitor blogs for new content
- **Scholar & Patent Search**: Search academic papers and patents
- **History Tracking**: Track all content sources and thesis uploads

## Project Structure

```
sourcing-factore/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API server
│   ├── ai_utils.py         # AI utilities (summarization, embeddings)
│   ├── scraper.py          # Web scraping functionality
│   ├── vector_store.py     # Vector database for similarity search
│   ├── file_parser.py      # File parsing (PDF, Word, text)
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/                # Source code
│   ├── package.json        # Node.js dependencies
│   └── ...
├── package.json            # Root package.json with dev scripts
└── README.md              # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

5. Start the backend server:
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Development

From the root directory, you can use these commands:

- `npm run dev` - Start both backend and frontend in development mode
- `npm run dev:backend` - Start only the backend
- `npm run dev:frontend` - Start only the frontend
- `npm run build` - Build the frontend for production
- `npm run start` - Start the production backend

## API Endpoints

- `POST /api/sources` - Add new content source
- `POST /api/thesis/upload` - Upload thesis file
- `POST /api/blog/upload` - Upload blog/website
- `GET /api/matches` - Get matched content
- `GET /api/history` - Get content history
- `POST /api/scholar/search` - Search Google Scholar
- `POST /api/patents/search` - Search Google Patents

## Architecture

The platform uses a modular architecture:

- **FastAPI Backend**: RESTful API with async support
- **Vector Database**: FAISS for similarity search
- **AI Integration**: OpenAI API for advanced text processing
- **Web Scraping**: BeautifulSoup and newspaper3k for content extraction
- **React Frontend**: Modern UI with TypeScript and Tailwind CSS

## Clean Code Principles

This codebase has been cleaned up to follow these principles:

- ✅ No duplicate functions or mock data
- ✅ Clear separation of concerns
- ✅ Proper error handling and fallbacks
- ✅ Consistent naming conventions
- ✅ Removed legacy endpoints and unused code
- ✅ Real functionality instead of mock implementations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
