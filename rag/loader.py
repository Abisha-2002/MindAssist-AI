"""
RAG Pipeline: Load, Chunk, Embed, and Store Documents
"""

import os
import streamlit as st

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Configuration
PERSIST_DIR = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

@st.cache_resource
def get_embeddings():
    """
    Initialize embedding model with proper error handling
    """
    try:
        # Try to import and load the embedding model
        from langchain_huggingface import HuggingFaceEmbeddings
        
        # Set environment variable to avoid downloading issues
        os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
        
        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            cache_folder="./models"  # Local cache folder
        )
    except ImportError:
        # Fallback to sentence-transformers if langchain_huggingface is not installed
        try:
            from sentence_transformers import SentenceTransformer
            from langchain_community.embeddings import HuggingFaceEmbeddings
            
            st.info("🔄 Using sentence-transformers as fallback...")
            
            # Download and cache the model
            model = SentenceTransformer(EMBEDDING_MODEL)
            
            return HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'}
            )
        except Exception as e:
            st.error(f"❌ Failed to load embedding model: {e}")
            st.info("💡 Try running: pip install sentence-transformers")
            return None
    except Exception as e:
        st.error(f"❌ Failed to initialize embeddings: {e}")
        return None

def load_and_chunk_pdfs(pdf_folder="data/pdfs/"):
    """
    Load PDFs and split into chunks
    """
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
        st.warning(f"📁 '{pdf_folder}' folder created. Add PDFs there.")
        return None

    pdf_files = [
        f for f in os.listdir(pdf_folder)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        st.warning(f"⚠️ No PDF files found in '{pdf_folder}'")
        return None

    st.info(f"📚 Loading {len(pdf_files)} PDF files...")

    try:
        loader = PyPDFDirectoryLoader(pdf_folder)
        documents = loader.load()

        if not documents:
            st.error("❌ No documents loaded.")
            return None

        st.info(f"📄 Loaded {len(documents)} pages.")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        chunks = text_splitter.split_documents(documents)
        st.info(f"✂️ Created {len(chunks)} chunks.")

        return chunks

    except Exception as e:
        st.error(f"❌ Failed to load PDFs: {e}")
        return None

@st.cache_resource
def get_vector_store():
    """
    Create or load Chroma vector database
    """
    embeddings = get_embeddings()
    
    if embeddings is None:
        st.error("❌ Embedding model failed to load. Cannot create vector database.")
        return None

    # Load existing database
    if os.path.exists(PERSIST_DIR) and os.path.isdir(PERSIST_DIR):
        try:
            vectordb = Chroma(
                persist_directory=PERSIST_DIR,
                embedding_function=embeddings
            )

            # Check if collection exists and has documents
            try:
                count = vectordb._collection.count()
                if count > 0:
                    st.success(f"✅ Loaded vector DB ({count} chunks)")
                    return vectordb
            except:
                pass  # Collection might not exist yet
        except Exception as e:
            st.warning(f"Database loading issue: {e}. Rebuilding...")

    # Create new database
    chunks = load_and_chunk_pdfs()

    if not chunks:
        st.error("❌ No PDF chunks available.")
        return None

    st.info("🔄 Creating Chroma vector database...")

    try:
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=PERSIST_DIR
        )

        st.success(f"✅ Vector DB created with {len(chunks)} chunks")
        return vectordb

    except Exception as e:
        st.error(f"❌ Vector database error: {e}")
        return None

def query_retrieval(query, k=5):
    """
    Retrieve relevant document chunks
    """
    vectordb = get_vector_store()

    if vectordb is None:
        return []

    try:
        results = vectordb.similarity_search_with_score(
            query,
            k=k
        )
        return results

    except Exception as e:
        st.error(f"❌ Retrieval failed: {e}")
        return []

# Sample queries for evaluation
SAMPLE_QUERIES = [
    "What is PHQ-9 and how is it scored?",
    "What machine learning techniques are used for depression prediction?",
    "What is the prevalence of depression in Sri Lanka?",
    "What are depression risk factors among university students?",
    "How does DASS-21 differ from PHQ-9?"
]

def evaluate_retrieval():
    """
    Evaluate RAG retrieval performance
    """
    results = {}

    for query in SAMPLE_QUERIES:
        retrieved = query_retrieval(query, k=3)

        results[query] = {
            "num_results": len(retrieved),
            "top_score": retrieved[0][1] if retrieved else None,
            "top_content": retrieved[0][0].page_content[:200] + "..." if retrieved else "No results"
        }

    return results