"""
RAG-based code assessment system using ChromaDB for vector storage
and retrieval of rubrics and example assessments.
"""
import os
import json
import re
from urllib.parse import urlparse
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from repo_analyzer import analyze_repo

load_dotenv()

class RAGAssessor:
    def __init__(self, index_name="directed"):
        """Initialize the RAG assessor with ChromaDB vector store"""
        self.embeddings = OpenAIEmbeddings()
        self.index_name = index_name
        
        # Initialize ChromaDB (use same directory as trainer)
        persist_directory = f"./chroma_db/{index_name}"
        
        # Initialize vector store
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name=index_name
        )
        
        # Initialize LLM with increased max_retries
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.2,
            max_retries=3
        )
        
        # Create QA chain
        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}  # Retrieve top 5 most relevant documents
            )
        )
    
    def extract_student_info(self, github_url):
        """Extract student information from GitHub URL"""
        parsed = urlparse(github_url)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2:
            username = path_parts[0]
            repo_name = path_parts[1]
            return {
                "username": username,
                "repo_name": repo_name,
                "github_url": github_url
            }
        return None

    def extract_json_from_response(self, response):
        """Extract JSON from response text, with retries for different formats"""
        # Try to find JSON using regex pattern
        json_pattern = r'\{[^{}]*\{[^{}]*\}[^{}]*\}'  # Matches nested JSON
        match = re.search(json_pattern, response)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        
        # Try to find any JSON-like structure
        try:
            start = response.find('{')
            if start != -1:
                # Find matching closing brace
                count = 1
                for i in range(start + 1, len(response)):
                    if response[i] == '{':
                        count += 1
                    elif response[i] == '}':
                        count -= 1
                    if count == 0:
                        json_str = response[start:i+1]
                        return json.loads(json_str)
        except:
            pass

        # If no JSON found, create a structured response from text
        try:
            # Extract key information using patterns
            mark_match = re.search(r'(\d+(?:\s*-\s*\d+)?(?:\s*marks?)?)', response, re.IGNORECASE)
            level_match = re.search(r'(fully correct|mostly correct|partially correct|incorrect)', response, re.IGNORECASE)
            
            mark = mark_match.group(1) if mark_match else "0"
            level = level_match.group(1) if level_match else "Unable to determine"
            
            # Create structured response
            return {
                "assessment": {
                    "selected_mark": mark,
                    "level_description": level,
                    "justification": response[:500],  # Use first 500 chars as justification
                    "key_observations": [
                        "Assessment generated from unstructured response",
                        "See justification for details"
                    ]
                }
            }
        except:
            raise ValueError("Could not parse assessment response")
    
    def assess_code(self, github_url, rubric):
        """
        Assess code from a GitHub repository using RAG approach
        
        Args:
            github_url (str): URL of the GitHub repository to assess
            rubric (str): The rubric to use for assessment
            
        Returns:
            dict: Dictionary of assessments and scores for each criterion
        """
        try:
            # Get student info from GitHub URL
            student_info = self.extract_student_info(github_url)
            if not student_info:
                raise ValueError(f"Invalid GitHub URL format: {github_url}")
            
            # Analyze GitHub repository
            code = analyze_repo(github_url)
            if not code or code == "No code files found in repo.":
                raise ValueError(f"No code found in repository: {github_url}")
            
            # First, search for similar rubrics to ensure we have context
            similar_docs = self.vectorstore.similarity_search(
                rubric,
                k=2
            )
            
            # Then search for similar examples
            similar_examples = self.vectorstore.similarity_search(
                code[:1000],  # Use first 1000 chars of code for search
                k=3
            )
            
            # Combine the context from similar rubrics and examples
            context = ""
            if similar_docs:
                context += "SIMILAR RUBRICS:\n"
                for i, doc in enumerate(similar_docs):
                    if hasattr(doc.metadata, 'type') and doc.metadata['type'] == 'rubric':
                        context += f"Rubric {i+1}:\n{doc.page_content}\n\n"
            
            if similar_examples:
                context += "SIMILAR EXAMPLES WITH SCORES:\n"
                for i, doc in enumerate(similar_examples):
                    if (hasattr(doc.metadata, 'type') and doc.metadata['type'] == 'example' and
                        hasattr(doc.metadata, 'has_scores') and doc.metadata['has_scores']):
                        context += f"Example {i+1}:\n{doc.page_content}\n\n"
            
            # Parse rubric to extract scoring levels
            main_criterion = None
            scoring_levels = {}
            
            for line in rubric.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Main Criterion:'):
                    main_criterion = line.split(':', 1)[1].strip()
                elif '(No Mark):' in line:
                    mark = '0'
                    description = line.split(':', 1)[1].strip()
                    scoring_levels[mark] = description
                elif 'Marks:' in line:
                    mark = line.split('Marks:', 1)[0].strip()
                    description = line.split(':', 1)[1].strip()
                    scoring_levels[mark] = description
            
            # Create the assessment prompt
            query = f"""
            Assess the code from GitHub repository: {github_url}
            Student: {student_info['username']}
            Repository: {student_info['repo_name']}

            RUBRIC CRITERION:
            {main_criterion}

            AVAILABLE SCORING LEVELS:
            {json.dumps(scoring_levels, indent=2)}
            
            CODE TO ASSESS:
            {code[:5000]}
            
            SIMILAR ASSESSMENTS FOR REFERENCE:
            {context}
            
            Analyze the code and provide your assessment as a JSON object with this structure:
            {{
              "assessment": {{
                "selected_mark": "The exact mark or mark range from the rubric (e.g., '0', '1 - 3', '4 - 8', '10 - 12')",
                "level_description": "Copy the EXACT level description from the rubric that matches this mark",
                "justification": "Detailed explanation of why this mark was chosen",
                "key_observations": [
                  "Specific examples from the code",
                  "That support your scoring decision"
                ]
              }}
            }}
            
            REQUIREMENTS:
            1. Use ONLY the scoring levels defined in the rubric
            2. The mark MUST EXACTLY match one of these: {', '.join(scoring_levels.keys())}
            3. The level description must EXACTLY match one from the rubric
            4. Include specific code examples in your observations
            5. Be strict and accurate in your assessment
            """
            
            # Get response from QA chain
            response = self.qa.run(query)
            
            # Extract and validate JSON from response
            try:
                result = self.extract_json_from_response(response)
                
                # Return the assessment with student info
                return {
                    "student": {
                        "name": student_info["username"],
                        "github_username": student_info["username"],
                        "repository_name": student_info["repo_name"],
                        "repository_url": student_info["github_url"]
                    },
                    "criterion": main_criterion,
                    "mark": result["assessment"]["selected_mark"],
                    "level": result["assessment"]["level_description"],
                    "justification": result["assessment"]["justification"],
                    "observations": result["assessment"]["key_observations"]
                }
            except Exception as e:
                raise ValueError(f"Error parsing assessment response: {str(e)}")
        except Exception as e:
            raise Exception(f"Error assessing repository {github_url}: {str(e)}")

# Singleton instance for use in routes
assessor = None

def get_assessor():
    """Get or create the RAG assessor singleton"""
    global assessor
    if assessor is None:
        assessor = RAGAssessor()
    return assessor
