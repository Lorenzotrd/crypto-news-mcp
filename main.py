from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(title="Crypto News API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from environment variable
API_KEY = os.getenv("NEWS_API_KEY")
if not API_KEY:
    raise ValueError("NEWS_API_KEY not found in environment variables. Please set it.")
BASE_URL = "https://newsdata.io/api/1/crypto"

# Helper function to fetch news from the API with nextPage pagination
async def fetch_crypto_news(query: str = None, max_pages: int = 1) -> List[Dict[str, Any]]:
    all_articles = []
    next_page = None  # Start with no page token for the first request
    
    async with httpx.AsyncClient() as client:
        params = {
            "apikey": API_KEY,
        }
        if query:
            params["q"] = query
        
        # Fetch up to max_pages
        for _ in range(max_pages):
            if next_page:
                params["page"] = next_page  # Use nextPage token from previous response
            
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()  # Raise an exception for bad responses
            
            data = response.json()
            articles = data.get("results", [])
            all_articles.extend(articles)
            
            # Get the nextPage token from the response
            next_page = data.get("nextPage")
            
            # Stop if there's no nextPage or no more articles
            if not next_page or not articles:
                break
        
        return all_articles

@app.get("/get_latest_news")
async def get_latest_news():
    """
    Fetch the latest cryptocurrency news headlines.
    """
    articles = await fetch_crypto_news()
    headlines = [
        {
            "title": article["title"],
            "published": article["pubDate"],
            "description": article.get("description", "No description available")
        }
        for article in articles
    ]
    return {"status": "success", "data": headlines}

@app.get("/get_crypto_news")
async def get_crypto_news(query: str, max_pages: int = 1):
    """
    Fetch news articles for a specific cryptocurrency or topic with pagination support.
    """
    articles = await fetch_crypto_news(query=query, max_pages=max_pages)
    
    if not articles:
        return {"status": "error", "message": f"No news found for query '{query}'."}
    
    result = [
        {
            "title": article["title"],
            "published": article["pubDate"],
            "description": article.get("description", "No description available")
        }
        for article in articles
    ]
    return {"status": "success", "data": result}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
