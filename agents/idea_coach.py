import json
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent


class IdeaCoachAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "idea_coach")
        self.idea_generation_prompts = {
            "creative": """You are an expert idea generation coach. Generate
{num_ideas} innovative and creative ideas based on the following prompt:

{prompt}

For each idea, provide:
1. Title: A catchy, memorable name
2. Concept: A clear 2-3 sentence description
3. Target Market: Who would use this
4. Unique Value Proposition: What makes it special
5. Innovation Level: Rate 1-10 (10 being most innovative)
6. Implementation Difficulty: Rate 1-10 (10 being most difficult)

Format your response as a JSON array of idea objects.""",

            "business": """You are a business idea generation expert.
Create {num_ideas} viable business ideas for:

{prompt}

Each idea should include:
1. Business Name: Professional, marketable name
2. Description: Clear business model description
3. Revenue Model: How it makes money
4. Market Size: Estimated target market
5. Competitive Advantage: Key differentiators
6. Startup Costs: Rough estimate (Low/Medium/High)
7. Scalability: Growth potential (1-10)

Return as JSON array of business idea objects.""",

            "product": """As a product innovation specialist, develop
{num_ideas} product ideas for:

{prompt}

For each product idea:
1. Product Name: Market-ready name
2. Description: Core functionality and features
3. Target Users: Primary user personas
4. Problem Solved: What pain point it addresses
5. Key Features: Top 3-5 features
6. Technology Stack: Required technologies
7. Development Timeline: Estimated timeframe
8. Market Readiness: How ready is the market (1-10)

Provide response as JSON array."""
        }

    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        self.update_status(
            "processing", f"Generating ideas for: {task_data.get('prompt', 'unknown')}"
        )
        start_time = datetime.now()

        try:
            prompt = task_data.get("prompt", "")
            num_ideas = task_data.get("num_ideas", self.config["agents"]["num_ideas"])
            idea_type = task_data.get("idea_type", "creative")

            # Select appropriate prompt template
            template = self.idea_generation_prompts.get(
                idea_type, self.idea_generation_prompts["creative"]
            )
            formatted_prompt = template.format(prompt=prompt, num_ideas=num_ideas)

            # Get AI response
            response = await self.get_ai_response(formatted_prompt)

            # Parse JSON response
            try:
                ideas = json.loads(response)
                if not isinstance(ideas, list):
                    ideas = [ideas]
            except json.JSONDecodeError:
                # Fallback: extract ideas from text response
                ideas = self._extract_ideas_from_text(response, num_ideas)

            # Enhance ideas with metadata
            enhanced_ideas = []
            for i, idea in enumerate(ideas[:num_ideas]):
                enhanced_idea = {
                    "id": f"idea_{datetime.now().timestamp()}_{i}",
                    "generated_by": self.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "type": idea_type,
                    **idea
                }
                enhanced_ideas.append(enhanced_idea)

            response_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(True, response_time)
            self.update_status("completed", None)

            return {
                "success": True,
                "ideas": enhanced_ideas,
                "generated_count": len(enhanced_ideas),
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

    def _extract_ideas_from_text(
        self, text: str, num_ideas: int
    ) -> List[Dict[str, Any]]:
        """Fallback method to extract ideas from non-JSON text response"""
        ideas = []
        lines = text.split('\n')
        current_idea = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for idea separators or numbers
            if (any(str(i) in line for i in range(1, num_ideas + 1))
                    and len(current_idea) > 0):
                ideas.append(current_idea)
                current_idea = {}

            # Extract key-value pairs
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                current_idea[key] = value

        if current_idea:
            ideas.append(current_idea)

        # Ensure we have the right number of ideas
        while len(ideas) < num_ideas:
            ideas.append({
                "title": f"Generated Idea {len(ideas) + 1}",
                "concept": "Creative solution generated from input prompt",
                "innovation_level": 5
            })

        return ideas[:num_ideas]

    async def generate_ideas(
        self, prompt: str, num_ideas: int = None, idea_type: str = "creative"
    ) -> Dict[str, Any]:
        """Public method to generate ideas"""
        task_data = {
            "prompt": prompt,
            "num_ideas": num_ideas or self.config["agents"]["num_ideas"],
            "idea_type": idea_type
        }
        return await self.execute_task(task_data)
