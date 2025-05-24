"""
AI Assessor module that uses RAG to evaluate code submissions
"""
import os
import json
from dotenv import load_dotenv
from rag_trainer import RAGTrainer
from langchain_openai import OpenAI

# Load environment variables
load_dotenv()

class AIAssessor:
    def __init__(self, index_name="directed"):
        """Initialize the AI Assessor with RAG capabilities"""
        # Initialize the RAG system
        self.rag = RAGTrainer(index_name)
        self.llm = OpenAI(temperature=0.2)
        
    def assess_submission(self, code, assignment_type=None):
        """
        Assess a code submission using RAG
        
        Args:
            code: The code submission to assess
            assignment_type: Optional assignment type to help find relevant rubrics
            
        Returns:
            Dictionary with assessment scores and feedback
        """
        # Find relevant rubrics
        rubric_results = self.rag.query(
            query_text=code,
            filter_type="rubric",
            top_k=1
        )
        
        if not rubric_results:
            return {"error": "No matching rubric found"}
        
        # Get the best matching rubric
        best_rubric_doc, rubric_metadata, _ = rubric_results[0]
        
        # Find similar examples
        example_results = self.rag.query(
            query_text=code,
            filter_type="example",
            top_k=3
        )
        
        # Extract examples for context
        examples = []
        for doc, metadata, _ in example_results:
            examples.append(doc)
        
        # Create prompt for LLM
        prompt = f"""
        You are an expert code assessor. Assess the following code submission based on the rubric.
        
        RUBRIC:
        {best_rubric_doc}
        
        CODE SUBMISSION:
        {code}
        
        SIMILAR EXAMPLES (for reference):
        {examples[:2] if examples else 'No similar examples found.'}
        
        Provide a detailed assessment with scores for each rubric criterion and specific feedback.
        Format your response as a JSON object with 'scores' and 'feedback' keys.
        """
        
        # Get assessment from LLM
        assessment_text = self.llm.invoke(prompt)
        
        try:
            # Try to parse as JSON
            assessment = json.loads(assessment_text)
            return assessment
        except:
            # If parsing fails, return the raw text
            return {
                "scores": {},
                "feedback": assessment_text,
                "rubric_used": rubric_metadata.get("rubric_id", "unknown")
            }
    
    def get_rubrics(self):
        """Get all available rubrics"""
        results = self.rag.vectorstore.similarity_search_with_score(
            query="list all rubrics",
            k=100,
            filter={"type": "rubric"}
        )
        
        rubrics = []
        for doc, metadata, _ in results:
            rubrics.append({
                "id": metadata.get("rubric_id", "unknown"),
                "text": doc
            })
        
        return rubrics

if __name__ == "__main__":
    # Simple test
    assessor = AIAssessor()
    
    # Test code
    test_code = """
    def fibonacci(n):
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        
        return fib
    
    print(fibonacci(10))
    """
    
    result = assessor.assess_submission(test_code)
    print(json.dumps(result, indent=2))