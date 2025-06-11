# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with actual API keys (ANTHROPIC_API_KEY and OPENAI_API_KEY)
```

### Running the Application
```bash
# Start the FastAPI server
python main.py

# Start with explicit environment variables (if .env not loading)
export ANTHROPIC_API_KEY="your_key" && export OPENAI_API_KEY="your_key" && python main.py

# Check if server is running
lsof -i:8000

# Kill server on port 8000
lsof -ti:8000 | xargs kill -9
```

### Testing API Endpoints
```bash
# Test idea generation
curl -X POST http://localhost:8000/api/generate-ideas \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test prompt","num_ideas":2,"context":{"idea_type":"creative"}}'

# Test validation
curl -X POST http://localhost:8000/api/validate-idea \
  -H "Content-Type: application/json" \
  -d '{"idea":{"title":"Test","description":"Test idea"},"session_id":"test123"}'

# Test PRD creation
curl -X POST http://localhost:8000/api/create-prd \
  -H "Content-Type: application/json" \
  -d '{"idea":{"title":"Test"},"validation_data":{"overall_score":8.5},"session_id":"test123"}'

# Check system status
curl http://localhost:8000/api/status
```

## Architecture Overview

### Multi-Agent System Architecture
FreshAgentLab implements a claude-flow inspired multi-agent system without ADK framework dependencies:

- **OrchestratorAgent**: Coordinates workflow execution and manages sessions. Initializes and coordinates all sub-agents through predefined workflow templates (`full_pipeline`, `idea_generation`, `validation_only`).

- **IdeaCoachAgent**: Generates ideas using different prompt templates based on idea type (creative, business, product). Each type has specialized prompts optimized for different use cases.

- **ValidationAgent**: Performs comprehensive idea validation including market analysis, competitive analysis, technical feasibility, and financial assessment. Generates validation scores and actionable recommendations.

- **ProductManagerAgent**: Creates detailed Product Requirements Documents (PRDs) with executive summaries, technical requirements, timelines, success metrics, and risk assessments.

### Agent Communication Pattern
All agents inherit from `BaseAgent` which provides:
- AI client management (Anthropic Claude and OpenAI)
- Performance metrics tracking
- Status management
- Environment variable loading from project root

### Data Flow
1. **Request**: FastAPI receives request with prompt, idea type, and workflow type
2. **Orchestration**: OrchestratorAgent creates session and executes workflow steps
3. **Agent Execution**: Each agent processes its step and returns structured results
4. **Response Processing**: Main.py extracts nested results and returns proper API response format
5. **Frontend Display**: Static HTML/JS renders results with appropriate field mapping

### Critical Implementation Details

#### Environment Variable Loading
The `.env` file must be in project root. BaseAgent loads it explicitly:
```python
load_dotenv(Path(__file__).parent.parent / '.env')
```

#### API Response Structure Handling
The orchestrator returns nested workflow results. Main.py must extract actual agent results:
```python
# Extract ideas from nested structure
if ideas and len(ideas) > 0:
    if isinstance(ideas[0], dict) and "business_ideas" in ideas[0]:
        actual_ideas = ideas[0]["business_ideas"]  # For business ideas
    elif isinstance(ideas[0], dict) and "ideas" in ideas[0]:
        actual_ideas = ideas[0]["ideas"]  # For creative/product ideas
```

#### Frontend Field Mapping
The frontend must handle different field names from different idea types:
- Creative ideas: `title`, `concept`, `innovationLevel`, `implementationDifficulty`
- Business ideas: `business_name`, `description`, `scalability`, `startup_costs`
- Product ideas: `product_name`, `description`, `market_readiness`, `development_timeline`

### Student Mode Implementation
The application includes a Student Mode toggle that:
- Switches between simplified and professional language
- Shows different example prompts (campus-focused vs general)
- Adjusts default settings (2 product ideas vs 2 creative ideas)
- Provides educational context and learning objectives
- Uses CSS classes `student-mode` and `simplified-labels` for UI switching

### Configuration Management
All agent behavior is controlled through `config.yaml`:
- `agents.num_ideas`: Default number of ideas to generate (currently 2)
- `models.default_provider`: AI provider preference (anthropic/openai)
- `models.anthropic_model` and `models.openai_model`: Specific model versions

### Session Management
The OrchestratorAgent maintains session state for workflow continuity:
- Tracks active sessions with unique IDs
- Stores workflow history and results
- Manages agent interactions and human-in-the-loop checkpoints
- Enables workflow pause/resume functionality