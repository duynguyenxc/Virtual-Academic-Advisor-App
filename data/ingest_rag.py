import os
import json
import logging
from typing import List, Dict

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv

# Re-load env to ensure GOOGLE_API_KEY is picked up
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Import DB URL
from app.core.database import DATABASE_URL

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
COLLECTION_NAME = "olemiss_knowledge_base"
# Google's latest embedding model
EMBEDDING_MODEL_NAME = "models/text-embedding-004" 
DATA_FILE = os.path.join(os.path.dirname(__file__), "olemiss_data.jsonl")

def load_documents() -> List[Document]:
    logger.info(f"Loading data from {DATA_FILE}...")
    docs = []
    if not os.path.exists(DATA_FILE):
        logger.error("Data file not found!")
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                # Skip duplicate/empty content
                text = item.get("text_clean", "")
                if not text or len(text) < 50:
                    continue
                
                # Metadata
                metadata = {
                    "source": item.get("source") or item.get("url"),
                    "title": item.get("title"),
                    "page_type": item.get("page_type"),
                    "catalog_year": item.get("catalog_year")
                }
                
                docs.append(Document(page_content=text, metadata=metadata))
            except json.JSONDecodeError:
                continue
    
    logger.info(f"Loaded {len(docs)} documents.")
    return docs

def chunk_documents(docs: List[Document]) -> List[Document]:
    logger.info("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    logger.info(f"Created {len(chunks)} chunks.")
    return chunks

def ingest_vectors():
    # 1. Load Data
    raw_docs = load_documents()
    if not raw_docs:
        return
    
    # 2. Chunk Data
    chunks = chunk_documents(raw_docs)
    
    # 3. Create Embeddings (Google Gemini)
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logger.error("GOOGLE_API_KEY not found in environment!")
        return

    logger.info(f"Initializing Embedding Model: {EMBEDDING_MODEL_NAME} with Google API.")
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=google_api_key
    )
    
    # 4. Store in PGVector
    logger.info(f"Connecting to PGVector at: {DATABASE_URL.replace(':' + DATABASE_URL.split(':')[-1].split('@')[0], ':****')}") # Mask password
    
    connection_string = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

    try:
        # Re-create the collection (this handles overwrite/append, but for clean start we assume it's fine)
        # Note: If dimensions differ (Google is 768 vs MiniLM 384), this MIGHT error on existing table.
        # Best practice: Drop table first if switching models, but PGVector might handle it if collection name is same but table structure... 
        # Actually, PGVector implementation stores vectors in `langchain_pg_embedding`. 
        # If we switch dimensions, we MUST drop the table or use a different collection name.
        # Strategy: Use a NEW collection name to be safe.
        
        NEW_COLLECTION_NAME = "olemiss_knowledge_base_gemini"
        
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=NEW_COLLECTION_NAME,
            connection=connection_string,
            use_jsonb=True,
        )
        
        # Add documents (chunks)
        logger.info(f"Adding documents to vector store '{NEW_COLLECTION_NAME}'...")
        vector_store.add_documents(chunks)
        logger.info("Successfully ingested vectors with Google Gemini!")
        
    except Exception as e:
        logger.error(f"Failed to ingest vectors: {e}")

if __name__ == "__main__":
    ingest_vectors()
