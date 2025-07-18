import asyncio
from typing import Dict, Any, List
from .csv_agent import CSVAgent
from .repo_agent import RepoAgent
from .grading_agent import GradingAgent
from .ai_detection_agent import AIDetectionAgent
from .report_agent import ReportAgent
from .vector_agent import VectorAgent
from .batch_agent import BatchAgent
from .graph_rag_agent import GraphRAGAgent
from .consistency_agent import ConsistencyAgent

class AgentOrchestrator:
    def __init__(self):
        self.csv_agent = CSVAgent()
        self.repo_agent = RepoAgent()
        self.grading_agent = GradingAgent()
        self.ai_detection_agent = AIDetectionAgent()
        self.report_agent = ReportAgent()
        self.vector_agent = VectorAgent()
        self.batch_agent = BatchAgent()
        self.graph_rag_agent = GraphRAGAgent()
        self.consistency_agent = ConsistencyAgent()
        
    async def process_assessment(self, csv_data: Dict[str, Any], rubric: str) -> Dict[str, Any]:
        try:
            # Step 1: Process CSV
            csv_result = await self.csv_agent.process(csv_data)
            if 'error' in csv_result:
                return {'error': f"CSV processing failed: {csv_result['error']}"}
            
            students = csv_result['students']
            
            # Step 2: Collect repository data
            repo_tasks = []
            for student in students:
                task = self.repo_agent.process({
                    'repo_url': student.get('repo_url'),
                    'student_name': student.get('name')
                })
                repo_tasks.append(task)
            
            repo_results = await asyncio.gather(*repo_tasks, return_exceptions=True)
            print("=== DEBUG: repo_results ===")
            import pprint
            pprint.pprint(repo_results)
            print("=== END DEBUG ===")
            # Step 3: Build knowledge graph and store in vector DB
            valid_students = []
            for result in repo_results:
                if not isinstance(result, Exception) and result.get('code'):
                    valid_students.append(result)
                    # Store in vector database for context
                    await self.vector_agent.process({
                        'action': 'store',
                        'student_name': result.get('student_name'),
                        'code': result.get('code'),
                        'metadata': {'repo_url': result.get('repo_url')}
                    })
                else:
                    print("Skipping student due to missing code or error:", result)
            
            # Build knowledge graph
            await self.graph_rag_agent.process({
                'action': 'build_graph',
                'students': valid_students
            })
            
            # Step 4: Use batch processing for grading (50% token reduction)
            batch_result = await self.batch_agent.process({
                'students': valid_students,
                'rubric': rubric,
                'api_type': 'openai'
            })
            
            # Step 5: Run consistency checks
            consistency_tasks = []
            for student in valid_students[:3]:  # Check first 3 for consistency
                task = self.consistency_agent.process({
                    'code': student.get('code'),
                    'rubric': rubric,
                    'student_name': student.get('student_name')
                })
                consistency_tasks.append(task)
            
            consistency_results = await asyncio.gather(*consistency_tasks, return_exceptions=True)
            
            # Step 6: Generate enhanced report
            report_result = await self.report_agent.process({
                'results': batch_result.get('results', []),
                'consistency_metrics': consistency_results,
                'rubric': rubric
            })
            
            return {
                'results': batch_result.get('results', []),
                'report': report_result,
                'consistency_metrics': consistency_results,
                'summary': report_result.get('summary', {}),
                'status': 'completed'
            }
            
        except Exception as e:
            return {'error': f"Orchestration failed: {str(e)}"}
    
    async def _process_student(self, student: Dict[str, Any], rubric: str) -> Dict[str, Any]:
        student_name = student.get('name')
        repo_url = student.get('repo_url')
        
        try:
            # Step 1: Analyze repository
            repo_data = {
                'repo_url': repo_url,
                'student_name': student_name
            }
            repo_result = await self.repo_agent.process(repo_data)
            
            if repo_result.get('status') == 'error':
                return {
                    'student_name': student_name,
                    'repo_url': repo_url,
                    'error': repo_result.get('error'),
                    'status': 'repo_error'
                }
            
            code = repo_result.get('code', '')
            
            # Step 2: Run grading and AI detection concurrently
            grading_task = self.grading_agent.process({
                'code': code,
                'rubric': rubric,
                'student_name': student_name
            })
            
            ai_detection_task = self.ai_detection_agent.process({
                'code': code,
                'student_name': student_name
            })
            
            grading_result, ai_result = await asyncio.gather(
                grading_task, ai_detection_task, return_exceptions=True
            )
            
            # Combine results
            final_result = {
                'student_name': student_name,
                'repo_url': repo_url,
                'status': 'completed'
            }
            
            if isinstance(grading_result, Exception):
                final_result['grading_error'] = str(grading_result)
            else:
                final_result['scores'] = grading_result.get('scores', {})
            
            if isinstance(ai_result, Exception):
                final_result['ai_detection_error'] = str(ai_result)
            else:
                final_result['ai_percentage'] = ai_result.get('ai_percentage', 0)
                final_result['ai_confidence'] = ai_result.get('confidence', 'low')
                final_result['ai_indicators'] = ai_result.get('indicators', [])
            
            return final_result
            
        except Exception as e:
            return {
                'student_name': student_name,
                'repo_url': repo_url,
                'error': str(e),
                'status': 'processing_error'
            }

# === Double Agentic LLM Functions ===

import os
import openai

def process_with_azure_openai(repo, prompt):
    """
    Call Azure OpenAI Chat Completion API with the given prompt and repo context.
    Returns a dict. If a content policy error is encountered, return {'error': 'content_policy'}
    """
    try:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        api_version = os.getenv("OPENAI_API_VERSION", "2023-05-15")
        deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

        if not all([api_key, api_base, api_version, deployment_name]):
            return {"error": "Azure OpenAI environment variables not set properly."}

        client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=api_base,
            api_version=api_version,
        )

        # Compose the message for the chat completion
        messages = [
            {"role": "system", "content": "You are an AI code assistant. Use the repo context to answer the prompt."},
            {"role": "user", "content": f"Repo: {repo}\nPrompt: {prompt}"}
        ]

        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
        )

        # Check for content policy error in response (Azure returns 400 with error details)
        if hasattr(response, "error") and response.error.get("code") == "content_filter":
            return {"error": "content_policy"}

        # Return the response text
        return {"response": response.choices[0].message.content}

    except openai.OpenAIError as e:
        # Check for content policy error
        if hasattr(e, "error") and getattr(e.error, "code", None) == "content_filter":
            return {"error": "content_policy"}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

def process_with_openai(repo, prompt):
    """
    Simulate processing with standard OpenAI.
    Replace this stub with actual OpenAI API logic.
    Returns a dict.
    """
    # TODO: Implement actual OpenAI call
    return {"response": f"OpenAI processed repo: {repo} with prompt: {prompt}"}
