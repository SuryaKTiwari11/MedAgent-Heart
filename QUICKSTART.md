# 🚀 Quick Start Guide - MedAgent-Heart

## Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] Conda or virtualenv installed
- [ ] API keys obtained (Groq, Pinecone, Tavily)

## Step-by-Step Setup

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/angad2803/MedAgent-Heart.git
cd MedAgent-Heart

# Create conda environment
conda create -n medagent python=3.11 -y
conda activate medagent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create `.env` file in `backend/` directory:

```bash
# backend/.env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
PINECONE_API_KEY=pcsk_xxxxxxxxxxxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=langgraph-rag-index
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxx
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Get your API keys:**

- Groq: https://console.groq.com/
- Pinecone: https://www.pinecone.io/
- Tavily: https://tavily.com/

### 3. Start the Servers

**Option A: Using Two Terminals (Recommended)**

**Terminal 1 - Backend:**

```bash
cd backend
conda activate medagent
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**

```bash
conda activate medagent
streamlit run frontend/app.py
```

**Option B: Windows - Full Path Method**

**Terminal 1 - Backend:**

```bash
cd backend
D:\anaconda3\envs\medagent\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**

```bash
D:\anaconda3\envs\medagent\python.exe -m streamlit run frontend\app.py
```

### 4. Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 5. Upload Sample Document

1. Open the frontend at http://localhost:8501
2. Click on "📤 Upload New Document"
3. Upload the sample PDF from `dataForRag/heart_dieasespdf.pdf`
4. Wait for confirmation message

### 6. Start Chatting!

Try these sample questions:

- "What are the main types of heart diseases?"
- "How can I prevent heart disease?"
- "What are the symptoms of a heart attack?"
- "What treatments are available for coronary artery disease?"

## Troubleshooting

### Backend won't start

- ✅ Check if port 8000 is already in use
- ✅ Verify all API keys are in `.env` file
- ✅ Make sure conda environment is activated

### Frontend won't start

- ✅ Check if port 8501 is already in use
- ✅ Ensure backend is running first
- ✅ Verify `FASTAPI_BASE_URL` in `frontend/config.py`

### Connection errors

- ✅ Ensure both servers are running
- ✅ Check firewall settings
- ✅ Verify URLs in browser console

### Model errors

- ✅ Verify Groq API key is valid
- ✅ Check if you have Groq API credits
- ✅ Ensure using supported model (llama-3.3-70b-versatile)

## Testing

Run the test suite to verify everything works:

```bash
# Quick functionality test
python quick_test.py

# Comprehensive test
python final_test.py
```

Expected output:

```
✅ Health check: {'status': 'ok'}
✅ Status: 200
✅ ALL TESTS COMPLETED SUCCESSFULLY!
```

## Next Steps

1. **Upload more documents** - Add your own medical PDFs to expand the knowledge base
2. **Customize settings** - Toggle web search on/off based on your needs
3. **Explore API** - Visit http://localhost:8000/docs for interactive API documentation
4. **Check workflow trace** - Expand the trace section to see how the agent processes queries

## Need Help?

- 📖 Read the full [README.md](README.md)
- 🐛 Report issues on [GitHub Issues](https://github.com/angad2803/MedAgent-Heart/issues)
- 💡 Check the [API documentation](http://localhost:8000/docs) when servers are running

---

Happy chatting! 🫀💙
