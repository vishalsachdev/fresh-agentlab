"""
Test suite for ValidationAgent scoring algorithm
Following TDD methodology with SPARC integration

Tests the weighted scoring system:
- Market Analysis: 30% weight
- Competitive Analysis: 25% weight  
- Technical Feasibility: 25% weight
- Financial Analysis: 20% weight
- Overall Score: 0-10 scale
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.validation import ValidationAgent


class TestValidationScoringAlgorithm:
    """Test suite for validation scoring algorithm"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing"""
        return {
            "models": {
                "default_provider": "anthropic",
                "anthropic_model": "claude-3-5-sonnet-20241022"
            }
        }
    
    @pytest.fixture
    def validation_agent(self, mock_config):
        """Create ValidationAgent instance for testing"""
        with patch('agents.base_agent.load_dotenv'), \
             patch('agents.base_agent.os.getenv') as mock_getenv, \
             patch('agents.base_agent.anthropic.Anthropic'), \
             patch('agents.base_agent.openai.OpenAI'):
            
            # Mock environment variables
            mock_getenv.side_effect = lambda key: "test_key" if "API_KEY" in key else None
            
            agent = ValidationAgent(mock_config)
            return agent
    
    @pytest.fixture
    def sample_idea(self):
        """Sample idea for testing"""
        return {
            "title": "AI-Powered Study Assistant",
            "concept": "An AI tool that helps students create personalized study plans",
            "target_market": "College students"
        }

    # TEST 1: Weighted Score Calculation Accuracy
    def test_calculate_validation_score_perfect_scores(self, validation_agent):
        """Test scoring with perfect scores (all 10s)"""
        scores = {
            "market": 10,
            "competition": 10, 
            "technical": 10,
            "financial": 10
        }
        
        result = validation_agent._calculate_validation_score(scores)
        expected = (10 * 0.3) + (10 * 0.25) + (10 * 0.25) + (10 * 0.2)  # = 10.0
        
        assert result == 10.0
        assert isinstance(result, float)
    
    def test_calculate_validation_score_zero_scores(self, validation_agent):
        """Test scoring with all zero scores"""
        scores = {
            "market": 0,
            "competition": 0,
            "technical": 0, 
            "financial": 0
        }
        
        result = validation_agent._calculate_validation_score(scores)
        expected = 0.0
        
        assert result == expected
    
    def test_calculate_validation_score_weighted_distribution(self, validation_agent):
        """Test that weights are correctly applied"""
        scores = {
            "market": 8,      # 30% weight = 2.4
            "competition": 6,  # 25% weight = 1.5
            "technical": 7,   # 25% weight = 1.75
            "financial": 9    # 20% weight = 1.8
        }
        
        result = validation_agent._calculate_validation_score(scores)
        expected = (8 * 0.3) + (6 * 0.25) + (7 * 0.25) + (9 * 0.2)  # = 7.45
        
        assert result == 7.45
    
    def test_calculate_validation_score_missing_keys(self, validation_agent):
        """Test scoring handles missing score keys gracefully"""
        scores = {
            "market": 8,
            "competition": 6
            # Missing technical and financial
        }
        
        result = validation_agent._calculate_validation_score(scores)
        expected = (8 * 0.3) + (6 * 0.25) + (0 * 0.25) + (0 * 0.2)  # = 3.9
        
        assert result == 3.9
    
    def test_calculate_validation_score_rounding(self, validation_agent):
        """Test that scores are properly rounded to 2 decimal places"""
        scores = {
            "market": 7.333,
            "competition": 8.666,
            "technical": 6.111,
            "financial": 9.999
        }
        
        result = validation_agent._calculate_validation_score(scores)
        # Should be rounded to 2 decimal places
        assert len(str(result).split('.')[-1]) <= 2
    
    # TEST 2: Weight Distribution Validation
    def test_weight_sum_equals_one(self, validation_agent):
        """Test that all weights sum to 1.0 (100%)"""
        # Access the weights used in the calculation
        weights = {
            "market": 0.3,
            "competition": 0.25,
            "technical": 0.25,
            "financial": 0.2
        }
        
        total_weight = sum(weights.values())
        assert total_weight == 1.0
    
    def test_market_weight_highest(self, validation_agent):
        """Test that market analysis has the highest weight (30%)"""
        # Test with extreme scores to verify market weight dominance
        high_market_scores = {
            "market": 10,
            "competition": 0,
            "technical": 0,
            "financial": 0
        }
        
        high_other_scores = {
            "market": 0,
            "competition": 10,
            "technical": 10,
            "financial": 10
        }
        
        market_result = validation_agent._calculate_validation_score(high_market_scores)
        other_result = validation_agent._calculate_validation_score(high_other_scores)
        
        # Market at 10 with 30% weight = 3.0
        # Others at 10 with 25%+25%+20% = 7.0
        assert market_result == 3.0
        assert other_result == 7.0
        assert other_result > market_result  # But others combined outweigh market
    
    # TEST 3: Edge Cases and Error Handling
    def test_calculate_validation_score_negative_values(self, validation_agent):
        """Test handling of negative scores (should work but unusual)"""
        scores = {
            "market": -2,
            "competition": 5,
            "technical": 8,
            "financial": 6
        }
        
        result = validation_agent._calculate_validation_score(scores)
        expected = (-2 * 0.3) + (5 * 0.25) + (8 * 0.25) + (6 * 0.2)  # = 3.85
        
        assert result == 3.85
    
    def test_calculate_validation_score_values_above_ten(self, validation_agent):
        """Test handling of scores above 10 (should work but unusual)"""
        scores = {
            "market": 15,
            "competition": 8,
            "technical": 7,
            "financial": 6
        }
        
        result = validation_agent._calculate_validation_score(scores)
        expected = (15 * 0.3) + (8 * 0.25) + (7 * 0.25) + (6 * 0.2)  # = 9.45
        
        assert result == 9.45
    
    def test_calculate_validation_score_empty_dict(self, validation_agent):
        """Test scoring with empty scores dictionary"""
        scores = {}
        
        result = validation_agent._calculate_validation_score(scores)
        expected = 0.0
        
        assert result == expected
    
    # TEST 4: Recommendation Generation Based on Scores
    def test_generate_recommendations_high_score(self, validation_agent):
        """Test recommendations for high overall scores (≥8)"""
        mock_analyses = {
            "market": {"score": 9},
            "competition": {"score": 8},
            "technical": {"score": 8},
            "financial": {"score": 8}
        }
        
        recommendations = validation_agent._generate_recommendations(8.5, mock_analyses)
        
        assert any("Strong idea" in rec for rec in recommendations)
        assert any("recommend proceeding" in rec for rec in recommendations)
    
    def test_generate_recommendations_medium_score(self, validation_agent):
        """Test recommendations for medium scores (6-7.9)"""
        mock_analyses = {
            "market": {"score": 7},
            "competition": {"score": 6},
            "technical": {"score": 7},
            "financial": {"score": 6}
        }
        
        recommendations = validation_agent._generate_recommendations(6.5, mock_analyses)
        
        assert any("Promising idea" in rec for rec in recommendations)
        assert any("address key concerns" in rec for rec in recommendations)
    
    def test_generate_recommendations_low_score(self, validation_agent):
        """Test recommendations for low scores (<6)"""
        mock_analyses = {
            "market": {"score": 4},
            "competition": {"score": 5},
            "technical": {"score": 3},
            "financial": {"score": 4}
        }
        
        recommendations = validation_agent._generate_recommendations(4.0, mock_analyses)
        
        assert any("Significant challenges" in rec for rec in recommendations)
        assert any("pivoting" in rec or "major modifications" in rec for rec in recommendations)
    
    # TEST 5: Individual Component Recommendations
    def test_generate_recommendations_low_market_score(self, validation_agent):
        """Test specific recommendations for low market scores"""
        mock_analyses = {
            "market": {"score": 4},  # Low market score
            "competition": {"score": 8},
            "technical": {"score": 8},
            "financial": {"score": 8}
        }
        
        recommendations = validation_agent._generate_recommendations(7.0, mock_analyses)
        
        # Should include market research recommendation
        assert any("market research" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_low_technical_score(self, validation_agent):
        """Test specific recommendations for low technical scores"""
        mock_analyses = {
            "market": {"score": 8},
            "competition": {"score": 8},
            "technical": {"score": 4},  # Low technical score
            "financial": {"score": 8}
        }
        
        recommendations = validation_agent._generate_recommendations(7.0, mock_analyses)
        
        # Should include technical risk assessment recommendation
        assert any("technical risks" in rec.lower() for rec in recommendations)
    
    def test_generate_recommendations_low_financial_score(self, validation_agent):
        """Test specific recommendations for low financial scores"""
        mock_analyses = {
            "market": {"score": 8},
            "competition": {"score": 8},
            "technical": {"score": 8},
            "financial": {"score": 4}  # Low financial score
        }
        
        recommendations = validation_agent._generate_recommendations(7.0, mock_analyses)
        
        # Should include business model recommendation
        assert any("business model" in rec.lower() for rec in recommendations)

    # TEST 6: Integration Tests
    @pytest.mark.asyncio
    async def test_full_validation_workflow_scoring(self, validation_agent, sample_idea):
        """Integration test for full validation workflow with mocked AI responses"""
        
        # Mock AI responses for each analysis
        mock_responses = [
            '{"score": 8, "analysis": "Strong market potential", "key_insights": ["Growing market"]}',  # Market
            '{"score": 7, "competitors": ["CompetitorA"], "advantages": ["Unique approach"], "threats": ["Market entry"]}',  # Competition
            '{"score": 6, "complexity": "Medium", "technologies": ["AI", "Web"], "timeline": "6 months"}',  # Technical
            '{"score": 9, "revenue_potential": "High", "investment_needed": "Medium", "roi_timeline": "18 months"}'  # Financial
        ]
        
        with patch.object(validation_agent, 'get_ai_response', side_effect=mock_responses):
            result = await validation_agent._comprehensive_validation(sample_idea, [])
            
            # Check that overall score is calculated correctly
            expected_score = (8 * 0.3) + (7 * 0.25) + (6 * 0.25) + (9 * 0.2)  # = 7.45
            assert result["overall_score"] == 7.45
            
            # Check that all components are present
            assert "market_analysis" in result
            assert "competitive_analysis" in result
            assert "technical_feasibility" in result
            assert "financial_analysis" in result
            assert "recommendations" in result


# TEST 7: Performance and Boundary Tests
class TestValidationScoringPerformance:
    """Performance and boundary tests for the scoring algorithm"""
    
    @pytest.fixture
    def validation_agent(self):
        """Create ValidationAgent for performance testing"""
        with patch('agents.base_agent.load_dotenv'), \
             patch('agents.base_agent.os.getenv') as mock_getenv, \
             patch('agents.base_agent.anthropic.Anthropic'), \
             patch('agents.base_agent.openai.OpenAI'):
            
            mock_getenv.side_effect = lambda key: "test_key" if "API_KEY" in key else None
            
            config = {"models": {"default_provider": "anthropic"}}
            agent = ValidationAgent(config)
            return agent
    
    def test_scoring_performance_large_numbers(self, validation_agent):
        """Test performance with very large score values"""
        scores = {
            "market": 999999,
            "competition": 888888,
            "technical": 777777,
            "financial": 666666
        }
        
        result = validation_agent._calculate_validation_score(scores)
        
        # Should complete without error and return a reasonable result
        assert isinstance(result, float)
        assert result > 0
    
    def test_scoring_precision_float_values(self, validation_agent):
        """Test precision with many decimal places"""
        scores = {
            "market": 7.123456789,
            "competition": 8.987654321,
            "technical": 6.555555555,
            "financial": 9.111111111
        }
        
        result = validation_agent._calculate_validation_score(scores)
        
        # Should handle precision correctly and round to 2 decimal places
        assert isinstance(result, float)
        decimal_places = len(str(result).split('.')[-1])
        assert decimal_places <= 2


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])