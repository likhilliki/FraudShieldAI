import openai
from dotenv import load_dotenv
import os
import re
from typing import Dict, Any
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY', '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')

def ai_credibility_analysis(content: str, context: str = "general") -> Dict[str, Any]:
    """
    Uses OpenAI GPT-4o-mini to score credibility of financial content.
    
    Args:
        content: Text input (advisor name, announcement, social tip)
        context: Type of check ("advisor", "announcement", "social", "anomaly")
    
    Returns:
        Dict with risk_score, risk_level, and ai_explanation
    """
    try:
        # Create context-specific prompts
        context_prompts = {
            "advisor": "You are analyzing a financial advisor for potential fraud indicators. Check if they make unrealistic promises or lack proper credentials.",
            "announcement": "You are analyzing a corporate announcement for authenticity and potential market manipulation. Look for exaggerated claims or suspicious timing.",
            "social": "You are analyzing social media content for investment fraud. Look for guaranteed returns, urgency tactics, and other red flags.",
            "anomaly": "You are analyzing stock market data for pump-and-dump schemes. Look for unusual volume/price patterns without fundamental justification."
        }
        
        system_prompt = context_prompts.get(context, "You are a financial fraud detection expert.")
        
        user_prompt = f"""
        Analyze the following content and rate its credibility on a scale of 0-100 
        (0 = certain fraud, 100 = fully trustworthy).
        
        Content: {content}
        
        Provide your analysis in this format:
        SCORE: [your numeric score 0-100]
        REASONING: [explain your reasoning in 2-3 sentences, focusing on specific red flags or positive indicators]
        
        Focus on detecting:
        - Unrealistic promises or guarantees
        - Pressure tactics or urgency
        - Lack of proper registration/credentials
        - Vague or exaggerated claims
        - Common fraud language patterns
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=300,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Extract score and reasoning
        score_match = re.search(r'SCORE:\s*(\d+)', ai_response)
        reasoning_match = re.search(r'REASONING:\s*(.+)', ai_response, re.DOTALL)
        
        if score_match:
            ai_score = int(score_match.group(1))
            # Convert to risk score (invert the credibility score)
            risk_score = 100 - ai_score
        else:
            # Fallback scoring based on keywords
            risk_score = _fallback_scoring(content, context)
        
        if reasoning_match:
            explanation = reasoning_match.group(1).strip()
        else:
            explanation = ai_response
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "High"
        elif risk_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "risk_score": min(95, max(5, risk_score)),  # Clamp between 5-95
            "risk_level": risk_level,
            "ai_explanation": explanation
        }
        
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        # Fallback to rule-based analysis
        return _fallback_analysis(content, context)

def _fallback_scoring(content: str, context: str) -> int:
    """Fallback rule-based scoring when AI fails"""
    content_lower = content.lower()
    risk_score = 30  # Base score
    
    # High-risk keywords
    high_risk_words = [
        'guaranteed', 'risk-free', 'sure shot', 'double your money',
        'insider information', 'hot tip', 'secret', 'exclusive deal'
    ]
    
    medium_risk_words = [
        'urgent', 'limited time', 'act now', 'extraordinary returns',
        'easy money', 'get rich quick'
    ]
    
    for word in high_risk_words:
        if word in content_lower:
            risk_score += 20
    
    for word in medium_risk_words:
        if word in content_lower:
            risk_score += 10
    
    return min(95, risk_score)

def _fallback_analysis(content: str, context: str) -> Dict[str, Any]:
    """Complete fallback analysis when AI is unavailable"""
    risk_score = _fallback_scoring(content, context)
    
    if risk_score >= 70:
        risk_level = "High"
        explanation = "High risk detected based on suspicious language patterns and potential fraud indicators."
    elif risk_score >= 40:
        risk_level = "Medium"
        explanation = "Medium risk - some concerning elements detected that warrant caution."
    else:
        risk_level = "Low"
        explanation = "Low risk - content appears relatively safe but always conduct your own research."
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "ai_explanation": explanation
    }

def test_ai_scoring():
    """Test function for AI scoring"""
    test_cases = [
        ("Guaranteed 300% returns in 30 days! Risk-free investment!", "social"),
        ("Reliance Industries announces quarterly dividend of Rs 8 per share", "announcement"),
        ("John Smith, SEBI registered investment advisor", "advisor"),
        ("XYZ stock showing 500% volume increase with no news", "anomaly")
    ]
    
    for content, context in test_cases:
        result = ai_credibility_analysis(content, context)
        print(f"\nContent: {content}")
        print(f"Context: {context}")
        print(f"Risk Score: {result['risk_score']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Explanation: {result['ai_explanation']}")
        print("-" * 50)

if __name__ == "__main__":
    test_ai_scoring()