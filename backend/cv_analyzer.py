"""
CV Analyzer module that uses RAG to evaluate resumes against job descriptions
"""
import os
import json
from dotenv import load_dotenv
from rag_trainer import RAGTrainer
from langchain_openai import OpenAI

# Load environment variables
load_dotenv()

class CVAnalyzer:
    def __init__(self, index_name="cv_analysis"):
        """Initialize the CV Analyzer with RAG capabilities"""
        # Initialize the RAG system
        self.rag = RAGTrainer(index_name)
        self.llm = OpenAI(temperature=0.2)
    
    def analyze_cv(self, cv_text, job_description):
        """
        Analyze a CV against a job description using RAG
        
        Args:
            cv_text: The CV/resume text
            job_description: The job description to match against
            
        Returns:
            Dictionary with analysis results
        """
        # Combine CV and job description for context
        query = f"CV: {cv_text[:500]}...\nJob: {job_description[:500]}..."
        
        # Find relevant examples
        results = self.rag.query(query, top_k=5)
        
        # Extract examples for context
        examples = []
        for doc, metadata, _ in results:
            examples.append(doc)
        
        # Create prompt for LLM
        prompt = f"""
        You are an expert CV/resume analyzer. Analyze the following CV against the job description.
        
        JOB DESCRIPTION:
        {job_description}
        
        CV/RESUME:
        {cv_text}
        
        SIMILAR EXAMPLES (for reference):
        {examples[:2] if examples else 'No similar examples found.'}
        
        Provide a detailed analysis with:
        1. Match score (0-100%)
        2. Key strengths
        3. Missing skills or experience
        4. Recommendations for improvement
        
        Format your response as a JSON object with 'match_score', 'strengths', 'gaps', and 'recommendations' keys.
        """
        
        # Get analysis from LLM
        analysis_text = self.llm.invoke(prompt)
        
        try:
            # Try to parse as JSON
            analysis = json.loads(analysis_text)
            return analysis
        except:
            # If parsing fails, return the raw text
            return {
                "match_score": 0,
                "analysis": analysis_text
            }
    
    def add_example(self, cv_text, job_description, match_score, feedback):
        """
        Add an example CV analysis to the RAG system
        
        Args:
            cv_text: The CV/resume text
            job_description: The job description
            match_score: The match score (0-100%)
            feedback: Feedback on the match
            
        Returns:
            None
        """
        # Create a combined document
        example_text = f"JOB DESCRIPTION:\n{job_description}\n\nCV:\n{cv_text}\n\nMATCH SCORE: {match_score}%\n\nFEEDBACK:\n{feedback}"
        
        # Add to ChromaDB
        self.rag.vectorstore.add_texts(
            texts=[example_text],
            metadatas=[{"type": "cv_example", "match_score": match_score}]
        )

if __name__ == "__main__":
    # Simple test
    analyzer = CVAnalyzer()
    
    # Test CV and job description
    test_cv = """
    John Doe
    Software Engineer
    
    Experience:
    - 5 years Python development
    - 3 years AWS cloud infrastructure
    - 2 years machine learning projects
    
    Education:
    - BS Computer Science, University of Example
    """
    
    test_job = """
    Senior Python Developer
    
    Requirements:
    - 5+ years Python experience
    - Experience with cloud platforms (AWS preferred)
    - Knowledge of machine learning frameworks
    - Experience with database design
    """
    
    result = analyzer.analyze_cv(test_cv, test_job)
    print(json.dumps(result, indent=2))