import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class ProductManagerAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, "product_manager")
        
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        self.update_status("processing", "Creating Product Requirements Document")
        start_time = datetime.now()
        
        try:
            idea = task_data.get("idea", {})
            validation_data = task_data.get("validation_data", {})
            requirements_focus = task_data.get("requirements_focus", [
                "functional", "technical", "business", "user_experience", "compliance"
            ])
            
            # Create comprehensive PRD
            prd_document = await self._create_prd(idea, validation_data, requirements_focus)
            
            response_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(True, response_time)
            self.update_status("completed", None)
            
            return {
                "success": True,
                "prd_document": prd_document,
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
    
    async def _create_prd(self, idea: Dict[str, Any], validation_data: Dict[str, Any], focus_areas: List[str]) -> Dict[str, Any]:
        """Create comprehensive Product Requirements Document"""
        
        # Executive Summary
        executive_summary = await self._create_executive_summary(idea, validation_data)
        
        # Product Overview
        product_overview = await self._create_product_overview(idea, validation_data)
        
        # Market Analysis & User Research
        market_analysis = await self._create_market_analysis(idea, validation_data)
        
        # Functional Requirements
        functional_requirements = await self._create_functional_requirements(idea, validation_data)
        
        # Technical Requirements
        technical_requirements = await self._create_technical_requirements(idea, validation_data)
        
        # User Experience Requirements
        ux_requirements = await self._create_ux_requirements(idea, validation_data)
        
        # Business Requirements
        business_requirements = await self._create_business_requirements(idea, validation_data)
        
        # Project Timeline & Milestones
        timeline = await self._create_timeline(idea, validation_data)
        
        # Success Metrics & KPIs
        success_metrics = await self._create_success_metrics(idea, validation_data)
        
        # Risk Assessment & Mitigation
        risk_assessment = await self._create_risk_assessment(idea, validation_data)
        
        return {
            "document_id": f"prd_{datetime.now().timestamp()}",
            "created_by": self.agent_id,
            "creation_date": datetime.now().isoformat(),
            "product_name": idea.get("title", "New Product"),
            "version": "1.0",
            "executive_summary": executive_summary,
            "product_overview": product_overview,
            "market_analysis": market_analysis,
            "functional_requirements": functional_requirements,
            "technical_requirements": technical_requirements,
            "ux_requirements": ux_requirements,
            "business_requirements": business_requirements,
            "timeline": timeline,
            "success_metrics": success_metrics,
            "risk_assessment": risk_assessment,
            "appendices": {
                "validation_data": validation_data,
                "original_idea": idea
            }
        }
    
    async def _create_executive_summary(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary section"""
        prompt = f"""
        As a senior product manager, create an executive summary for this product:
        
        Product: {idea.get('title', 'New Product')}
        Description: {idea.get('concept', 'No description')}
        Validation Score: {validation_data.get('overall_score', 'N/A')}
        Market Potential: {validation_data.get('market_analysis', {}).get('score', 'N/A')}
        
        Create a compelling executive summary including:
        1. Product Vision & Mission
        2. Market Opportunity
        3. Key Value Propositions
        4. Success Potential
        5. Resource Requirements Overview
        
        Format as JSON with structured sections.
        """
        
        response = await self.get_ai_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "vision": f"Revolutionary {idea.get('title', 'product')} addressing market needs",
                "mission": "Deliver exceptional value to target users",
                "opportunity": "Significant market opportunity identified",
                "value_propositions": ["Innovative solution", "Strong market fit", "Scalable approach"],
                "success_potential": "High potential based on validation analysis"
            }
    
    async def _create_product_overview(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed product overview"""
        return {
            "product_name": idea.get("title", "New Product"),
            "product_description": idea.get("concept", "Innovative solution"),
            "target_users": idea.get("target_market", "Primary market users"),
            "core_problem": "Identified user pain points",
            "solution_approach": idea.get("unique_value_proposition", "Unique approach to solving problems"),
            "key_differentiators": [
                "Innovation-focused approach",
                "User-centric design",
                "Scalable architecture"
            ],
            "product_category": "Technology/Software",
            "launch_readiness": validation_data.get("overall_score", 0) >= 7
        }
    
    async def _create_market_analysis(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create market analysis section"""
        return {
            "target_market": {
                "primary": idea.get("target_market", "Primary users"),
                "secondary": "Adjacent market segments",
                "market_size": validation_data.get("market_analysis", {}).get("analysis", "Market size analysis pending")
            },
            "competitive_landscape": validation_data.get("competitive_analysis", {}),
            "market_trends": ["Growing demand", "Technology adoption", "User behavior shifts"],
            "go_to_market_strategy": {
                "channels": ["Direct sales", "Digital marketing", "Partnership"],
                "pricing_strategy": "Value-based pricing",
                "launch_approach": "Phased rollout"
            }
        }
    
    async def _create_functional_requirements(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create functional requirements"""
        prompt = f"""
        As a product manager, define functional requirements for:
        
        Product: {idea.get('title', 'Product')}
        Description: {idea.get('concept', 'Description')}
        Key Features: {idea.get('key_features', [])}
        
        Create detailed functional requirements with:
        1. Core Features (Must-have)
        2. Enhanced Features (Should-have)
        3. Future Features (Could-have)
        4. User Stories for key features
        5. Acceptance Criteria
        
        Format as JSON with priority levels and user stories.
        """
        
        response = await self.get_ai_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "core_features": [
                    {"name": "Primary functionality", "priority": "Must-have", "description": "Core product capability"},
                    {"name": "User interface", "priority": "Must-have", "description": "Intuitive user experience"},
                    {"name": "Data management", "priority": "Must-have", "description": "Secure data handling"}
                ],
                "enhanced_features": [
                    {"name": "Advanced analytics", "priority": "Should-have", "description": "Enhanced reporting"},
                    {"name": "Integration capabilities", "priority": "Should-have", "description": "Third-party connections"}
                ],
                "future_features": [
                    {"name": "AI enhancements", "priority": "Could-have", "description": "Machine learning features"},
                    {"name": "Mobile optimization", "priority": "Could-have", "description": "Mobile-first experience"}
                ]
            }
    
    async def _create_technical_requirements(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create technical requirements"""
        return {
            "architecture": {
                "system_type": "Web-based application",
                "deployment": "Cloud-native",
                "scalability": "Horizontally scalable",
                "availability": "99.9% uptime target"
            },
            "technology_stack": {
                "backend": idea.get("technology_stack", ["Python", "FastAPI"]),
                "frontend": ["React", "TypeScript"],
                "database": ["PostgreSQL", "Redis"],
                "infrastructure": ["AWS", "Docker", "Kubernetes"]
            },
            "performance_requirements": {
                "response_time": "< 200ms for API calls",
                "throughput": "1000+ concurrent users",
                "data_processing": "Real-time processing capability"
            },
            "security_requirements": [
                "Authentication and authorization",
                "Data encryption in transit and at rest",
                "GDPR compliance",
                "Regular security audits"
            ],
            "integration_requirements": [
                "RESTful API design",
                "Webhook support",
                "Third-party service integration"
            ]
        }
    
    async def _create_ux_requirements(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user experience requirements"""
        return {
            "design_principles": [
                "User-centered design",
                "Accessibility compliance (WCAG 2.1)",
                "Mobile-responsive design",
                "Intuitive navigation"
            ],
            "user_journey": {
                "onboarding": "Streamlined user onboarding process",
                "core_workflow": "Efficient task completion",
                "support": "Contextual help and documentation"
            },
            "interface_requirements": {
                "design_system": "Consistent component library",
                "responsiveness": "Mobile-first approach",
                "loading_performance": "Progressive loading",
                "error_handling": "User-friendly error messages"
            },
            "usability_metrics": {
                "task_completion_rate": "> 90%",
                "user_satisfaction": "> 4.5/5",
                "learning_curve": "< 30 minutes to proficiency"
            }
        }
    
    async def _create_business_requirements(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create business requirements"""
        return {
            "business_objectives": [
                "Achieve product-market fit",
                "Generate sustainable revenue",
                "Build scalable user base",
                "Establish market presence"
            ],
            "revenue_model": {
                "primary": idea.get("revenue_model", "Subscription-based"),
                "pricing_tiers": ["Basic", "Professional", "Enterprise"],
                "monetization": "Freemium with premium features"
            },
            "success_criteria": {
                "user_acquisition": "10,000+ users in first year",
                "revenue_target": "$500K ARR by year 2",
                "market_share": "5% of target market segment"
            },
            "compliance_requirements": [
                "Data privacy regulations",
                "Industry-specific compliance",
                "Accessibility standards",
                "Security certifications"
            ]
        }
    
    async def _create_timeline(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create project timeline and milestones"""
        start_date = datetime.now()
        
        return {
            "project_phases": [
                {
                    "phase": "Discovery & Planning",
                    "duration": "4 weeks",
                    "start_date": start_date.isoformat(),
                    "end_date": (start_date + timedelta(weeks=4)).isoformat(),
                    "deliverables": ["Requirements finalization", "Technical architecture", "Design system"]
                },
                {
                    "phase": "MVP Development",
                    "duration": "12 weeks",
                    "start_date": (start_date + timedelta(weeks=4)).isoformat(),
                    "end_date": (start_date + timedelta(weeks=16)).isoformat(),
                    "deliverables": ["Core features", "Basic UI", "Testing framework"]
                },
                {
                    "phase": "Beta Testing",
                    "duration": "4 weeks",
                    "start_date": (start_date + timedelta(weeks=16)).isoformat(),
                    "end_date": (start_date + timedelta(weeks=20)).isoformat(),
                    "deliverables": ["User feedback", "Performance optimization", "Bug fixes"]
                },
                {
                    "phase": "Launch Preparation",
                    "duration": "4 weeks",
                    "start_date": (start_date + timedelta(weeks=20)).isoformat(),
                    "end_date": (start_date + timedelta(weeks=24)).isoformat(),
                    "deliverables": ["Marketing materials", "Support documentation", "Launch strategy"]
                }
            ],
            "critical_milestones": [
                "Requirements sign-off",
                "MVP completion",
                "Beta user onboarding",
                "Public launch"
            ],
            "estimated_timeline": "6 months to launch",
            "resource_allocation": {
                "development": "3-4 developers",
                "design": "1-2 designers",
                "product_management": "1 product manager",
                "qa_testing": "1-2 testers"
            }
        }
    
    async def _create_success_metrics(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create success metrics and KPIs"""
        return {
            "key_metrics": {
                "user_metrics": {
                    "daily_active_users": "Target: 1,000+ DAU",
                    "monthly_active_users": "Target: 10,000+ MAU",
                    "user_retention": "Target: 80% 30-day retention",
                    "churn_rate": "Target: < 5% monthly churn"
                },
                "business_metrics": {
                    "revenue": "Target: $50K MRR by month 12",
                    "customer_acquisition_cost": "Target: < $100 CAC",
                    "lifetime_value": "Target: > $500 LTV",
                    "conversion_rate": "Target: > 10% trial to paid"
                },
                "product_metrics": {
                    "feature_adoption": "Target: > 60% core feature usage",
                    "user_satisfaction": "Target: > 4.5/5 rating",
                    "support_tickets": "Target: < 2% of users/month"
                }
            },
            "measurement_framework": {
                "tracking_tools": ["Google Analytics", "Mixpanel", "Customer surveys"],
                "reporting_frequency": "Weekly dashboards, monthly reviews",
                "success_reviews": "Quarterly business reviews"
            }
        }
    
    async def _create_risk_assessment(self, idea: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk assessment and mitigation strategies"""
        return {
            "identified_risks": [
                {
                    "risk": "Market competition",
                    "probability": "Medium",
                    "impact": "High",
                    "mitigation": "Focus on unique value proposition and rapid iteration"
                },
                {
                    "risk": "Technical complexity",
                    "probability": "Medium",
                    "impact": "Medium",
                    "mitigation": "Phased development approach and technical prototyping"
                },
                {
                    "risk": "User adoption",
                    "probability": "Medium",
                    "impact": "High",
                    "mitigation": "Extensive user research and beta testing program"
                },
                {
                    "risk": "Resource constraints",
                    "probability": "Low",
                    "impact": "Medium",
                    "mitigation": "Flexible team scaling and priority management"
                }
            ],
            "contingency_plans": [
                "Pivot strategy for market changes",
                "Alternative technical approaches",
                "Backup funding scenarios",
                "Timeline adjustment procedures"
            ],
            "monitoring_strategy": "Monthly risk assessment reviews with mitigation updates"
        }
    
    async def create_prd(self, idea: Dict[str, Any], validation_data: Dict[str, Any], session_id: str = None) -> Dict[str, Any]:
        """Public method to create PRD"""
        task_data = {
            "idea": idea,
            "validation_data": validation_data,
            "session_id": session_id
        }
        return await self.execute_task(task_data)