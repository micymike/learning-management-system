"""
Simplified version of RAG trainer that doesn't require Google Drive API
"""
import os
import json
import pandas as pd
import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from dotenv import load_dotenv
import requests
import io

# Load environment variables
load_dotenv()

# Initialize Pinecone
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV")
)

class SimplifiedRAGTrainer:
    def __init__(self, index_name="code-assessment"):
        self.embeddings = OpenAIEmbeddings()
        self.index_name = index_name
        
        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine"
            )
        
        # Initialize vector store
        self.vectorstore = Pinecone.from_existing_index(
            index_name=index_name,
            embedding=self.embeddings
        )
    
    def add_rubric(self, rubric_text, rubric_id=None):
        """Add rubric to the vector store"""
        metadata = {"type": "rubric"}
        if rubric_id:
            metadata["rubric_id"] = rubric_id
            
        self.vectorstore.add_texts(
            texts=[rubric_text],
            metadatas=[metadata]
        )
        print(f"Added rubric to Pinecone (ID: {rubric_id})")
    
    def add_assessment_example(self, code, rubric, scores, example_id=None):
        """Add an example assessment to the vector store"""
        # Create a combined document with code, rubric and expected scores
        example_text = f"CODE EXAMPLE:\n{code[:1000]}...\n\nRUBRIC:\n{rubric}\n\nSCORES:\n{json.dumps(scores, indent=2)}"
        
        metadata = {
            "type": "example",
            "has_scores": True
        }
        if example_id:
            metadata["example_id"] = example_id
            
        self.vectorstore.add_texts(
            texts=[example_text],
            metadatas=[metadata]
        )
        print(f"Added assessment example to Pinecone (ID: {example_id})")
    
    def download_google_sheet(self, url):
        """Download a Google Sheet as CSV using the export URL pattern"""
        # Extract sheet ID and gid from URL
        sheet_id = None
        gid = '0'
        
        # Extract sheet ID
        if '/d/' in url:
            parts = url.split('/d/')
            if len(parts) > 1:
                sheet_id = parts[1].split('/')[0]
        
        # Extract gid
        if 'gid=' in url:
            gid = url.split('gid=')[1].split('&')[0].split('#')[0]
        
        if not sheet_id:
            print(f"Could not extract sheet ID from URL: {url}")
            return None
        
        # Construct export URL
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        
        try:
            response = requests.get(export_url)
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text))
        except Exception as e:
            print(f"Error downloading sheet: {e}")
            return None