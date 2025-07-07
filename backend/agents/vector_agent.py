from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any, List
import chromadb
import os

class VectorAgent(BaseAgent):
    def __init__(self):
        super().__init__("vector_agent")
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection("code_context")
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            action = data.get('action')
            
            if action == 'store':
                return await self._store_context(data)
            elif action == 'retrieve':
                return await self._retrieve_context(data)
            else:
                raise ValueError("Invalid action")
                
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {'error': str(e)}
    
    async def _store_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        student_name = data.get('student_name')
        code = data.get('code')
        metadata = data.get('metadata', {})
        
        self.collection.add(
            documents=[code],
            metadatas=[{**metadata, 'student': student_name}],
            ids=[f"{student_name}_{hash(code)}"]
        )
        
        return {'status': 'stored', 'student': student_name}
    
    async def _retrieve_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        query = data.get('query')
        n_results = data.get('n_results', 3)
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return {
            'documents': results['documents'][0],
            'metadatas': results['metadatas'][0],
            'distances': results['distances'][0]
        }