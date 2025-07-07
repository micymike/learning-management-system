# Multi-Agent System Architecture

## Overview
The AI-Powered Student Repo Grader now uses a multi-agent system where specialized agents handle different aspects of the grading process.

## Agents

### 1. CSVAgent
- **Purpose**: Process CSV/Excel files containing student data
- **Input**: File content and metadata
- **Output**: Structured student data (name, repo_url)

### 2. RepoAgent  
- **Purpose**: Clone and analyze GitHub repositories
- **Input**: Repository URL and student name
- **Output**: Extracted code content

### 3. GradingAgent
- **Purpose**: Assess code against rubric using AI
- **Input**: Code and rubric
- **Output**: Scores and justifications per criterion

### 4. AIDetectionAgent
- **Purpose**: Detect AI-generated code patterns
- **Input**: Code content
- **Output**: AI percentage estimate and indicators

### 5. ReportAgent
- **Purpose**: Generate Excel reports and summaries
- **Input**: All assessment results
- **Output**: Formatted Excel file and summary statistics

### 6. AgentOrchestrator
- **Purpose**: Coordinate all agents and manage workflow
- **Features**: 
  - Concurrent processing of multiple students
  - Error handling and recovery
  - Result aggregation

## Benefits

1. **Scalability**: Agents can process students concurrently
2. **Modularity**: Each agent has a single responsibility
3. **Fault Tolerance**: Individual agent failures don't crash the system
4. **Extensibility**: New agents can be added easily
5. **Performance**: Parallel processing reduces total time

## Usage

```python
from agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
result = await orchestrator.process_assessment(csv_data, rubric)
```

## API Endpoints

- `POST /api/process-with-agents` - Process CSV with multi-agent system
- `GET /api/download-agent-report` - Download generated Excel report  
- `GET /api/agent-status` - Check status of all agents