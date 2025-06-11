from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.orchestrator import OrchestratorAgent
from agents.idea_coach import IdeaCoachAgent
from agents.validation import ValidationAgent
from agents.product_manager import ProductManagerAgent
from models.schemas import IdeaRequest, IdeaResponse, ValidationRequest, PRDRequest

app = FastAPI(title="FreshAgentLab", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

orchestrator = OrchestratorAgent(config)
idea_coach = IdeaCoachAgent(config)
validator = ValidationAgent(config)
product_manager = ProductManagerAgent(config)

@app.post("/api/generate-ideas", response_model=IdeaResponse)
async def generate_ideas(request: IdeaRequest):
    try:
        # Extract idea_type from context if provided
        idea_type = "creative"
        if request.context and "idea_type" in request.context:
            idea_type = request.context["idea_type"]
            
        result = await orchestrator.generate_ideas(request.prompt, request.num_ideas, idea_type)
        
        # Extract the workflow result to get the actual ideas
        if "workflow_result" in result and "steps" in result["workflow_result"]:
            for step in result["workflow_result"]["steps"]:
                if step.get("agent") == "idea_coach" and "result" in step:
                    step_result = step["result"]
                    ideas = step_result.get("ideas", [])
                    
                    # Handle multiple levels of nesting
                    if ideas and len(ideas) > 0:
                        first_item = ideas[0]
                        if isinstance(first_item, dict):
                            # Check for different possible nested structures
                            if "ideas" in first_item:
                                actual_ideas = first_item["ideas"]
                            elif "business_ideas" in first_item:
                                actual_ideas = first_item["business_ideas"]
                            elif "product_ideas" in first_item:
                                actual_ideas = first_item["product_ideas"]
                            else:
                                actual_ideas = ideas
                        else:
                            actual_ideas = ideas
                    else:
                        actual_ideas = []
                    
                    return IdeaResponse(ideas=actual_ideas, session_id=result["session_id"])
        
        # Fallback if structure is different
        return IdeaResponse(ideas=result.get("ideas", []), session_id=result.get("session_id", "unknown"))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/validate-idea")
async def validate_idea(request: ValidationRequest):
    try:
        result = await validator.validate_idea(request.idea, request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-prd")
async def create_prd(request: PRDRequest):
    try:
        result = await product_manager.create_prd(request.idea, request.validation_data, request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    return {
        "status": "running",
        "agents": {
            "orchestrator": orchestrator.get_status(),
            "idea_coach": idea_coach.get_status(),
            "validator": validator.get_status(),
            "product_manager": product_manager.get_status()
        }
    }

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host=config["app"]["host"], port=config["app"]["port"])