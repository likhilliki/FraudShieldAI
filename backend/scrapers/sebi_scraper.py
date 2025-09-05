import requests
import pandas as pd
import io
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import os
import time
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SEBIScraper:
    """Scraper for SEBI registry data"""
    
    def __init__(self):
        self.base_url = "https://www.sebi.gov.in"
        self.registry_url = "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognised=yes"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def check_advisor_registration(self, advisor_name: str) -> bool:
        """
        Check if advisor is registered with SEBI
        This is a simplified version - in production, you'd scrape the actual registry
        """
        try:
            # For demo purposes, we'll simulate checking against a database
            # In production, this would query the intermediaries table after scraping
            
            from database import search_intermediary
            results = search_intermediary(advisor_name)
            
            if results:
                logger.info(f"Advisor {advisor_name} found in registry")
                return True
            else:
                # Try fuzzy matching
                for result in results:
                    if advisor_name.lower() in result['name'].lower() or \
                       result['name'].lower() in advisor_name.lower():
                        logger.info(f"Advisor {advisor_name} found via fuzzy match")
                        return True
                
                logger.info(f"Advisor {advisor_name} not found in registry")
                return False
                
        except Exception as e:
            logger.error(f"Error checking advisor registration: {str(e)}")
            return False
    
    def scrape_registry_page(self, url: str) -> List[Dict[str, Any]]:
        """Scrape a single registry page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            advisors = []
            
            # Look for tables containing advisor data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                if len(rows) < 2:
                    continue
                
                # Try to identify header row
                header_row = rows[0]
                headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
                
                # Look for advisor-related headers
                if not any(header in ['name', 'advisor', 'intermediary'] for header in headers):
                    continue
                
                # Parse data rows
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        advisor_data = {
                            'name': cells[0].get_text().strip(),
                            'registration_number': cells[1].get_text().strip() if len(cells) > 1 else None,
                            'category': cells[2].get_text().strip() if len(cells) > 2 else 'Investment Advisor',
                            'status': 'Active'
                        }
                        
                        if advisor_data['name']:
                            advisors.append(advisor_data)
            
            logger.info(f"Scraped {len(advisors)} advisors from page")
            return advisors
            
        except Exception as e:
            logger.error(f"Error scraping registry page {url}: {str(e)}")
            return []
    
    def download_excel_files(self) -> List[str]:
        """Download Excel files from SEBI website"""
        try:
            response = self.session.get(self.registry_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            excel_links = []
            
            # Look for Excel file links
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href.endswith(('.xlsx', '.xls', '.csv')):
                    if not href.startswith('http'):
                        href = self.base_url + href
                    excel_links.append(href)
            
            downloaded_files = []
            
            for i, link in enumerate(excel_links[:5]):  # Limit to 5 files
                try:
                    logger.info(f"Downloading file: {link}")
                    file_response = self.session.get(link, timeout=60)
                    file_response.raise_for_status()
                    
                    filename = f"sebi_data_{i}.xlsx"
                    filepath = os.path.join('/tmp', filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(file_response.content)
                    
                    downloaded_files.append(filepath)
                    time.sleep(1)  # Be nice to the server
                    
                except Exception as e:
                    logger.error(f"Error downloading file {link}: {str(e)}")
                    continue
            
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Error downloading Excel files: {str(e)}")
            return []
    
    def parse_excel_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse Excel file containing advisor data"""
        try:
            advisors = []
            
            # Try different sheet names and formats
            df = pd.read_excel(filepath, sheet_name=None)  # Read all sheets
            
            for sheet_name, sheet_df in df.items():
                logger.info(f"Processing sheet: {sheet_name}")
                
                # Look for columns that might contain advisor names
                name_columns = ['name', 'advisor_name', 'intermediary_name', 'entity_name']
                name_col = None
                
                for col in sheet_df.columns:
                    if any(name_part in col.lower() for name_part in name_columns):
                        name_col = col
                        break
                
                if name_col is None:
                    # Use first column as name
                    name_col = sheet_df.columns[0]
                
                for index, row in sheet_df.iterrows():
                    try:
                        name = str(row[name_col]).strip()
                        if name and name != 'nan':
                            advisor_data = {
                                'name': name,
                                'registration_number': str(row.get('registration_no', row.get('reg_no', ''))).strip(),
                                'category': str(row.get('category', row.get('type', 'Investment Advisor'))).strip(),
                                'email': str(row.get('email', '')).strip(),
                                'status': 'Active'
                            }
                            advisors.append(advisor_data)
                    except Exception as e:
                        logger.debug(f"Error parsing row {index}: {str(e)}")
                        continue
            
            logger.info(f"Parsed {len(advisors)} advisors from {filepath}")
            return advisors
            
        except Exception as e:
            logger.error(f"Error parsing Excel file {filepath}: {str(e)}")
            return []
    
    def refresh_registry(self) -> Dict[str, Any]:
        """
        Refresh the SEBI registry data
        This method coordinates the entire scraping and updating process
        """
        try:
            logger.info("Starting SEBI registry refresh")
            
            from database import insert_intermediary
            
            total_advisors = 0
            
            # Method 1: Scrape web pages
            advisors_from_web = self.scrape_registry_page(self.registry_url)
            for advisor in advisors_from_web:
                if insert_intermediary(
                    advisor['name'], 
                    advisor.get('email'), 
                    advisor.get('registration_number'),
                    advisor.get('category'),
                    advisor.get('status')
                ):
                    total_advisors += 1
            
            # Method 2: Download and parse Excel files
            excel_files = self.download_excel_files()
            for filepath in excel_files:
                try:
                    advisors_from_excel = self.parse_excel_file(filepath)
                    for advisor in advisors_from_excel:
                        if insert_intermediary(
                            advisor['name'], 
                            advisor.get('email'), 
                            advisor.get('registration_number'),
                            advisor.get('category'),
                            advisor.get('status')
                        ):
                            total_advisors += 1
                    
                    # Clean up temporary file
                    os.unlink(filepath)
                    
                except Exception as e:
                    logger.error(f"Error processing Excel file {filepath}: {str(e)}")
                    continue
            
            # Add some sample data for demo purposes
            sample_advisors = [
                {"name": "ABC Investment Advisors", "registration_number": "INA000001234", "category": "Investment Advisor"},
                {"name": "XYZ Wealth Management", "registration_number": "INA000005678", "category": "Investment Advisor"},
                {"name": "SecureInvest Advisory", "registration_number": "INA000009012", "category": "Investment Advisor"},
                {"name": "TrustFund Advisors Ltd", "registration_number": "INA000003456", "category": "Investment Advisor"},
                {"name": "Elite Portfolio Management", "registration_number": "INA000007890", "category": "Portfolio Manager"}
            ]
            
            for advisor in sample_advisors:
                if insert_intermediary(
                    advisor['name'], 
                    None, 
                    advisor['registration_number'],
                    advisor['category']
                ):
                    total_advisors += 1
            
            logger.info(f"SEBI registry refresh completed. Total advisors: {total_advisors}")
            
            return {
                'success': True,
                'count': total_advisors,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error refreshing SEBI registry: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'count': 0
            }

def test_sebi_scraper():
    """Test the SEBI scraper"""
    scraper = SEBIScraper()
    
    # Test advisor check
    test_advisors = [
        "ABC Investment Advisors",
        "NonExistent Advisor",
        "XYZ Wealth Management"
    ]
    
    for advisor in test_advisors:
        is_registered = scraper.check_advisor_registration(advisor)
        print(f"Advisor: {advisor} - Registered: {is_registered}")
    
    # Test registry refresh
    result = scraper.refresh_registry()
    print(f"Registry refresh result: {result}")

if __name__ == "__main__":
    test_sebi_scraper()