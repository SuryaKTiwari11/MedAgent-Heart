# 🫀 MedAgent-Heart

**An AI-powered cardiac health information system built with LangGraph, Groq, and Pinecone**

MedAgent-Heart is an intelligent RAG (Retrieval Augmented Generation) chatbot that provides information about heart diseases, treatments, symptoms, and prevention methods. It combines document-based knowledge retrieval with real-time web search capabilities to deliver accurate, up-to-date cardiac health information.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## ✨ Features

- 🤖 **Intelligent Agent System** - LangGraph-powered decision-making workflow
- 📚 **RAG Knowledge Base** - Upload and query medical documents (PDF)
- 🌐 **Web Search Integration** - Real-time information retrieval via Tavily
- 🔄 **Hybrid Approach** - Combines internal knowledge with web search
- 💬 **Interactive Chat UI** - Beautiful Streamlit-based interface
- 🔍 **Workflow Tracing** - Transparent agent decision-making process
- 🎨 **Modern Design** - Custom color palette with gradient accents

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Streamlit      │────────▶│   FastAPI        │
│  Frontend       │         │   Backend        │
│  (Port 8501)    │◀────────│   (Port 8000)    │
└─────────────────┘         └──────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │ Groq LLM │    │ Pinecone │    │  Tavily  │
              │  (AI)    │    │ (Vector  │    │  (Web    │
              │          │    │  Store)  │    │  Search) │
              └──────────┘    └──────────┘    └──────────┘
```

### Workflow

1. **Router** - Analyzes query and decides between RAG or Web Search
2. **RAG Lookup** - Searches uploaded documents in Pinecone
3. **Judge** - Evaluates if RAG results are sufficient
4. **Web Search** - Fetches latest information if needed
5. **Answer** - Generates final response using context

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Conda (recommended) or virtualenv
- API Keys for:
  - [Groq](https://console.groq.com/) - LLM inference
  - [Pinecone](https://www.pinecone.io/) - Vector database
  - [Tavily](https://tavily.com/) - Web search

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/angad2803/MedAgent-Heart.git
   cd MedAgent-Heart
   ```

2. **Create and activate conda environment**

   ```bash
   conda create -n medagent python=3.11 -y
   conda activate medagent
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the `backend/` directory:

   ```bash
   # backend/.env
   GROQ_API_KEY=your_groq_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=us-east-1
   PINECONE_INDEX_NAME=langgraph-rag-index
   TAVILY_API_KEY=your_tavily_api_key_here
   EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

### Running the Application

#### Option 1: Using Separate Terminals (Recommended)

**Terminal 1 - Backend Server:**

```bash
cd backend
conda activate medagent
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend Server:**

```bash
conda activate medagent
streamlit run frontend/app.py
```

#### Option 2: Using Full Python Path (Windows)

**Backend:**

```bash
cd backend
D:\anaconda3\envs\medagent\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
D:\anaconda3\envs\medagent\python.exe -m streamlit run frontend\app.py
```

### Accessing the Application

- 🌐 **Frontend UI**: http://localhost:8501
- 🔧 **Backend API**: http://localhost:8000
- 📖 **API Docs**: http://localhost:8000/docs
- ✅ **Health Check**: http://localhost:8000/health

## 📂 Project Structure

```
MedAgent-Heart/
├── backend/
│   ├── agent.py              # LangGraph agent workflow
│   ├── config.py             # Configuration management
│   ├── main.py               # FastAPI application
│   ├── vectorstore.py        # Pinecone vector store
│   └── .env                  # Environment variables
├── frontend/
│   ├── app.py                # Main Streamlit app
│   ├── backendApi.py         # Backend API client
│   ├── config.py             # Frontend config
│   ├── session_manager.py    # Session state management
│   └── ui_components.py      # UI components & styling
├── dataForRag/
│   └── heart_dieasespdf.pdf  # Sample medical document
├── requirements.txt          # Python dependencies
├── test_api.py               # API endpoint tests
├── quick_test.py             # Quick functionality test
├── final_test.py             # Comprehensive test suite
└── README.md                 # This file
```

## 🎨 Color Palette

The application uses a custom Tailwind-inspired color scheme:

- **Charcoal** (#17191c - #2f3137) - Dark backgrounds
- **Electric Aqua** (#00eaff) - Primary accent, headers, highlights
- **Burnt Peach** (#f73c08) - Error states
- **Tuscan Sun** (#f7b708) - Warning states
- **Soft Blush** (#ff0000) - Critical alerts

## 🧪 Testing

### Run API Tests

```bash
# Quick test
python quick_test.py

# Full test suite
python final_test.py

# Upload test
python test_upload.py
```

### Test Endpoints Manually

**Chat Endpoint:**

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-001",
    "query": "What are the treatments for heart disease?",
    "enable_web_search": true
  }'
```

**Upload Document:**

```bash
curl -X POST http://localhost:8000/upload-document/ \
  -F "file=@dataForRag/heart_dieasespdf.pdf"
```

## 📚 API Documentation

### POST `/chat/`

Chat with the AI agent.

**Request Body:**

```json
{
  "session_id": "unique-session-id",
  "query": "Your question here",
  "enable_web_search": true
}
```

**Response:**

```json
{
  "response": "Agent's answer",
  "trace_events": [
    {
      "step": 1,
      "node_name": "router",
      "description": "Router decided: 'rag'",
      "details": {},
      "event_type": "router_decision"
    }
  ]
}
```

### POST `/upload-document/`

Upload a PDF document to the knowledge base.

**Request:** Multipart form data with PDF file

**Response:**

```json
{
  "message": "PDF 'filename.pdf' successfully uploaded and indexed.",
  "filename": "filename.pdf",
  "processed_chunks": 66
}
```

### GET `/health`

Health check endpoint.

**Response:**

```json
{
  "status": "ok"
}
```

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)

- `PINECONE_API_KEY` - Pinecone API key
- `PINECONE_ENVIRONMENT` - Pinecone environment (default: us-east-1)
- `PINECONE_INDEX_NAME` - Index name (default: langgraph-rag-index)
- `GROQ_API_KEY` - Groq API key for LLM
- `TAVILY_API_KEY` - Tavily API key for web search
- `EMBED_MODEL` - Embedding model (default: sentence-transformers/all-MiniLM-L6-v2)

### Frontend Configuration (`frontend/config.py`)

- `FASTAPI_BASE_URL` - Backend API URL (default: http://localhost:8000)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

MedAgent-Heart is an educational and informational tool. It should **not** be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## 🙏 Acknowledgments

- **LangGraph** - For the agent framework
- **Groq** - For fast LLM inference
- **Pinecone** - For vector database
- **Tavily** - For web search capabilities
- **Streamlit** - For the beautiful UI framework
- **FastAPI** - For the robust backend framework

## 📧 Contact

- **Author:** Angad — [@angad2803](https://github.com/angad2803)
- **Repository:** [angad2803/MedAgent-Heart](https://github.com/angad2803/MedAgent-Heart)
- **Contributors:** Surya Kant Tiwari — [@SuryaKTiwari11](https://github.com/SuryaKTiwari11)

Have feedback or found an issue? Please open an issue or submit a pull request on the repository: https://github.com/angad2803/MedAgent-Heart/issues

License: MIT
</br>

---

<div align="center">
  Made with ❤️ for better cardiac health awareness
</div>
