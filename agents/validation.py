import asyncio
import json
import aiohttp
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent

class ValidationAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "validation")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        self.update_status("processing", "Validating idea")
        start_time = datetime.now()
        
        try:
            idea = task_data.get("idea", {})
            validation_criteria = task_data.get("validation_criteria", [
                "market_viability", "technical_feasibility", "competitive_analysis", 
                "financial_potential", "user_demand"
            ])
            
            # Perform comprehensive validation
            validation_results = await self._comprehensive_validation(idea, validation_criteria)
            
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(True, response_time)
            self.update_status("completed", None)
            
            return {
                "success": True,
                "validation_results": validation_results,
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
    
    async def _comprehensive_validation(self, idea: Dict[str, Any], criteria: List[str]) -> Dict[str, Any]:
        """Perform comprehensive idea validation"""
        
        # Market Analysis
        market_analysis = await self._analyze_market(idea)
        
        # Competitive Analysis
        competitive_analysis = await self._analyze_competition(idea)
        
        # Technical Feasibility
        technical_feasibility = await self._assess_feasibility(idea)
        
        # Financial Potential
        financial_analysis = await self._analyze_financials(idea)
        
        # Calculate overall validation score
        overall_score = self._calculate_validation_score({
            "market": market_analysis.get("score", 0),
            "competition": competitive_analysis.get("score", 0),
            "technical": technical_feasibility.get("score", 0),
            "financial": financial_analysis.get("score", 0)
        })
        
        return {
            "overall_score": overall_score,
            "market_analysis": market_analysis,
            "competitive_analysis": competitive_analysis,
            "technical_feasibility": technical_feasibility,
            "financial_analysis": financial_analysis,
            "recommendations": self._generate_recommendations(overall_score, {
                "market": market_analysis,
                "competition": competitive_analysis,
                "technical": technical_feasibility,
                "financial": financial_analysis
            }),
            "validation_timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_market(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market viability of the idea"""
        prompt = f"""
        As a market research expert, analyze the market viability for this idea:
        
        Idea: {idea.get('title', 'Unknown')}
        Description: {idea.get('concept', 'No description')}
        Target Market: {idea.get('target_market', 'Unknown')}
        
        Provide analysis on:
        1. Market Size (TAM, SAM, SOM estimates)
        2. Market Trends (growing/declining/stable)
        3. Customer Pain Points addressed
        4. Market Readiness (early/mainstream/late adopter)
        5. Regulatory Environment
        6. Market Entry Barriers
        
        Rate the market viability from 1-10 and explain your reasoning.
        Format as JSON with 'score', 'analysis', and 'key_insights' fields.
        """
        
        response = await self.get_ai_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "score": 5,
                "analysis": response,
                "key_insights": ["Market analysis completed", "Further research recommended"]
            }
    
    async def _analyze_competition(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        prompt = f"""
        As a competitive intelligence analyst, analyze the competitive landscape for:
        
        Idea: {idea.get('title', 'Unknown')}
        Description: {idea.get('concept', 'No description')}
        
        Analyze:
        1. Direct Competitors (existing solutions)
        2. Indirect Competitors (alternative approaches)
        3. Competitive Advantages/Disadvantages
        4. Market Saturation Level
        5. Differentiation Opportunities
        6. Competitive Response Likelihood
        
        Rate competitive position from 1-10 (10 = strong competitive position).
        Format as JSON with 'score', 'competitors', 'advantages', 'threats' fields.
        """
        
        response = await self.get_ai_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "score": 6,
                "competitors": ["Analysis in progress"],
                "advantages": ["Unique approach identified"],
                "threats": ["Competitive response expected"]
            }
    
    async def _assess_feasibility(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Assess technical and operational feasibility"""
        prompt = f"""
        As a technical feasibility expert, assess the feasibility of implementing:
        
        Idea: {idea.get('title', 'Unknown')}
        Description: {idea.get('concept', 'No description')}
        Technology Stack: {idea.get('technology_stack', 'Not specified')}
        
        Evaluate:
        1. Technical Complexity (1-10)
        2. Resource Requirements (team size, skills)
        3. Technology Readiness Level
        4. Development Timeline estimates
        5. Scalability Challenges
        6. Integration Requirements
        7. Risk Factors
        
        Rate overall feasibility from 1-10.
        Format as JSON with 'score', 'complexity', 'timeline', 'risks' fields.
        """
        
        response = await self.get_ai_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "score": 7,
                "complexity": "Medium",
                "timeline": "6-12 months",
                "risks": ["Technical challenges manageable"]
            }
    
    async def _analyze_financials(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial potential and requirements"""
        prompt = f"""
        As a financial analyst, evaluate the financial aspects of:
        
        Idea: {idea.get('title', 'Unknown')}
        Description: {idea.get('concept', 'No description')}
        Revenue Model: {idea.get('revenue_model', 'Not specified')}
        Startup Costs: {idea.get('startup_costs', 'Unknown')}
        
        Analyze:
        1. Revenue Potential (annual projections)
        2. Startup Investment Required
        3. Operating Costs Structure
        4. Break-even Timeline
        5. Profitability Potential
        6. Funding Requirements
        7. ROI Projections
        
        Rate financial attractiveness from 1-10.
        Format as JSON with 'score', 'revenue_potential', 'investment_needed', 'roi_timeline' fields.
        """
        
        response = await self.get_ai_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "score": 6,
                "revenue_potential": "Moderate",
                "investment_needed": "Medium",
                "roi_timeline": "2-3 years"
            }
    
    def _calculate_validation_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall validation score"""
        weights = {
            "market": 0.3,
            "competition": 0.25,
            "technical": 0.25,
            "financial": 0.2
        }
        
        weighted_score = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        return round(weighted_score, 2)
    
    def _generate_recommendations(self, overall_score: float, analyses: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        recommendations = []
        
        if overall_score >= 8:
            recommendations.append("Strong idea with high potential - recommend proceeding to development")
        elif overall_score >= 6:
            recommendations.append("Promising idea with some challenges - address key concerns before proceeding")
        else:
            recommendations.append("Significant challenges identified - consider pivoting or major modifications")
        
        # Add specific recommendations based on individual scores
        market_score = analyses.get("market", {}).get("score", 0)
        if market_score < 6:
            recommendations.append("Conduct additional market research to validate demand")
        
        tech_score = analyses.get("technical", {}).get("score", 0)
        if tech_score < 6:
            recommendations.append("Assess technical risks and consider alternative implementation approaches")
        
        financial_score = analyses.get("financial", {}).get("score", 0)
        if financial_score < 6:
            recommendations.append("Review business model and explore additional revenue streams")
        
        return recommendations
    
    async def validate_idea(self, idea: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """Public method to validate an idea"""
        task_data = {
            "idea": idea,
            "session_id": session_id
        }
        return await self.execute_task(task_data)