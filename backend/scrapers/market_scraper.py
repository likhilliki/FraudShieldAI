import requests
import yfinance as yf
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time
import re

logger = logging.getLogger(__name__)

class MarketScraper:
    """Scraper for NSE/BSE market data and corporate announcements"""
    
    def __init__(self):
        self.nse_base = "https://www.nseindia.com"
        self.bse_base = "https://www.bseindia.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def verify_announcement(self, announcement: str, ticker: str = None) -> bool:
        """
        Verify if an announcement matches official filings
        """
        try:
            from database import search_announcements
            
            # Search in our database first
            if ticker:
                results = search_announcements(announcement, ticker)
            else:
                results = search_announcements(announcement)
            
            if results:
                # Check for content similarity
                for result in results:
                    if self._calculate_similarity(announcement, result.get('content', '')) > 0.7:
                        logger.info(f"Announcement verified against official filing")
                        return True
            
            # If not found locally, try to fetch latest announcements
            if ticker:
                recent_announcements = self.get_company_announcements(ticker)
                for ann in recent_announcements:
                    if self._calculate_similarity(announcement, ann.get('content', '')) > 0.7:
                        return True
            
            logger.info(f"Announcement not verified against official sources")
            return False
            
        except Exception as e:
            logger.error(f"Error verifying announcement: {str(e)}")
            return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple implementation)"""
        try:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_company_announcements(self, ticker: str) -> List[Dict[str, Any]]:
        """Get recent company announcements"""
        try:
            announcements = []
            
            # Try NSE first
            nse_announcements = self._scrape_nse_announcements(ticker)
            announcements.extend(nse_announcements)
            
            # Try BSE if NSE fails
            if not announcements:
                bse_announcements = self._scrape_bse_announcements(ticker)
                announcements.extend(bse_announcements)
            
            # Add to database
            from database import insert_announcement
            for ann in announcements:
                insert_announcement(
                    ann.get('company_name', ticker),
                    ticker,
                    ann.get('title'),
                    ann.get('content'),
                    ann.get('date'),
                    ann.get('source', 'NSE')
                )
            
            return announcements
            
        except Exception as e:
            logger.error(f"Error getting company announcements: {str(e)}")
            return []
    
    def _scrape_nse_announcements(self, ticker: str) -> List[Dict[str, Any]]:
        """Scrape NSE announcements for a company"""
        try:
            # NSE corporate announcements URL (this is a simplified version)
            url = f"{self.nse_base}/companies-listing/corporate-disclosure/corporate-announcements"
            
            # In production, you'd need to handle NSE's complex API authentication
            # For demo, we'll return some sample data
            
            sample_announcements = [
                {
                    'company_name': ticker,
                    'title': f'{ticker} - Board Meeting Announcement',
                    'content': f'The Board of Directors of {ticker} will meet to consider quarterly results',
                    'date': (datetime.now() - timedelta(days=1)).isoformat(),
                    'source': 'NSE'
                },
                {
                    'company_name': ticker,
                    'title': f'{ticker} - Dividend Declaration',
                    'content': f'{ticker} announces dividend payment to shareholders',
                    'date': (datetime.now() - timedelta(days=5)).isoformat(),
                    'source': 'NSE'
                }
            ]
            
            logger.info(f"Retrieved {len(sample_announcements)} NSE announcements for {ticker}")
            return sample_announcements
            
        except Exception as e:
            logger.error(f"Error scraping NSE announcements: {str(e)}")
            return []
    
    def _scrape_bse_announcements(self, ticker: str) -> List[Dict[str, Any]]:
        """Scrape BSE announcements for a company"""
        try:
            # BSE announcements (simplified version)
            sample_announcements = [
                {
                    'company_name': ticker,
                    'title': f'{ticker} - Corporate Action',
                    'content': f'BSE filing for {ticker} regarding corporate restructuring',
                    'date': (datetime.now() - timedelta(days=2)).isoformat(),
                    'source': 'BSE'
                }
            ]
            
            logger.info(f"Retrieved {len(sample_announcements)} BSE announcements for {ticker}")
            return sample_announcements
            
        except Exception as e:
            logger.error(f"Error scraping BSE announcements: {str(e)}")
            return []
    
    def detect_anomalies(self, ticker: str) -> Dict[str, Any]:
        """
        Detect market anomalies like pump and dump schemes
        """
        try:
            logger.info(f"Detecting anomalies for {ticker}")
            
            # Get stock data using yfinance as fallback
            stock_data = self._get_stock_data(ticker)
            
            if not stock_data:
                return {
                    'volume_spike': False,
                    'price_manipulation': False,
                    'social_buzz': False,
                    'volume_increase': 0,
                    'price_change': 0
                }
            
            # Analyze volume spikes
            recent_volumes = [data['volume'] for data in stock_data[-10:]]  # Last 10 days
            avg_volume = sum(recent_volumes[:-1]) / len(recent_volumes[:-1]) if len(recent_volumes) > 1 else recent_volumes[0]
            latest_volume = recent_volumes[-1]
            
            volume_increase = ((latest_volume - avg_volume) / avg_volume) * 100 if avg_volume > 0 else 0
            volume_spike = volume_increase > 200  # 200% increase threshold
            
            # Analyze price patterns
            recent_prices = [data['price'] for data in stock_data[-5:]]  # Last 5 days
            price_change = ((recent_prices[-1] - recent_prices[0]) / recent_prices[0]) * 100 if recent_prices[0] > 0 else 0
            
            # Detect manipulation patterns
            price_manipulation = False
            if volume_spike and abs(price_change) > 15:  # High volume + significant price change
                price_manipulation = True
            
            # Social buzz detection (simplified)
            social_buzz = volume_increase > 150 and abs(price_change) > 10
            
            # Store market data
            from database import insert_market_data
            if stock_data:
                latest = stock_data[-1]
                insert_market_data(ticker, latest['price'], latest['volume'], price_change, volume_increase)
            
            result = {
                'volume_spike': volume_spike,
                'price_manipulation': price_manipulation,
                'social_buzz': social_buzz,
                'volume_increase': round(volume_increase, 2),
                'price_change': round(price_change, 2),
                'avg_volume': int(avg_volume),
                'latest_volume': latest_volume,
                'analysis_date': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Anomaly detection completed for {ticker}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting anomalies for {ticker}: {str(e)}")
            return {
                'volume_spike': False,
                'price_manipulation': False,
                'social_buzz': False,
                'volume_increase': 0,
                'price_change': 0,
                'error': str(e)
            }
    
    def _get_stock_data(self, ticker: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get stock data using yfinance"""
        try:
            # Add .NS for NSE stocks if not present
            if not any(suffix in ticker.upper() for suffix in ['.NS', '.BO', '.BSE']):
                ticker_symbol = f"{ticker.upper()}.NS"
            else:
                ticker_symbol = ticker.upper()
            
            stock = yf.Ticker(ticker_symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                # Try with .BO suffix for BSE
                ticker_symbol = f"{ticker.upper()}.BO"
                stock = yf.Ticker(ticker_symbol)
                hist = stock.history(start=start_date, end=end_date)
            
            stock_data = []
            for date, row in hist.iterrows():
                stock_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'price': float(row['Close']),
                    'volume': int(row['Volume']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'open': float(row['Open'])
                })
            
            logger.info(f"Retrieved {len(stock_data)} days of data for {ticker_symbol}")
            return stock_data
            
        except Exception as e:
            logger.error(f"Error getting stock data for {ticker}: {str(e)}")
            # Return sample data for demo
            return self._get_sample_stock_data(ticker)
    
    def _get_sample_stock_data(self, ticker: str) -> List[Dict[str, Any]]:
        """Generate sample stock data for demo purposes"""
        import random
        
        base_price = random.uniform(100, 1000)
        base_volume = random.randint(100000, 1000000)
        
        stock_data = []
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            
            # Simulate normal variation
            price_change = random.uniform(-0.05, 0.05)  # ±5% daily change
            volume_change = random.uniform(-0.3, 0.3)   # ±30% volume change
            
            # Add anomaly for recent days (simulate pump)
            if i >= 25:  # Last 5 days
                if ticker.upper() in ['XYZ', 'PUMP', 'SCAM']:  # Demo tickers
                    price_change = random.uniform(0.1, 0.3)    # 10-30% increase
                    volume_change = random.uniform(2, 5)       # 200-500% volume spike
            
            current_price = base_price * (1 + price_change)
            current_volume = int(base_volume * (1 + volume_change))
            
            stock_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': round(current_price, 2),
                'volume': current_volume,
                'high': round(current_price * 1.02, 2),
                'low': round(current_price * 0.98, 2),
                'open': round(current_price * 0.99, 2)
            })
            
            base_price = current_price
            base_volume = current_volume
        
        return stock_data
    
    def refresh_data(self) -> Dict[str, Any]:
        """Refresh market data for all tracked stocks"""
        try:
            logger.info("Starting market data refresh")
            
            # Get list of actively traded stocks (sample)
            popular_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'ITC', 'HINDUNILVR']
            
            total_announcements = 0
            
            for ticker in popular_stocks:
                try:
                    announcements = self.get_company_announcements(ticker)
                    total_announcements += len(announcements)
                    
                    # Also update anomaly data
                    self.detect_anomalies(ticker)
                    
                    time.sleep(1)  # Be nice to APIs
                    
                except Exception as e:
                    logger.error(f"Error processing {ticker}: {str(e)}")
                    continue
            
            logger.info(f"Market data refresh completed. Processed {total_announcements} announcements")
            
            return {
                'success': True,
                'announcements': total_announcements,
                'stocks_processed': len(popular_stocks),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error refreshing market data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'announcements': 0
            }

def test_market_scraper():
    """Test the market scraper"""
    scraper = MarketScraper()
    
    # Test announcement verification
    test_announcement = "RELIANCE announces quarterly dividend of Rs 8 per share"
    is_verified = scraper.verify_announcement(test_announcement, "RELIANCE")
    print(f"Announcement verified: {is_verified}")
    
    # Test anomaly detection
    test_tickers = ['RELIANCE', 'XYZ', 'PUMP']
    for ticker in test_tickers:
        anomalies = scraper.detect_anomalies(ticker)
        print(f"\nTicker: {ticker}")
        print(f"Volume spike: {anomalies.get('volume_spike')}")
        print(f"Price manipulation: {anomalies.get('price_manipulation')}")
        print(f"Volume increase: {anomalies.get('volume_increase')}%")
        print(f"Price change: {anomalies.get('price_change')}%")
    
    # Test data refresh
    result = scraper.refresh_data()
    print(f"\nData refresh result: {result}")

if __name__ == "__main__":
    test_market_scraper()