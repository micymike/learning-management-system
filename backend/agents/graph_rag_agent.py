from .base_agent import BaseAgent, AgentStatus
from typing import Dict, Any, List
import networkx as nx
import json

class GraphRAGAgent(BaseAgent):
    def __init__(self):
        super().__init__("graph_rag_agent")
        self.knowledge_graph = nx.DiGraph()
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            action = data.get('action')
            
            if action == 'build_graph':
                return await self._build_knowledge_graph(data)
            elif action == 'query_graph':
                return await self._query_knowledge_graph(data)
            else:
                raise ValueError("Invalid action")
                
        except Exception as e:
            self.status = AgentStatus.ERROR
            return {'error': str(e)}
    
    async def _build_knowledge_graph(self, data: Dict[str, Any]) -> Dict[str, Any]:
        students_data = data.get('students', [])
        
        for student in students_data:
            student_name = student.get('name')
            code = student.get('code', '')
            
            # Add student node
            self.knowledge_graph.add_node(student_name, type='student')
            
            # Extract code patterns and create relationships
            patterns = self._extract_code_patterns(code)
            for pattern in patterns:
                pattern_id = f"pattern_{hash(pattern)}"
                self.knowledge_graph.add_node(pattern_id, type='pattern', content=pattern)
                self.knowledge_graph.add_edge(student_name, pattern_id, relation='uses')
        
        return {'nodes': len(self.knowledge_graph.nodes), 'edges': len(self.knowledge_graph.edges)}
    
    async def _query_knowledge_graph(self, data: Dict[str, Any]) -> Dict[str, Any]:
        student_name = data.get('student_name')
        
        if student_name not in self.knowledge_graph:
            return {'similar_students': [], 'common_patterns': []}
        
        # Find similar students based on shared patterns
        student_patterns = set(self.knowledge_graph.successors(student_name))
        similar_students = []
        
        for node in self.knowledge_graph.nodes:
            if self.knowledge_graph.nodes[node].get('type') == 'student' and node != student_name:
                other_patterns = set(self.knowledge_graph.successors(node))
                similarity = len(student_patterns & other_patterns) / len(student_patterns | other_patterns)
                if similarity > 0.3:
                    similar_students.append({'name': node, 'similarity': similarity})
        
        return {
            'similar_students': sorted(similar_students, key=lambda x: x['similarity'], reverse=True),
            'common_patterns': list(student_patterns)
        }
    
    def _extract_code_patterns(self, code: str) -> List[str]:
        patterns = []
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('def '):
                patterns.append(f"function_{line.split('(')[0].replace('def ', '')}")
            elif line.startswith('class '):
                patterns.append(f"class_{line.split(':')[0].replace('class ', '')}")
            elif 'import ' in line:
                patterns.append(f"import_{line.replace('import ', '').replace('from ', '')}")
        
        return patterns