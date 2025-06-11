import asyncio
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_agent import BaseAgent
from .idea_coach import IdeaCoachAgent
from .validation import ValidationAgent
from .product_manager import ProductManagerAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "orchestrator")
        
        # Initialize sub-agents
        self.idea_coach = IdeaCoachAgent(config)
        self.validator = ValidationAgent(config)
        self.product_manager = ProductManagerAgent(config)
        
        # Session management
        self.active_sessions = {}
        self.workflow_templates = {
            "full_pipeline": [
                {"agent": "idea_coach", "task": "generate_ideas"},
                {"agent": "validator", "task": "validate_ideas"},
                {"agent": "product_manager", "task": "create_prd"}
            ],
            "idea_generation": [
                {"agent": "idea_coach", "task": "generate_ideas"}
            ],
            "validation_only": [
                {"agent": "validator", "task": "validate_ideas"}
            ],
            "prd_creation": [
                {"agent": "product_manager", "task": "create_prd"}
            ]
        }
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        self.update_status("processing", "Orchestrating multi-agent workflow")
        start_time = datetime.now()
        
        try:
            workflow_type = task_data.get("workflow_type", "full_pipeline")
            session_id = task_data.get("session_id") or str(uuid.uuid4())
            
            # Initialize session
            session = self._create_session(session_id, task_data)
            
            # Execute workflow
            workflow_result = await self._execute_workflow(workflow_type, task_data, session)
            
            # Update session with results
            self._update_session(session_id, workflow_result)
            
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(True, response_time)
            self.update_status("completed", None)
            
            return {
                "success": True,
                "session_id": session_id,
                "workflow_result": workflow_result,
                "agent_id": self.agent_id,
                "processing_time": response_time
            }
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(False, response_time)
            self.update_status("error", f"Error: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
                "processing_time": response_time
            }
    
    def _create_session(self, session_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new session for tracking workflow execution"""
        session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "initial_request": task_data,
            "workflow_history": [],
            "current_stage": "initialized",
            "results": {},
            "human_interactions": []
        }
        
        self.active_sessions[session_id] = session
        return session
    
    def _update_session(self, session_id: str, workflow_result: Dict[str, Any]):
        """Update session with workflow results"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session["last_updated"] = datetime.now().isoformat()
            session["results"] = workflow_result
            session["current_stage"] = "completed"
    
    async def _execute_workflow(self, workflow_type: str, task_data: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specified workflow with agent coordination"""
        if workflow_type not in self.workflow_templates:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        workflow_steps = self.workflow_templates[workflow_type]
        results = {"workflow_type": workflow_type, "steps": []}
        
        # Store data between steps
        workflow_context = {"task_data": task_data}
        
        for step_idx, step in enumerate(workflow_steps):
            step_result = await self._execute_workflow_step(
                step, workflow_context, session, step_idx
            )
            results["steps"].append(step_result)
            
            # Update context for next step
            workflow_context[f"step_{step_idx}_result"] = step_result
            
            # Handle human-in-the-loop checkpoints
            if step_result.get("requires_human_input"):
                await self._handle_human_interaction(step_result, session)
        
        return results
    
    async def _execute_workflow_step(self, step: Dict[str, Any], context: Dict[str, Any], session: Dict[str, Any], step_idx: int) -> Dict[str, Any]:
        """Execute individual workflow step"""
        agent_name = step["agent"]
        task_name = step["task"]
        
        try:
            if agent_name == "idea_coach":
                result = await self._execute_idea_generation_step(context, session)
            elif agent_name == "validator":
                result = await self._execute_validation_step(context, session)
            elif agent_name == "product_manager":
                result = await self._execute_prd_creation_step(context, session)
            else:
                raise ValueError(f"Unknown agent: {agent_name}")
            
            return {
                "step_index": step_idx,
                "agent": agent_name,
                "task": task_name,
                "status": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "step_index": step_idx,
                "agent": agent_name,
                "task": task_name,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_idea_generation_step(self, context: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute idea generation step"""
        task_data = context["task_data"]
        
        result = await self.idea_coach.generate_ideas(
            prompt=task_data.get("prompt", ""),
            num_ideas=task_data.get("num_ideas", self.config["agents"]["num_ideas"]),
            idea_type=task_data.get("idea_type", "creative")
        )
        
        # Store ideas in session for next steps
        session["ideas"] = result.get("ideas", [])
        
        return result
    
    async def _execute_validation_step(self, context: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation step"""
        # Get ideas from previous step or session
        ideas = session.get("ideas", [])
        if not ideas:
            raise ValueError("No ideas available for validation")
        
        validation_results = []
        
        # Validate each idea (or top ideas based on config)
        max_validations = min(len(ideas), 3)  # Limit validations
        
        for idea in ideas[:max_validations]:
            validation_result = await self.validator.validate_idea(
                idea=idea,
                session_id=session["session_id"]
            )
            validation_results.append({
                "idea": idea,
                "validation": validation_result
            })
        
        # Store validation results in session
        session["validations"] = validation_results
        
        return {
            "validated_ideas": validation_results,
            "total_validated": len(validation_results)
        }
    
    async def _execute_prd_creation_step(self, context: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PRD creation step"""
        # Get top validated idea
        validations = session.get("validations", [])
        if not validations:
            raise ValueError("No validated ideas available for PRD creation")
        
        # Select best idea based on validation score
        best_idea_data = max(
            validations,
            key=lambda x: x.get("validation", {}).get("validation_results", {}).get("overall_score", 0)
        )
        
        idea = best_idea_data["idea"]
        validation_data = best_idea_data["validation"]["validation_results"]
        
        prd_result = await self.product_manager.create_prd(
            idea=idea,
            validation_data=validation_data,
            session_id=session["session_id"]
        )
        
        # Store PRD in session
        session["prd"] = prd_result
        
        return prd_result
    
    async def _handle_human_interaction(self, step_result: Dict[str, Any], session: Dict[str, Any]):
        """Handle human-in-the-loop interactions"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "step": step_result.get("agent"),
            "requires_input": step_result.get("requires_human_input"),
            "context": step_result.get("human_context", {}),
            "status": "pending"
        }
        
        session["human_interactions"].append(interaction)
        
        # In a real implementation, this would pause execution
        # and wait for human input through the web interface
        pass
    
    async def generate_ideas(self, prompt: str, num_ideas: int = None, idea_type: str = "creative") -> Dict[str, Any]:
        """Public method for idea generation workflow"""
        task_data = {
            "workflow_type": "idea_generation",
            "prompt": prompt,
            "num_ideas": num_ideas or self.config["agents"]["num_ideas"],
            "idea_type": idea_type
        }
        return await self.execute_task(task_data)
    
    async def full_pipeline(self, prompt: str, num_ideas: int = None, idea_type: str = "creative") -> Dict[str, Any]:
        """Public method for full pipeline workflow"""
        task_data = {
            "workflow_type": "full_pipeline",
            "prompt": prompt,
            "num_ideas": num_ideas or self.config["agents"]["num_ideas"],
            "idea_type": idea_type
        }
        return await self.execute_task(task_data)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.active_sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return list(self.active_sessions.values())
    
    def get_agent_status_summary(self) -> Dict[str, Any]:
        """Get status summary of all agents"""
        return {
            "orchestrator": self.get_status(),
            "idea_coach": self.idea_coach.get_status(),
            "validator": self.validator.get_status(),
            "product_manager": self.product_manager.get_status(),
            "active_sessions": len(self.active_sessions),
            "total_workflows_executed": self.performance_metrics["tasks_completed"]
        }