# FreshAgentLab 🧠

Multi-Agent AI-Powered Idea Generation & Validation Platform built using the claude-flow approach without ADK framework dependencies.



## Features

- 🎯 **Multi-Agent Architecture**: IdeaCoach, Validation, ProductManager, and Orchestrator agents
- 🚀 **Three Idea Types**: Creative, Business, and Product-focused generation
- 🔍 **Comprehensive Validation**: Market analysis, technical feasibility, competitive landscape
- 📋 **PRD Generation**: Automated Product Requirements Document creation
- 🌐 **Web Interface**: Beautiful UI with human-in-the-loop interaction
- ⚡ **Full Pipeline**: Ideas → Validation → PRD in one workflow

## Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **AI Models**: Anthropic Claude, OpenAI GPT
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Architecture**: RESTful API, Multi-agent coordination

## Quick Start

### Prerequisites
- Python 3.8+
- Anthropic API key
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fresh-agentlab.git
   cd fresh-agentlab
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the server**
   ```bash
   python main.py
   ```

6. **Open your browser**
   ```
   http://localhost:8000
   ```

## Usage

1. **Enter your prompt**: Describe the challenge or domain for idea generation
2. **Choose idea type**: Creative, Business, or Product ideas
3. **Select workflow**: Ideas only or Full Pipeline (Ideas → Validation → PRD)
4. **Generate**: Watch the multi-agent system work its magic!

## API Endpoints

- `POST /api/generate-ideas` - Generate ideas
- `POST /api/validate-idea` - Validate an idea
- `POST /api/create-prd` - Create Product Requirements Document
- `GET /api/status` - Check agent status

## Project Structure

```
fresh-agentlab/
├── agents/                 # Multi-agent system
│   ├── base_agent.py      # Base agent class
│   ├── idea_coach.py      # Idea generation agent
│   ├── validation.py      # Validation agent
│   ├── product_manager.py # PRD creation agent
│   └── orchestrator.py    # Workflow coordination
├── models/                # Pydantic schemas
├── static/                # Web interface
├── config.yaml           # Application configuration
├── main.py               # FastAPI application
└── requirements.txt      # Dependencies
```

## Claude-Flow Approach

This project demonstrates the claude-flow methodology:
- **No ADK Framework Dependencies**: Pure Python/FastAPI implementation
- **Dynamic Agent Coordination**: Agents adapt to requirements
- **Human-in-the-Loop**: Interactive decision points
- **Parallel Execution**: Multiple agents working simultaneously
- **Shared Memory**: Session-based state management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

Built with ❤️ using the claude-flow approach and Claude Code.