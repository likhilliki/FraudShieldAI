from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import sqlite3
import os
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Import our custom modules
from scrapers.sebi_scraper import SEBIScraper
from scrapers.market_scraper import MarketScraper
from ai_scoring import ai_credibility_analysis
from database import init_db, get_db_connection

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Initialize scrapers
sebi_scraper = SEBIScraper()
market_scraper = MarketScraper()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/verify/advisor', methods=['POST'])
def verify_advisor():
    """Verify advisor against SEBI registry"""
    try:
        data = request.get_json()
        advisor_name = data.get('advisor_name', '').strip()
        
        if not advisor_name:
            return jsonify({'error': 'Advisor name is required'}), 400
        
        logger.info(f"Verifying advisor: {advisor_name}")
        
        # Check SEBI registry
        is_registered = sebi_scraper.check_advisor_registration(advisor_name)
        
        # Build risk assessment
        reasons = []
        risk_score = 50  # Default medium risk
        
        if not is_registered:
            reasons.append("Advisor not found in SEBI registry")
            risk_score = 85  # High risk
        else:
            reasons.append("Advisor found in SEBI registry")
            risk_score = 20  # Low risk
        
        # Get AI analysis
        ai_result = ai_credibility_analysis(
            content=f"Financial advisor: {advisor_name}",
            context="advisor"
        )
        
        # Combine assessments
        final_score = (risk_score + ai_result['risk_score']) // 2
        risk_level = "High" if final_score > 60 else "Medium" if final_score > 30 else "Low"
        
        # Save to history
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO history (type, content, risk_score, risk_level, reasons, ai_explanation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('advisor', advisor_name, final_score, risk_level, 
              '; '.join(reasons + [ai_result.get('ai_explanation', '')]), 
              ai_result.get('ai_explanation', '')))
        conn.commit()
        conn.close()
        
        return jsonify({
            'risk_score': final_score,
            'risk_level': risk_level,
            'reasons': reasons,
            'ai_explanation': ai_result.get('ai_explanation', 'Analysis completed.'),
            'sebi_registered': is_registered
        })
        
    except Exception as e:
        logger.error(f"Error in verify_advisor: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/verify/announcement', methods=['POST'])
def verify_announcement():
    """Verify corporate announcement against official filings"""
    try:
        data = request.get_json()
        announcement = data.get('announcement', '').strip()
        ticker = data.get('ticker', '').strip()
        
        if not announcement:
            return jsonify({'error': 'Announcement text is required'}), 400
        
        logger.info(f"Verifying announcement: {announcement[:100]}...")
        
        # Check against official filings
        is_verified = market_scraper.verify_announcement(announcement, ticker)
        
        # Build risk assessment
        reasons = []
        risk_score = 50
        
        if not is_verified:
            reasons.append("No matching official filing found")
            risk_score = 70
        else:
            reasons.append("Matches official corporate filing")
            risk_score = 25
        
        # Check for suspicious keywords
        suspicious_keywords = [
            'guaranteed returns', 'risk-free', 'double your money',
            'extraordinary returns', 'insider information', 'hot tip'
        ]
        
        for keyword in suspicious_keywords:
            if keyword.lower() in announcement.lower():
                reasons.append(f"Contains suspicious phrase: '{keyword}'")
                risk_score += 15
        
        # Get AI analysis
        ai_result = ai_credibility_analysis(
            content=announcement,
            context="announcement"
        )
        
        # Combine assessments
        final_score = min(95, (risk_score + ai_result['risk_score']) // 2)
        risk_level = "High" if final_score > 60 else "Medium" if final_score > 30 else "Low"
        
        # Save to history
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO history (type, content, risk_score, risk_level, reasons, ai_explanation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('announcement', announcement, final_score, risk_level, 
              '; '.join(reasons), ai_result.get('ai_explanation', '')))
        conn.commit()
        conn.close()
        
        return jsonify({
            'risk_score': final_score,
            'risk_level': risk_level,
            'reasons': reasons,
            'ai_explanation': ai_result.get('ai_explanation', 'Analysis completed.'),
            'official_filing_found': is_verified
        })
        
    except Exception as e:
        logger.error(f"Error in verify_announcement: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/verify/social', methods=['POST'])
def verify_social():
    """Detect fraud in social media content"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        logger.info(f"Analyzing social content: {content[:100]}...")
        
        # Rule-based fraud detection
        reasons = []
        risk_score = 30  # Start with low-medium risk
        
        # Check for fraud keywords
        fraud_indicators = {
            'guaranteed': 15,
            'risk-free': 20,
            'double your money': 25,
            'triple your money': 30,
            'insider': 20,
            'hot tip': 15,
            'sure shot': 20,
            'can\'t lose': 25,
            'limited time': 10,
            'act now': 10,
            'secret': 15,
            'exclusive': 10
        }
        
        for indicator, score in fraud_indicators.items():
            if indicator.lower() in content.lower():
                reasons.append(f"Contains fraud indicator: '{indicator}'")
                risk_score += score
        
        # Check for urgency patterns
        urgency_words = ['urgent', 'hurry', 'immediate', 'today only', 'expires']
        urgency_count = sum(1 for word in urgency_words if word.lower() in content.lower())
        if urgency_count > 0:
            reasons.append(f"High urgency language detected ({urgency_count} indicators)")
            risk_score += urgency_count * 5
        
        # Get AI analysis
        ai_result = ai_credibility_analysis(
            content=content,
            context="social"
        )
        
        # Combine assessments
        final_score = min(95, (risk_score + ai_result['risk_score']) // 2)
        risk_level = "High" if final_score > 60 else "Medium" if final_score > 30 else "Low"
        
        # Save to history
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO history (type, content, risk_score, risk_level, reasons, ai_explanation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('social', content, final_score, risk_level, 
              '; '.join(reasons), ai_result.get('ai_explanation', '')))
        conn.commit()
        conn.close()
        
        return jsonify({
            'risk_score': final_score,
            'risk_level': risk_level,
            'reasons': reasons,
            'ai_explanation': ai_result.get('ai_explanation', 'Analysis completed.'),
            'fraud_indicators_found': len(reasons)
        })
        
    except Exception as e:
        logger.error(f"Error in verify_social: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/verify/anomaly', methods=['POST'])
def verify_anomaly():
    """Detect pump and dump schemes"""
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').strip().upper()
        
        if not ticker:
            return jsonify({'error': 'Stock ticker is required'}), 400
        
        logger.info(f"Analyzing anomalies for ticker: {ticker}")
        
        # Get market data analysis
        anomaly_data = market_scraper.detect_anomalies(ticker)
        
        reasons = []
        risk_score = 30
        
        if anomaly_data.get('volume_spike'):
            reasons.append(f"Unusual volume spike detected ({anomaly_data['volume_increase']}% increase)")
            risk_score += 25
        
        if anomaly_data.get('price_manipulation'):
            reasons.append("Potential price manipulation pattern detected")
            risk_score += 30
        
        if anomaly_data.get('social_buzz'):
            reasons.append("High social media buzz without fundamental news")
            risk_score += 20
        
        # Get AI analysis
        ai_result = ai_credibility_analysis(
            content=f"Stock ticker {ticker} with volume spike: {anomaly_data.get('volume_increase', 0)}%, price change: {anomaly_data.get('price_change', 0)}%",
            context="anomaly"
        )
        
        # Combine assessments
        final_score = min(95, (risk_score + ai_result['risk_score']) // 2)
        risk_level = "High" if final_score > 60 else "Medium" if final_score > 30 else "Low"
        
        # Save to history
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO history (type, content, risk_score, risk_level, reasons, ai_explanation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('anomaly', ticker, final_score, risk_level, 
              '; '.join(reasons), ai_result.get('ai_explanation', '')))
        conn.commit()
        conn.close()
        
        return jsonify({
            'risk_score': final_score,
            'risk_level': risk_level,
            'reasons': reasons,
            'ai_explanation': ai_result.get('ai_explanation', 'Analysis completed.'),
            'market_data': anomaly_data
        })
        
    except Exception as e:
        logger.error(f"Error in verify_anomaly: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/refresh/sebi', methods=['POST'])
def refresh_sebi_data():
    """Manually refresh SEBI registry data"""
    try:
        logger.info("Starting SEBI registry refresh...")
        result = sebi_scraper.refresh_registry()
        return jsonify({
            'success': True,
            'message': f"SEBI registry updated. {result['count']} advisors processed.",
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error refreshing SEBI data: {str(e)}")
        return jsonify({'error': 'Failed to refresh SEBI data'}), 500

@app.route('/refresh/market', methods=['POST'])
def refresh_market_data():
    """Manually refresh market data"""
    try:
        logger.info("Starting market data refresh...")
        result = market_scraper.refresh_data()
        return jsonify({
            'success': True,
            'message': f"Market data updated. {result['announcements']} announcements processed.",
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error refreshing market data: {str(e)}")
        return jsonify({'error': 'Failed to refresh market data'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get verification history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        conn = get_db_connection()
        
        cursor = conn.execute('''
            SELECT * FROM history 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'id': row[0],
                'type': row[1],
                'content': row[2][:100] + '...' if len(row[2]) > 100 else row[2],
                'risk_score': row[3],
                'risk_level': row[4],
                'created_at': row[7]
            })
        
        conn.close()
        return jsonify({'history': history})
        
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'error': 'Failed to get history'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)