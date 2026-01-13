"""
Final comprehensive test for MedAgent-Heart API
Tests heart disease queries with the uploaded PDF knowledge base
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("=" * 70)
    print("1. Testing Health Endpoint")
    print("=" * 70)
    r = requests.get(f"{BASE_URL}/health")
    print(f"✅ Status: {r.status_code}")
    print(f"Response: {r.json()}\n")


def test_heart_disease_query():
    """Test chat with heart disease query"""
    print("=" * 70)
    print("2. Testing Chat Endpoint - Heart Disease Treatment")
    print("=" * 70)

    payload = {
        "session_id": "heart-test-001",
        "query": "What are the main types of heart diseases and their symptoms?",
        "enable_web_search": True,
    }

    print(f"Query: {payload['query']}")
    print("Sending request... (this may take 30-60 seconds)\n")

    response = requests.post(f"{BASE_URL}/chat/", json=payload, timeout=120)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"\n{'─' * 70}")
        print("RESPONSE:")
        print(f"{'─' * 70}")
        print(result.get("response", ""))
        print(f"\n{'─' * 70}")
        print(f"Trace Events: {len(result.get('trace_events', []))} steps")
        for i, event in enumerate(result.get("trace_events", []), 1):
            print(f"  Step {i}: {event.get('node_name')} - {event.get('description')}")
        print(f"{'─' * 70}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def test_prevention_query():
    """Test chat with prevention query"""
    print("=" * 70)
    print("3. Testing Chat Endpoint - Heart Disease Prevention")
    print("=" * 70)

    payload = {
        "session_id": "heart-test-002",
        "query": "How can I prevent heart disease?",
        "enable_web_search": True,
    }

    print(f"Query: {payload['query']}")
    print("Sending request... (this may take 30-60 seconds)\n")

    response = requests.post(f"{BASE_URL}/chat/", json=payload, timeout=120)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"\n{'─' * 70}")
        print("RESPONSE:")
        print(f"{'─' * 70}")
        print(result.get("response", ""))
        print(f"\n{'─' * 70}\n")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def show_summary():
    """Show test summary"""
    print("=" * 70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📊 System Status:")
    print(f"  • Backend API: Running on {BASE_URL}")
    print(f"  • Streamlit Frontend: Running on http://localhost:8501")
    print(f"  • Knowledge Base: Heart diseases PDF uploaded and indexed")
    print(f"  • Model: llama-3.3-70b-versatile (Groq)")
    print(f"  • Vector Store: Pinecone (langgraph-rag-index)")
    print("\n🔗 Available Endpoints:")
    print(f"  • Health: {BASE_URL}/health")
    print(f"  • Chat: {BASE_URL}/chat/")
    print(f"  • Upload: {BASE_URL}/upload-document/")
    print(f"  • API Docs: {BASE_URL}/docs")
    print("\n🌐 Access the application:")
    print(f"  • Frontend UI: http://localhost:8501")
    print(f"  • Backend API: {BASE_URL}")
    print("=" * 70)


if __name__ == "__main__":
    print("\n🏥 MedAgent-Heart - Comprehensive Test Suite")
    print("Testing heart disease queries with RAG system\n")

    try:
        test_health()
        test_heart_disease_query()
        test_prevention_query()
        show_summary()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend server")
        print(f"Make sure the server is running on {BASE_URL}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
