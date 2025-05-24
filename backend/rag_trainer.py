"""
Script to download rubrics and example outputs from Google Drive and upload them to ChromaDB
for training the RAG-based assessment system.
"""
import os
import json
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
# Make Google Drive API optional
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Google API libraries not installed. Google Drive functionality will be disabled.")
    print("To enable, install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
import io

# Load environment variables
load_dotenv()

class RAGTrainer:
    def __init__(self, index_name="directed"):
        self.embeddings = OpenAIEmbeddings()
        self.index_name = index_name
        
        # Initialize Chroma DB (persistent storage)
        persist_directory = f"./chroma_db/{index_name}"
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize vector store
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=index_name
        )
        
        # Initialize Google Drive API
        self.drive_service = self._init_drive_service()
    
    def _init_drive_service(self):
        """Initialize Google Drive API service"""
        if not GOOGLE_API_AVAILABLE:
            print("Google Drive API not available. Install required packages first.")
            return None
            
        creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
        if not creds_file:
            print("Warning: GOOGLE_CREDENTIALS_FILE not set in .env")
            return None
            
        try:
            creds = Credentials.from_service_account_file(
                creds_file, 
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            print(f"Error initializing Google Drive API: {e}")
            return None
    
    def download_file(self, file_id):
        """Download a file from Google Drive by ID"""
        if not self.drive_service:
            raise ValueError("Google Drive service not initialized")
            
        request = self.drive_service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while not done:
            _, done = downloader.next_chunk()
        
        file_content.seek(0)
        return file_content
    
    def download_from_folder(self, folder_id):
        """Download all files from a Google Drive folder"""
        if not self.drive_service:
            raise ValueError("Google Drive service not initialized")
            
        results = []
        page_token = None
        
        while True:
            response = self.drive_service.files().list(
                q=f"'{folder_id}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token
            ).execute()
            
            for file in response.get('files', []):
                file_id = file.get('id')
                file_name = file.get('name')
                mime_type = file.get('mimeType')
                
                if mime_type == 'application/vnd.google-apps.folder':
                    # Recursively download from subfolders
                    subfolder_results = self.download_from_folder(file_id)
                    results.extend(subfolder_results)
                else:
                    try:
                        content = self.download_file(file_id)
                        results.append({
                            'name': file_name,
                            'content': content,
                            'id': file_id
                        })
                        print(f"Downloaded: {file_name}")
                    except Exception as e:
                        print(f"Error downloading {file_name}: {e}")
            
            page_token = response.get('nextPageToken')
            if not page_token:
                break
                
        return results
    
    def process_rubric_file(self, file_content, file_name):
        """Process a rubric file and extract the text"""
        if file_name.endswith('.txt'):
            return file_content.getvalue().decode('utf-8')
        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_content)
            return '\n'.join(df[df.columns[0]].dropna().astype(str).tolist())
        else:
            return file_content.getvalue().decode('utf-8', errors='ignore')
    
    def process_example_file(self, file_content, file_name):
        """Process an example file with code and expected scores"""
        if file_name.endswith('.json'):
            return json.loads(file_content.getvalue().decode('utf-8'))
        else:
            # Assume it's a text file with a specific format
            content = file_content.getvalue().decode('utf-8', errors='ignore')
            # Parse the content based on your specific format
            # This is a placeholder - adjust based on your actual format
            parts = content.split('---SCORES---')
            if len(parts) >= 2:
                code = parts[0].strip()
                try:
                    scores = json.loads(parts[1].strip())
                    return {'code': code, 'scores': scores}
                except:
                    print(f"Error parsing scores in {file_name}")
            return None
    
    def add_rubric(self, rubric_text, rubric_id=None):
        """Add rubric to the vector store"""
        metadata = {"type": "rubric"}
        if rubric_id:
            metadata["rubric_id"] = rubric_id
            
        self.vectorstore.add_texts(
            texts=[rubric_text],
            metadatas=[metadata]
        )
        print(f"Added rubric to ChromaDB (ID: {rubric_id})")
    
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
        print(f"Added assessment example to ChromaDB (ID: {example_id})")
        
    def query(self, query_text, filter_type=None, top_k=5):
        """
        Query the vector store for similar documents
        
        Args:
            query_text: The text to search for
            filter_type: Optional filter for document type (e.g., "rubric" or "example")
            top_k: Number of results to return
            
        Returns:
            List of (document, metadata, score) tuples
        """
        # Create filter if specified
        filter_dict = None
        if filter_type:
            filter_dict = {"type": filter_type}
            
        # Query the vector store
        results = self.vectorstore.similarity_search_with_score(
            query=query_text,
            k=top_k,
            filter=filter_dict
        )
        
        return results
    
    def bulk_train_from_drive(self, rubrics_folder_id, examples_folder_id):
        """Download rubrics and examples from Google Drive and upload to ChromaDB"""
        # Download rubrics
        print("Downloading rubrics...")
        rubric_files = self.download_from_folder(rubrics_folder_id)
        
        # Download examples
        print("Downloading examples...")
        example_files = self.download_from_folder(examples_folder_id)
        
        # Process rubrics
        rubrics = {}
        for file in rubric_files:
            try:
                rubric_text = self.process_rubric_file(file['content'], file['name'])
                rubric_id = file['name'].split('.')[0]  # Use filename without extension as ID
                rubrics[rubric_id] = rubric_text
                self.add_rubric(rubric_text, rubric_id)
            except Exception as e:
                print(f"Error processing rubric {file['name']}: {e}")
        
        # Process examples
        for file in example_files:
            try:
                example_data = self.process_example_file(file['content'], file['name'])
                if example_data and 'code' in example_data and 'scores' in example_data:
                    # Try to match with a rubric
                    rubric_id = None
                    if 'rubric_id' in example_data:
                        rubric_id = example_data['rubric_id']
                    
                    # If we have the rubric, use it; otherwise use a default
                    rubric_text = rubrics.get(rubric_id, list(rubrics.values())[0] if rubrics else "")
                    
                    self.add_assessment_example(
                        example_data['code'],
                        rubric_text,
                        example_data['scores'],
                        file['name'].split('.')[0]  # Use filename without extension as ID
                    )
            except Exception as e:
                print(f"Error processing example {file['name']}: {e}")
        
        print(f"Training complete: {len(rubrics)} rubrics and {len(example_files)} examples processed")

if __name__ == "__main__":
    # Get folder IDs from environment or command line
    rubrics_folder_id = os.getenv("RUBRICS_FOLDER_ID")
    examples_folder_id = os.getenv("EXAMPLES_FOLDER_ID")
    
    if not rubrics_folder_id or not examples_folder_id:
        print("Please set RUBRICS_FOLDER_ID and EXAMPLES_FOLDER_ID in .env file")
        exit(1)
    
    trainer = RAGTrainer()
    trainer.bulk_train_from_drive(rubrics_folder_id, examples_folder_id)