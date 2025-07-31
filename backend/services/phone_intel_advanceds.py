# import asyncio
# import json
# import logging
# import os
# import csv
# import time
# import re
# import requests
# from datetime import datetime
# from typing import Dict, Any, Callable, Optional, List
# from urllib.parse import quote, urljoin
# import random
# from bs4 import BeautifulSoup
# import phonenumbers
# from phonenumbers import geocoder, carrier, timezone
# import whois
# import tldextract
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import httpx
# from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
# import google.generativeai as genai
# from googlesearch import search
# import aiohttp
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# import threading

# logger = logging.getLogger(__name__)

# class AdvancedPhoneIntelService:
#     def __init__(self):
#         self.session = requests.Session()
#         self.session.headers.update({
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
#         })
        
#         # API Keys from environment
#         self.numverify_key = os.getenv('NUMVERIFY_API_KEY')
#         self.veriphone_key = os.getenv('VERIPHONE_API_KEY')
#         self.abstractapi_key = os.getenv('ABSTRACTAPI_KEY')
#         self.whoisxml_key = os.getenv('WHOISXML_API_KEY')
#         self.hlrlookup_key = os.getenv('HLRLOOKUP_API_KEY')
#         self.serpapi_key = os.getenv('SERPAPI_KEY')
#         self.gemini_key = os.getenv('GEMINI_API_KEY')
        
#         # Configure Gemini
#         if self.gemini_key:
#             genai.configure(api_key=self.gemini_key)
#             self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
#         # Initialize HuggingFace models
#         try:
#             self.ner_pipeline = pipeline("ner", 
#                 model="dbmdz/bert-large-cased-finetuned-conll03-english",
#                 aggregation_strategy="simple"
#             )
#             self.sentiment_pipeline = pipeline("sentiment-analysis",
#                 model="distilbert-base-uncased-finetuned-sst-2-english"
#             )
#         except Exception as e:
#             logger.warning(f"Failed to load HuggingFace models: {e}")
#             self.ner_pipeline = None
#             self.sentiment_pipeline = None
        
#         # User agents for rotation
#         self.user_agents = [
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
#         ]

#     def get_random_headers(self):
#         """Get random headers for scraping"""
#         return {
#             'User-Agent': random.choice(self.user_agents),
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#             'Accept-Language': 'en-US,en;q=0.5',
#             'Accept-Encoding': 'gzip, deflate',
#             'Connection': 'keep-alive',
#             'Upgrade-Insecure-Requests': '1',
#         }

#     async def comprehensive_scan(self, phone_number: str, status_callback: Callable) -> Dict[str, Any]:
#         """Main comprehensive scan orchestrator"""
#         results = {
#             "phone_number": phone_number,
#             "scan_date": datetime.now().isoformat(),
#             "basic_info": {},
#             "geolocation": {},
#             "owner_spam": {},
#             "messaging_presence": {},
#             "social_media_profiles": {},
#             "breach_data": {},
#             "spam_reports": {},
#             "domain_whois": {},
#             "profile_images": {},
#             "number_reassignment": {},
#             "online_mentions": {},
#             "errors": []
#         }

#         # Enhanced feature scanning with multiple methods
#         features = [
#             ("basic_info", self.get_comprehensive_basic_info),
#             ("geolocation", self.get_comprehensive_geolocation),
#             ("owner_spam", self.get_comprehensive_owner_spam),
#             ("messaging", self.get_comprehensive_messaging_presence),
#             ("social_media", self.get_comprehensive_social_media),
#             ("breach_data", self.get_comprehensive_breach_data),
#             ("spam_reports", self.get_comprehensive_spam_reports),
#             ("domain_whois", self.get_comprehensive_domain_whois),
#             ("profile_images", self.get_comprehensive_profile_images),
#             ("reassignment", self.get_comprehensive_reassignment),
#             ("online_mentions", self.get_comprehensive_online_mentions)
#         ]

#         for feature_name, feature_func in features:
#             try:
#                 status_callback(feature_name, "running")
#                 logger.info(f"Starting comprehensive {feature_name} for {phone_number}")
                
#                 feature_data = await feature_func(phone_number)
#                 results[feature_name.replace("_", "_")] = feature_data
                
#                 # Save raw data
#                 clean_number = phone_number.replace('+', '').replace(' ', '')
#                 raw_file = f"output/raw/{clean_number}_{feature_name}.json"
#                 with open(raw_file, 'w') as f:
#                     json.dump(feature_data, f, indent=2, default=str)
                
#                 status_callback(feature_name, "success")
#                 logger.info(f"Completed comprehensive {feature_name} for {phone_number}")
                
#                 # Add delay between features to avoid rate limiting
#                 await asyncio.sleep(2)
                
#             except Exception as e:
#                 error_msg = f"Error in {feature_name}: {str(e)}"
#                 logger.error(error_msg)
#                 results["errors"].append({
#                     "feature": feature_name,
#                     "error": str(e),
#                     "timestamp": datetime.now().isoformat()
#                 })
#                 status_callback(feature_name, "failed")

#         return results

#     async def get_comprehensive_basic_info(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive basic phone info with multiple APIs and scrapers"""
#         result = {
#             "country_code": None, 
#             "region": None, 
#             "carrier_name": None, 
#             "line_type": None,
#             "is_valid": False,
#             "international_format": None,
#             "national_format": None,
#             "country_name": None
#         }
        
#         # Method 1: Numverify API
#         if self.numverify_key:
#             try:
#                 url = "http://apilayer.net/api/validate"
#                 params = {
#                     'access_key': self.numverify_key,
#                     'number': phone_number,
#                     'country_code': '',
#                     'format': 1
#                 }
#                 response = self.session.get(url, params=params, timeout=15)
#                 if response.status_code == 200:
#                     data = response.json()
#                     if data.get('valid'):
#                         result.update({
#                             "country_code": f"+{data.get('country_code')}",
#                             "region": data.get('location'),
#                             "carrier_name": data.get('carrier'),
#                             "line_type": data.get('line_type'),
#                             "is_valid": True,
#                             "international_format": data.get('international_format'),
#                             "national_format": data.get('national_format'),
#                             "country_name": data.get('country_name')
#                         })
#                         return result
#             except Exception as e:
#                 logger.warning(f"Numverify API failed: {e}")

#         # Method 2: Veriphone API
#         if self.veriphone_key:
#             try:
#                 url = "https://api.veriphone.io/v2/verify"
#                 params = {
#                     'key': self.veriphone_key,
#                     'phone': phone_number
#                 }
#                 response = self.session.get(url, params=params, timeout=15)
#                 if response.status_code == 200:
#                     data = response.json()
#                     if data.get('status') == 'success':
#                         phone_data = data.get('phone', {})
#                         result.update({
#                             "country_code": f"+{phone_data.get('country_code')}",
#                             "region": phone_data.get('location'),
#                             "carrier_name": phone_data.get('carrier'),
#                             "line_type": phone_data.get('phone_type'),
#                             "is_valid": phone_data.get('phone_valid', False),
#                             "international_format": phone_data.get('international_format'),
#                             "country_name": phone_data.get('country')
#                         })
#                         return result
#             except Exception as e:
#                 logger.warning(f"Veriphone API failed: {e}")

#         # Method 3: AbstractAPI
#         if self.abstractapi_key:
#             try:
#                 url = "https://phonevalidation.abstractapi.com/v1/"
#                 params = {
#                     'api_key': self.abstractapi_key,
#                     'phone': phone_number
#                 }
#                 response = self.session.get(url, params=params, timeout=15)
#                 if response.status_code == 200:
#                     data = response.json()
#                     if data.get('valid'):
#                         result.update({
#                             "country_code": data.get('country', {}).get('code'),
#                             "region": data.get('location'),
#                             "carrier_name": data.get('carrier'),
#                             "line_type": data.get('type'),
#                             "is_valid": True,
#                             "international_format": data.get('format', {}).get('international'),
#                             "national_format": data.get('format', {}).get('national'),
#                             "country_name": data.get('country', {}).get('name')
#                         })
#                         return result
#             except Exception as e:
#                 logger.warning(f"AbstractAPI failed: {e}")

#         # Fallback 1: phonenumbers library
#         try:
#             parsed = phonenumbers.parse(phone_number, None)
#             if phonenumbers.is_valid_number(parsed):
#                 result.update({
#                     "country_code": f"+{parsed.country_code}",
#                     "region": geocoder.description_for_number(parsed, "en"),
#                     "carrier_name": carrier.name_for_number(parsed, "en"),
#                     "line_type": "mobile" if phonenumbers.number_type(parsed) in [0, 1] else "landline",
#                     "is_valid": True,
#                     "international_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
#                     "national_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
#                 })
                
#                 # Get country name
#                 country_code = phonenumbers.region_code_for_number(parsed)
#                 if country_code:
#                     result["country_name"] = country_code
                
#                 return result
#         except Exception as e:
#             logger.warning(f"phonenumbers library failed: {e}")

#         # Fallback 2: Scrape carrier lookup sites
#         await self.scrape_multiple_carrier_sites(phone_number, result)

#         # Fallback 3: Use Gemini AI for analysis
#         if self.gemini_key and not result.get("carrier_name"):
#             try:
#                 prompt = f"Analyze this phone number: {phone_number}. Provide carrier, country, region, and line type information."
#                 response = self.gemini_model.generate_content(prompt)
#                 # Parse AI response and extract relevant info
#                 ai_text = response.text
#                 if "carrier" in ai_text.lower():
#                     # Extract carrier info using regex or NLP
#                     pass
#             except Exception as e:
#                 logger.warning(f"Gemini AI analysis failed: {e}")

#         return result

#     async def scrape_multiple_carrier_sites(self, phone_number: str, result: Dict):
#         """Scrape multiple carrier lookup sites"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         sites = [
#             {
#                 'url': f'https://www.freecarrierlookup.com/lookup.php?number={clean_number}',
#                 'parser': self.parse_freecarrierlookup
#             },
#             {
#                 'url': f'https://www.carrierlookup.com/index.php/lookup/carrier?msisdn={clean_number}',
#                 'parser': self.parse_carrierlookup
#             },
#             {
#                 'url': f'https://www.truecaller.com/search/in/{clean_number}',
#                 'parser': self.parse_truecaller_basic
#             }
#         ]
        
#         for site in sites:
#             try:
#                 headers = self.get_random_headers()
#                 response = self.session.get(site['url'], headers=headers, timeout=15)
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
#                     site['parser'](soup, result)
#                     if result.get('carrier_name'):
#                         break
#                 await asyncio.sleep(random.uniform(1, 3))
#             except Exception as e:
#                 logger.warning(f"Failed to scrape {site['url']}: {e}")

#     def parse_freecarrierlookup(self, soup: BeautifulSoup, result: Dict):
#         """Parse freecarrierlookup.com results"""
#         try:
#             carrier_elem = soup.find('td', string=re.compile('Carrier', re.I))
#             if carrier_elem:
#                 carrier_value = carrier_elem.find_next_sibling('td')
#                 if carrier_value:
#                     result['carrier_name'] = carrier_value.get_text(strip=True)
            
#             location_elem = soup.find('td', string=re.compile('Location', re.I))
#             if location_elem:
#                 location_value = location_elem.find_next_sibling('td')
#                 if location_value:
#                     result['region'] = location_value.get_text(strip=True)
#         except Exception as e:
#             logger.warning(f"Error parsing freecarrierlookup: {e}")

#     def parse_carrierlookup(self, soup: BeautifulSoup, result: Dict):
#         """Parse carrierlookup.com results"""
#         try:
#             # Look for carrier information in various formats
#             carrier_patterns = [
#                 r'Carrier[:\s]+([^<\n]+)',
#                 r'Network[:\s]+([^<\n]+)',
#                 r'Operator[:\s]+([^<\n]+)'
#             ]
            
#             text = soup.get_text()
#             for pattern in carrier_patterns:
#                 match = re.search(pattern, text, re.I)
#                 if match:
#                     result['carrier_name'] = match.group(1).strip()
#                     break
#         except Exception as e:
#             logger.warning(f"Error parsing carrierlookup: {e}")

#     def parse_truecaller_basic(self, soup: BeautifulSoup, result: Dict):
#         """Parse basic Truecaller info"""
#         try:
#             # Look for carrier/operator info
#             operator_elem = soup.find(string=re.compile('operator', re.I))
#             if operator_elem:
#                 parent = operator_elem.parent
#                 if parent:
#                     result['carrier_name'] = parent.get_text(strip=True)
#         except Exception as e:
#             logger.warning(f"Error parsing Truecaller basic: {e}")

#     async def get_comprehensive_geolocation(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive geolocation data with multiple sources"""
#         result = {
#             "city": None, 
#             "state": None, 
#             "timezone": None, 
#             "latitude": None, 
#             "longitude": None,
#             "country": None,
#             "region": None,
#             "postal_code": None
#         }
        
#         # Method 1: phonenumbers library
#         try:
#             parsed = phonenumbers.parse(phone_number, None)
#             if phonenumbers.is_valid_number(parsed):
#                 # Get timezone
#                 timezones = timezone.time_zones_for_number(parsed)
#                 if timezones:
#                     result["timezone"] = list(timezones)[0]
                
#                 # Get location description
#                 location = geocoder.description_for_number(parsed, "en")
#                 if location:
#                     result["region"] = location
#                     # Try to parse city/state from location
#                     if ", " in location:
#                         parts = location.split(", ")
#                         if len(parts) >= 2:
#                             result["city"] = parts[0]
#                             result["state"] = parts[1]
                    
#                 # Get country
#                 country_code = phonenumbers.region_code_for_number(parsed)
#                 if country_code:
#                     result["country"] = country_code
#         except Exception as e:
#             logger.warning(f"phonenumbers geolocation failed: {e}")

#         # Method 2: Scrape location databases
#         await self.scrape_location_databases(phone_number, result)
        
#         # Method 3: Use area code databases
#         await self.lookup_area_code_database(phone_number, result)
        
#         # Method 4: Gemini AI for location analysis
#         if self.gemini_key and not result.get("city"):
#             try:
#                 prompt = f"What city and state/region is phone number {phone_number} from? Provide specific location details."
#                 response = self.gemini_model.generate_content(prompt)
#                 ai_text = response.text
#                 # Parse AI response for location info
#                 await self.parse_ai_location_response(ai_text, result)
#             except Exception as e:
#                 logger.warning(f"Gemini location analysis failed: {e}")

#         return result

#     async def scrape_location_databases(self, phone_number: str, result: Dict):
#         """Scrape multiple location databases"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         # Extract area code for US numbers
#         if clean_number.startswith('1') and len(clean_number) == 11:
#             area_code = clean_number[1:4]
            
#             # Scrape area code databases
#             sites = [
#                 f'https://www.allareacodes.com/{area_code}',
#                 f'https://www.areacodehelp.com/where/area_code_{area_code}.shtml',
#                 f'https://www.whitepages.com/phone/1-{area_code}'
#             ]
            
#             for site in sites:
#                 try:
#                     headers = self.get_random_headers()
#                     response = self.session.get(site, headers=headers, timeout=15)
#                     if response.status_code == 200:
#                         soup = BeautifulSoup(response.content, 'html.parser')
#                         self.parse_area_code_info(soup, result)
#                         if result.get('city'):
#                             break
#                     await asyncio.sleep(random.uniform(1, 2))
#                 except Exception as e:
#                     logger.warning(f"Failed to scrape {site}: {e}")

#     def parse_area_code_info(self, soup: BeautifulSoup, result: Dict):
#         """Parse area code information from scraped pages"""
#         try:
#             # Look for city/state patterns
#             text = soup.get_text()
            
#             # Common patterns for location info
#             patterns = [
#                 r'(?:City|Cities)[:\s]+([^,\n]+),?\s*([^,\n]+)',
#                 r'(?:Location|Area)[:\s]+([^,\n]+),?\s*([^,\n]+)',
#                 r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})',
#             ]
            
#             for pattern in patterns:
#                 matches = re.findall(pattern, text)
#                 if matches:
#                     city, state = matches[0]
#                     result['city'] = city.strip()
#                     result['state'] = state.strip()
#                     break
#         except Exception as e:
#             logger.warning(f"Error parsing area code info: {e}")

#     async def lookup_area_code_database(self, phone_number: str, result: Dict):
#         """Lookup area code in local database or API"""
#         # This would use a local area code database
#         # For now, implement basic US area code mapping
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         if clean_number.startswith('1') and len(clean_number) == 11:
#             area_code = clean_number[1:4]
            
#             # Basic area code to location mapping (sample)
#             area_code_map = {
#                 '212': {'city': 'New York', 'state': 'NY'},
#                 '213': {'city': 'Los Angeles', 'state': 'CA'},
#                 '312': {'city': 'Chicago', 'state': 'IL'},
#                 '415': {'city': 'San Francisco', 'state': 'CA'},
#                 '713': {'city': 'Houston', 'state': 'TX'},
#                 '305': {'city': 'Miami', 'state': 'FL'},
#                 '404': {'city': 'Atlanta', 'state': 'GA'},
#                 '617': {'city': 'Boston', 'state': 'MA'},
#                 '206': {'city': 'Seattle', 'state': 'WA'},
#                 '702': {'city': 'Las Vegas', 'state': 'NV'},
#                 # Add more mappings as needed
#             }
            
#             if area_code in area_code_map:
#                 location_info = area_code_map[area_code]
#                 if not result.get('city'):
#                     result['city'] = location_info['city']
#                 if not result.get('state'):
#                     result['state'] = location_info['state']

#     async def parse_ai_location_response(self, ai_text: str, result: Dict):
#         """Parse AI response for location information"""
#         try:
#             # Use NER to extract location entities
#             if self.ner_pipeline:
#                 entities = self.ner_pipeline(ai_text)
#                 for entity in entities:
#                     if entity['entity_group'] == 'LOC':
#                         location = entity['word']
#                         if not result.get('city') and len(location.split()) <= 2:
#                             result['city'] = location
#                         elif not result.get('state') and len(location) == 2:
#                             result['state'] = location
#         except Exception as e:
#             logger.warning(f"Error parsing AI location response: {e}")

#     async def get_comprehensive_owner_spam(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive owner name and spam information"""
#         result = {
#             "caller_name": None, 
#             "spam_score": 0.0, 
#             "spam_tags": [],
#             "caller_type": None,
#             "business_name": None,
#             "reputation_score": None,
#             "report_count": 0
#         }
        
#         # Method 1: Scrape Truecaller with multiple approaches
#         await self.scrape_truecaller_comprehensive(phone_number, result)
        
#         # Method 2: Scrape other caller ID sites
#         await self.scrape_multiple_caller_id_sites(phone_number, result)
        
#         # Method 3: Use Selenium for dynamic content
#         await self.scrape_with_selenium(phone_number, result)
        
#         # Method 4: Use NER on scraped text
#         if result.get('caller_name') and self.ner_pipeline:
#             try:
#                 entities = self.ner_pipeline(result['caller_name'])
#                 for entity in entities:
#                     if entity['entity_group'] == 'PER':
#                         result['caller_name'] = entity['word']
#                         break
#             except Exception as e:
#                 logger.warning(f"NER processing failed: {e}")

#         return result

#     async def scrape_truecaller_comprehensive(self, phone_number: str, result: Dict):
#         """Comprehensive Truecaller scraping with multiple methods"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         urls = [
#             f'https://www.truecaller.com/search/in/{clean_number}',
#             f'https://www.truecaller.com/search/us/{clean_number}',
#             f'https://www.truecaller.com/search/global/{clean_number}'
#         ]
        
#         for url in urls:
#             try:
#                 headers = self.get_random_headers()
#                 headers['Referer'] = 'https://www.truecaller.com/'
                
#                 response = self.session.get(url, headers=headers, timeout=20)
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
                    
#                     # Look for caller name
#                     name_selectors = [
#                         'h1[data-test-id="search-result-name"]',
#                         '.search-result-name',
#                         '.caller-name',
#                         'h1.name'
#                     ]
                    
#                     for selector in name_selectors:
#                         name_elem = soup.select_one(selector)
#                         if name_elem:
#                             result['caller_name'] = name_elem.get_text(strip=True)
#                             break
                    
#                     # Look for spam indicators
#                     spam_indicators = soup.find_all(string=re.compile(r'spam|scam|fraud|telemarketer', re.I))
#                     if spam_indicators:
#                         result['spam_score'] = min(len(spam_indicators) * 0.2, 1.0)
#                         result['spam_tags'] = list(set([indicator.strip().lower() for indicator in spam_indicators[:5]]))
                    
#                     if result.get('caller_name'):
#                         break
                        
#                 await asyncio.sleep(random.uniform(2, 4))
#             except Exception as e:
#                 logger.warning(f"Truecaller scraping failed for {url}: {e}")

#     async def scrape_multiple_caller_id_sites(self, phone_number: str, result: Dict):
#         """Scrape multiple caller ID and spam reporting sites"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         sites = [
#             {
#                 'url': f'https://www.whocalld.com/+{clean_number}',
#                 'parser': self.parse_whocalld
#             },
#             {
#                 'url': f'https://www.shouldianswer.com/phone-number/{clean_number}',
#                 'parser': self.parse_shouldianswer
#             },
#             {
#                 'url': f'https://www.callercenter.com/number/{clean_number}',
#                 'parser': self.parse_callercenter
#             },
#             {
#                 'url': f'https://www.spamcalls.net/en/number/{clean_number}',
#                 'parser': self.parse_spamcalls
#             }
#         ]
        
#         for site in sites:
#             try:
#                 headers = self.get_random_headers()
#                 response = self.session.get(site['url'], headers=headers, timeout=15)
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
#                     site['parser'](soup, result)
                    
#                 await asyncio.sleep(random.uniform(1, 3))
#             except Exception as e:
#                 logger.warning(f"Failed to scrape {site['url']}: {e}")

#     def parse_whocalld(self, soup: BeautifulSoup, result: Dict):
#         """Parse whocalld.com results"""
#         try:
#             # Look for caller name
#             name_elem = soup.find('h1', class_='caller-name')
#             if not name_elem:
#                 name_elem = soup.find('div', class_='caller-info')
            
#             if name_elem:
#                 name = name_elem.get_text(strip=True)
#                 if name and not result.get('caller_name'):
#                     result['caller_name'] = name
            
#             # Look for spam indicators
#             spam_elem = soup.find('div', class_='spam-score')
#             if spam_elem:
#                 spam_text = spam_elem.get_text(strip=True)
#                 if 'spam' in spam_text.lower():
#                     result['spam_score'] = 0.8
#                     result['spam_tags'].append('reported_spam')
#         except Exception as e:
#             logger.warning(f"Error parsing whocalld: {e}")

#     def parse_shouldianswer(self, soup: BeautifulSoup, result: Dict):
#         """Parse shouldianswer.com results"""
#         try:
#             # Look for caller information
#             caller_elem = soup.find('div', class_='caller-details')
#             if caller_elem:
#                 name = caller_elem.get_text(strip=True)
#                 if name and not result.get('caller_name'):
#                     result['caller_name'] = name
            
#             # Check for negative ratings
#             rating_elem = soup.find('div', class_='rating')
#             if rating_elem:
#                 rating_text = rating_elem.get_text(strip=True)
#                 if any(word in rating_text.lower() for word in ['negative', 'spam', 'scam']):
#                     result['spam_score'] = 0.7
#                     result['spam_tags'].append('negative_rating')
#         except Exception as e:
#             logger.warning(f"Error parsing shouldianswer: {e}")

#     def parse_callercenter(self, soup: BeautifulSoup, result: Dict):
#         """Parse callercenter.com results"""
#         try:
#             # Look for caller name in various elements
#             name_selectors = ['h1.caller-name', '.caller-info h2', '.number-info .name']
#             for selector in name_selectors:
#                 name_elem = soup.select_one(selector)
#                 if name_elem:
#                     name = name_elem.get_text(strip=True)
#                     if name and not result.get('caller_name'):
#                         result['caller_name'] = name
#                         break
#         except Exception as e:
#             logger.warning(f"Error parsing callercenter: {e}")

#     def parse_spamcalls(self, soup: BeautifulSoup, result: Dict):
#         """Parse spamcalls.net results"""
#         try:
#             # Look for spam classification
#             spam_elem = soup.find('div', class_='spam-classification')
#             if spam_elem:
#                 classification = spam_elem.get_text(strip=True).lower()
#                 if 'spam' in classification:
#                     result['spam_score'] = 0.9
#                     result['spam_tags'].append('classified_spam')
#                 elif 'scam' in classification:
#                     result['spam_score'] = 0.95
#                     result['spam_tags'].append('classified_scam')
#         except Exception as e:
#             logger.warning(f"Error parsing spamcalls: {e}")

#     async def scrape_with_selenium(self, phone_number: str, result: Dict):
#         """Use Selenium for dynamic content scraping"""
#         try:
#             options = Options()
#             options.add_argument('--headless')
#             options.add_argument('--no-sandbox')
#             options.add_argument('--disable-dev-shm-usage')
#             options.add_argument('--disable-gpu')
#             options.add_argument('--window-size=1920,1080')
#             options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
            
#             driver = webdriver.Chrome(options=options)
            
#             try:
#                 clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
#                 url = f'https://www.truecaller.com/search/in/{clean_number}'
                
#                 driver.get(url)
#                 wait = WebDriverWait(driver, 10)
                
#                 # Wait for content to load
#                 try:
#                     name_element = wait.until(
#                         EC.presence_of_element_located((By.CSS_SELECTOR, 'h1, .caller-name, .search-result-name'))
#                     )
#                     if name_element:
#                         name = name_element.text.strip()
#                         if name and not result.get('caller_name'):
#                             result['caller_name'] = name
#                 except TimeoutException:
#                     pass
                
#                 # Look for spam indicators
#                 try:
#                     spam_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'spam') or contains(text(), 'scam')]")
#                     if spam_elements:
#                         result['spam_score'] = 0.8
#                         result['spam_tags'].append('selenium_detected_spam')
#                 except:
#                     pass
                    
#             finally:
#                 driver.quit()
                
#         except Exception as e:
#             logger.warning(f"Selenium scraping failed: {e}")

#     async def get_comprehensive_messaging_presence(self, phone_number: str) -> Dict[str, Any]:
#         """Check comprehensive messaging app presence"""
#         result = {
#             "whatsapp_active": None, 
#             "telegram_active": None,
#             "signal_active": None,
#             "viber_active": None,
#             "messenger_active": None
#         }
        
#         # Method 1: WhatsApp Web scraping
#         await self.check_whatsapp_presence(phone_number, result)
        
#         # Method 2: Telegram username search
#         await self.check_telegram_presence(phone_number, result)
        
#         # Method 3: Other messaging apps
#         await self.check_other_messaging_apps(phone_number, result)

#         return result

#     async def check_whatsapp_presence(self, phone_number: str, result: Dict):
#         """Check WhatsApp presence using web scraping"""
#         try:
#             # This is a simplified check - in practice, WhatsApp has strong anti-bot measures
#             # You would need to use WhatsApp Business API or similar
#             clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
#             # Try to access WhatsApp web with the number
#             options = Options()
#             options.add_argument('--headless')
#             options.add_argument('--no-sandbox')
#             options.add_argument('--disable-dev-shm-usage')
            
#             driver = webdriver.Chrome(options=options)
            
#             try:
#                 # This is a placeholder - actual WhatsApp checking requires more complex logic
#                 url = f'https://wa.me/{clean_number}'
#                 driver.get(url)
                
#                 # Check if the page loads successfully (indicates valid WhatsApp number)
#                 if "WhatsApp" in driver.title:
#                     result['whatsapp_active'] = True
#                 else:
#                     result['whatsapp_active'] = False
                    
#             finally:
#                 driver.quit()
                
#         except Exception as e:
#             logger.warning(f"WhatsApp presence check failed: {e}")
#             result['whatsapp_active'] = None

#     async def check_telegram_presence(self, phone_number: str, result: Dict):
#         """Check Telegram presence"""
#         try:
#             # Search for Telegram usernames associated with the phone number
#             # This would require Telegram API access
#             # For now, implement basic search
            
#             search_queries = [
#                 f'"{phone_number}" site:t.me',
#                 f'"{phone_number}" telegram',
#                 f'"{phone_number}" @'
#             ]
            
#             for query in search_queries:
#                 try:
#                     # Use Google search to find Telegram links
#                     search_results = list(search(query, num_results=5, stop=5))
#                     for url in search_results:
#                         if 't.me' in url or 'telegram' in url.lower():
#                             result['telegram_active'] = True
#                             return
#                     await asyncio.sleep(2)
#                 except Exception as e:
#                     logger.warning(f"Telegram search failed: {e}")
            
#             result['telegram_active'] = False
            
#         except Exception as e:
#             logger.warning(f"Telegram presence check failed: {e}")
#             result['telegram_active'] = None

#     async def check_other_messaging_apps(self, phone_number: str, result: Dict):
#         """Check other messaging apps presence"""
#         try:
#             # Search for presence on other platforms
#             apps = ['signal', 'viber', 'messenger']
            
#             for app in apps:
#                 search_query = f'"{phone_number}" {app}'
#                 try:
#                     search_results = list(search(search_query, num_results=3, stop=3))
#                     if search_results:
#                         result[f'{app}_active'] = True
#                     else:
#                         result[f'{app}_active'] = False
#                     await asyncio.sleep(2)
#                 except Exception as e:
#                     logger.warning(f"{app} search failed: {e}")
#                     result[f'{app}_active'] = None
                    
#         except Exception as e:
#             logger.warning(f"Other messaging apps check failed: {e}")

#     async def get_comprehensive_social_media(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive social media profiles"""
#         result = {
#             "instagram_url": None, 
#             "twitter_url": None, 
#             "facebook_url": None,
#             "linkedin_url": None,
#             "tiktok_url": None,
#             "snapchat_url": None,
#             "youtube_url": None
#         }
        
#         # Method 1: Google dork searches
#         await self.google_dork_social_search(phone_number, result)
        
#         # Method 2: Direct platform searches
#         await self.direct_platform_searches(phone_number, result)
        
#         # Method 3: Use SerpAPI if available
#         if self.serpapi_key:
#             await self.serpapi_social_search(phone_number, result)

#         return result

#     async def google_dork_social_search(self, phone_number: str, result: Dict):
#         """Perform Google dork searches for social media"""
#         platforms = {
#             'instagram': 'instagram.com',
#             'twitter': 'twitter.com OR x.com',
#             'facebook': 'facebook.com',
#             'linkedin': 'linkedin.com',
#             'tiktok': 'tiktok.com',
#             'snapchat': 'snapchat.com',
#             'youtube': 'youtube.com'
#         }
        
#         for platform, site in platforms.items():
#             search_queries = [
#                 f'"{phone_number}" site:{site}',
#                 f'"{phone_number}" {platform}',
#                 f'{phone_number} inurl:{site}'
#             ]
            
#             for query in search_queries:
#                 try:
#                     search_results = list(search(query, num_results=5, stop=5))
#                     for url in search_results:
#                         if site.split()[0] in url:  # Handle OR conditions
#                             result[f'{platform}_url'] = url
#                             break
                    
#                     if result.get(f'{platform}_url'):
#                         break
                        
#                     await asyncio.sleep(random.uniform(2, 4))
#                 except Exception as e:
#                     logger.warning(f"Google search failed for {platform}: {e}")

#     async def direct_platform_searches(self, phone_number: str, result: Dict):
#         """Direct searches on social media platforms"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         # Instagram search
#         try:
#             headers = self.get_random_headers()
#             # Instagram doesn't allow direct phone number searches, but we can try user search
#             # This is a placeholder for more complex Instagram API integration
#             pass
#         except Exception as e:
#             logger.warning(f"Instagram direct search failed: {e}")
        
#         # Twitter/X search
#         try:
#             # Twitter API would be needed for proper search
#             # This is a placeholder
#             pass
#         except Exception as e:
#             logger.warning(f"Twitter direct search failed: {e}")

#     async def serpapi_social_search(self, phone_number: str, result: Dict):
#         """Use SerpAPI for social media searches"""
#         if not self.serpapi_key:
#             return
            
#         try:
#             import serpapi
            
#             platforms = ['instagram', 'twitter', 'facebook', 'linkedin']
            
#             for platform in platforms:
#                 params = {
#                     "engine": "google",
#                     "q": f'"{phone_number}" site:{platform}.com',
#                     "api_key": self.serpapi_key,
#                     "num": 5
#                 }
                
#                 search = serpapi.GoogleSearch(params)
#                 results = search.get_dict()
                
#                 if 'organic_results' in results:
#                     for organic_result in results['organic_results']:
#                         link = organic_result.get('link', '')
#                         if platform in link:
#                             result[f'{platform}_url'] = link
#                             break
                
#                 await asyncio.sleep(1)
                
#         except Exception as e:
#             logger.warning(f"SerpAPI social search failed: {e}")

#     async def get_comprehensive_breach_data(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive breach data"""
#         result = {
#             "breached_emails": [], 
#             "breach_dates": [],
#             "breach_sources": [],
#             "data_types_exposed": [],
#             "severity_score": 0.0
#         }
        
#         # Method 1: Search public breach databases
#         await self.search_public_breach_databases(phone_number, result)
        
#         # Method 2: Check HaveIBeenPwned style databases
#         await self.check_hibp_style_databases(phone_number, result)
        
#         # Method 3: Search paste sites
#         await self.search_paste_sites(phone_number, result)

#         return result

#     async def search_public_breach_databases(self, phone_number: str, result: Dict):
#         """Search public breach databases"""
#         try:
#             # Search for phone number in breach data
#             search_queries = [
#                 f'"{phone_number}" breach database',
#                 f'"{phone_number}" data leak',
#                 f'"{phone_number}" exposed data',
#                 f'"{phone_number}" site:pastebin.com',
#                 f'"{phone_number}" site:ghostbin.com'
#             ]
            
#             for query in search_queries:
#                 try:
#                     search_results = list(search(query, num_results=10, stop=10))
#                     for url in search_results:
#                         if any(site in url for site in ['pastebin', 'ghostbin', 'leak', 'breach']):
#                             # Scrape the page for breach information
#                             await self.scrape_breach_page(url, result)
                    
#                     await asyncio.sleep(random.uniform(2, 4))
#                 except Exception as e:
#                     logger.warning(f"Breach database search failed: {e}")
                    
#         except Exception as e:
#             logger.warning(f"Public breach database search failed: {e}")

#     async def scrape_breach_page(self, url: str, result: Dict):
#         """Scrape individual breach pages"""
#         try:
#             headers = self.get_random_headers()
#             response = self.session.get(url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 text = soup.get_text()
                
#                 # Look for email patterns
#                 email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#                 emails = re.findall(email_pattern, text)
                
#                 if emails:
#                     result['breached_emails'].extend(emails[:5])  # Limit to 5 emails
#                     result['breach_sources'].append(url)
#                     result['breach_dates'].append(datetime.now().strftime('%Y-%m-%d'))
                    
#         except Exception as e:
#             logger.warning(f"Failed to scrape breach page {url}: {e}")

#     async def check_hibp_style_databases(self, phone_number: str, result: Dict):
#         """Check HaveIBeenPwned style databases"""
#         try:
#             # This would integrate with breach checking APIs
#             # For now, implement basic search
#             pass
#         except Exception as e:
#             logger.warning(f"HIBP style database check failed: {e}")

#     async def search_paste_sites(self, phone_number: str, result: Dict):
#         """Search paste sites for phone number"""
#         paste_sites = [
#             'pastebin.com',
#             'ghostbin.com',
#             'justpaste.it',
#             'paste.ee'
#         ]
        
#         for site in paste_sites:
#             try:
#                 search_query = f'"{phone_number}" site:{site}'
#                 search_results = list(search(search_query, num_results=5, stop=5))
                
#                 for url in search_results:
#                     await self.scrape_breach_page(url, result)
                
#                 await asyncio.sleep(random.uniform(2, 3))
#             except Exception as e:
#                 logger.warning(f"Paste site search failed for {site}: {e}")

#     async def get_comprehensive_spam_reports(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive spam/fraud reports"""
#         result = {
#             "report_sources": [], 
#             "report_texts": [], 
#             "sentiment_score": None,
#             "spam_categories": [],
#             "report_count": 0,
#             "latest_report_date": None
#         }
        
#         # Method 1: Scrape 800notes.com
#         await self.scrape_800notes_comprehensive(phone_number, result)
        
#         # Method 2: Scrape who-called.me
#         await self.scrape_who_called_comprehensive(phone_number, result)
        
#         # Method 3: Scrape additional spam reporting sites
#         await self.scrape_additional_spam_sites(phone_number, result)
        
#         # Method 4: Analyze sentiment of collected reports
#         if result['report_texts'] and self.sentiment_pipeline:
#             await self.analyze_report_sentiment(result)

#         return result

#     async def scrape_800notes_comprehensive(self, phone_number: str, result: Dict):
#         """Comprehensive 800notes.com scraping"""
#         try:
#             clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
#             # Try different URL formats
#             urls = [
#                 f"https://800notes.com/Phone.aspx/{clean_number}",
#                 f"https://www.800notes.com/Phone.aspx/{clean_number}",
#                 f"https://800notes.com/Phone.aspx/{clean_number[1:]}" if clean_number.startswith('1') else None
#             ]
            
#             for url in urls:
#                 if not url:
#                     continue
                    
#                 try:
#                     headers = self.get_random_headers()
#                     response = self.session.get(url, headers=headers, timeout=15)
                    
#                     if response.status_code == 200:
#                         soup = BeautifulSoup(response.content, 'html.parser')
                        
#                         # Look for reports
#                         report_elements = soup.find_all(['div', 'p'], class_=re.compile(r'report|comment|review', re.I))
                        
#                         for elem in report_elements:
#                             text = elem.get_text(strip=True)
#                             if text and len(text) > 20:  # Filter out short texts
#                                 result['report_texts'].append(text)
#                                 result['report_sources'].append('800notes.com')
#                                 result['report_count'] += 1
                        
#                         # Look for spam categories
#                         category_elements = soup.find_all(string=re.compile(r'spam|scam|telemarketer|robocall|fraud', re.I))
#                         for category in category_elements:
#                             category_clean = category.strip().lower()
#                             if category_clean not in result['spam_categories']:
#                                 result['spam_categories'].append(category_clean)
                        
#                         if result['report_texts']:
#                             break
                            
#                 except Exception as e:
#                     logger.warning(f"Failed to scrape {url}: {e}")
                    
#         except Exception as e:
#             logger.warning(f"800notes comprehensive scraping failed: {e}")

#     async def scrape_who_called_comprehensive(self, phone_number: str, result: Dict):
#         """Comprehensive who-called.me scraping"""
#         try:
#             clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
#             url = f"https://who-called.me/{clean_number}"
            
#             headers = self.get_random_headers()
#             response = self.session.get(url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
                
#                 # Look for user reports
#                 report_elements = soup.find_all(['div', 'article'], class_=re.compile(r'report|comment|user', re.I))
                
#                 for elem in report_elements:
#                     text = elem.get_text(strip=True)
#                     if text and len(text) > 30:
#                         result['report_texts'].append(text)
#                         result['report_sources'].append('who-called.me')
#                         result['report_count'] += 1
                
#                 # Look for dates
#                 date_elements = soup.find_all(string=re.compile(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}'))
#                 if date_elements:
#                     result['latest_report_date'] = date_elements[0].strip()
                    
#         except Exception as e:
#             logger.warning(f"who-called.me comprehensive scraping failed: {e}")

#     async def scrape_additional_spam_sites(self, phone_number: str, result: Dict):
#         """Scrape additional spam reporting sites"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         sites = [
#             {
#                 'url': f'https://www.shouldianswer.com/phone-number/{clean_number}',
#                 'name': 'shouldianswer.com'
#             },
#             {
#                 'url': f'https://www.spamcalls.net/en/number/{clean_number}',
#                 'name': 'spamcalls.net'
#             },
#             {
#                 'url': f'https://www.callercenter.com/number/{clean_number}',
#                 'name': 'callercenter.com'
#             },
#             {
#                 'url': f'https://www.unknownphone.com/phone-number/{clean_number}',
#                 'name': 'unknownphone.com'
#             }
#         ]
        
#         for site in sites:
#             try:
#                 headers = self.get_random_headers()
#                 response = self.session.get(site['url'], headers=headers, timeout=15)
                
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
                    
#                     # Generic report extraction
#                     text_elements = soup.find_all(['p', 'div', 'span'], string=re.compile(r'.{20,}'))
                    
#                     for elem in text_elements:
#                         text = elem.get_text(strip=True)
#                         if any(keyword in text.lower() for keyword in ['spam', 'scam', 'telemarketer', 'robocall']):
#                             result['report_texts'].append(text)
#                             result['report_sources'].append(site['name'])
#                             result['report_count'] += 1
                
#                 await asyncio.sleep(random.uniform(1, 3))
                
#             except Exception as e:
#                 logger.warning(f"Failed to scrape {site['name']}: {e}")

#     async def analyze_report_sentiment(self, result: Dict):
#         """Analyze sentiment of collected reports"""
#         try:
#             if not result['report_texts']:
#                 return
                
#             # Combine all report texts
#             combined_text = ' '.join(result['report_texts'][:10])  # Limit to first 10 reports
            
#             # Analyze sentiment
#             sentiment_result = self.sentiment_pipeline(combined_text[:512])  # Limit text length
            
#             if sentiment_result:
#                 sentiment = sentiment_result[0]
#                 result['sentiment_score'] = sentiment['score'] if sentiment['label'] == 'NEGATIVE' else 1 - sentiment['score']
                
#         except Exception as e:
#             logger.warning(f"Sentiment analysis failed: {e}")

#     async def get_comprehensive_domain_whois(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive domain/WHOIS information"""
#         result = {
#             "linked_domains": [], 
#             "whois_registrar": None, 
#             "creation_date": None,
#             "domain_count": 0,
#             "business_domains": [],
#             "suspicious_domains": []
#         }
        
#         # Method 1: Search for domains with phone number
#         await self.search_domains_with_phone(phone_number, result)
        
#         # Method 2: WHOIS reverse lookup
#         await self.whois_reverse_lookup(phone_number, result)
        
#         # Method 3: Business directory search
#         await self.search_business_directories(phone_number, result)

#         return result

#     async def search_domains_with_phone(self, phone_number: str, result: Dict):
#         """Search for domains containing the phone number"""
#         try:
#             search_queries = [
#                 f'"{phone_number}" site:*.com',
#                 f'"{phone_number}" site:*.org',
#                 f'"{phone_number}" site:*.net',
#                 f'"{phone_number}" contact phone',
#                 f'"{phone_number}" whois'
#             ]
            
#             for query in search_queries:
#                 try:
#                     search_results = list(search(query, num_results=10, stop=10))
                    
#                     for url in search_results:
#                         domain = tldextract.extract(url).registered_domain
#                         if domain and domain not in result['linked_domains']:
#                             result['linked_domains'].append(domain)
#                             result['domain_count'] += 1
                            
#                             # Check if domain seems business-related
#                             if any(word in domain.lower() for word in ['business', 'company', 'corp', 'inc', 'llc']):
#                                 result['business_domains'].append(domain)
                            
#                             # Check for suspicious patterns
#                             if any(word in domain.lower() for word in ['temp', 'fake', 'scam', 'spam']):
#                                 result['suspicious_domains'].append(domain)
                    
#                     await asyncio.sleep(random.uniform(2, 4))
#                 except Exception as e:
#                     logger.warning(f"Domain search failed for query: {e}")
                    
#         except Exception as e:
#             logger.warning(f"Domain search with phone failed: {e}")

#     async def whois_reverse_lookup(self, phone_number: str, result: Dict):
#         """Perform WHOIS reverse lookup"""
#         try:
#             # Use WhoisXML API if available
#             if self.whoisxml_key:
#                 url = "https://reverse-whois.whoisxmlapi.com/api/v2"
#                 params = {
#                     'apiKey': self.whoisxml_key,
#                     'searchType': 'current',
#                     'mode': 'purchase',
#                     'advancedSearchTerms': [
#                         {
#                             'field': 'RegistrantPhone',
#                             'term': phone_number
#                         }
#                     ]
#                 }
                
#                 response = self.session.post(url, json=params, timeout=15)
#                 if response.status_code == 200:
#                     data = response.json()
#                     if 'domainsList' in data:
#                         for domain_info in data['domainsList']:
#                             domain = domain_info.get('domainName')
#                             if domain:
#                                 result['linked_domains'].append(domain)
#                                 result['domain_count'] += 1
                                
#                                 # Get additional WHOIS info
#                                 if 'registrarName' in domain_info:
#                                     result['whois_registrar'] = domain_info['registrarName']
#                                 if 'createdDate' in domain_info:
#                                     result['creation_date'] = domain_info['createdDate']
            
#             # Fallback: Manual WHOIS lookup for known domains
#             for domain in result['linked_domains'][:5]:  # Limit to first 5 domains
#                 try:
#                     w = whois.whois(domain)
#                     if w:
#                         if not result['whois_registrar'] and w.registrar:
#                             result['whois_registrar'] = w.registrar
#                         if not result['creation_date'] and w.creation_date:
#                             result['creation_date'] = str(w.creation_date)
#                 except Exception as e:
#                     logger.warning(f"WHOIS lookup failed for {domain}: {e}")
                    
#         except Exception as e:
#             logger.warning(f"WHOIS reverse lookup failed: {e}")

#     async def search_business_directories(self, phone_number: str, result: Dict):
#         """Search business directories for phone number"""
#         try:
#             directories = [
#                 'yellowpages.com',
#                 'whitepages.com',
#                 'yelp.com',
#                 'bbb.org',
#                 'manta.com'
#             ]
            
#             for directory in directories:
#                 search_query = f'"{phone_number}" site:{directory}'
#                 try:
#                     search_results = list(search(search_query, num_results=5, stop=5))
                    
#                     for url in search_results:
#                         # Scrape business information
#                         await self.scrape_business_info(url, result)
                    
#                     await asyncio.sleep(random.uniform(2, 3))
#                 except Exception as e:
#                     logger.warning(f"Business directory search failed for {directory}: {e}")
                    
#         except Exception as e:
#             logger.warning(f"Business directory search failed: {e}")

#     async def scrape_business_info(self, url: str, result: Dict):
#         """Scrape business information from directory pages"""
#         try:
#             headers = self.get_random_headers()
#             response = self.session.get(url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
                
#                 # Look for website links
#                 website_links = soup.find_all('a', href=re.compile(r'https?://(?!.*(?:yellowpages|whitepages|yelp|bbb|manta)).*'))
                
#                 for link in website_links:
#                     href = link.get('href')
#                     if href:
#                         domain = tldextract.extract(href).registered_domain
#                         if domain and domain not in result['linked_domains']:
#                             result['linked_domains'].append(domain)
#                             result['business_domains'].append(domain)
#                             result['domain_count'] += 1
                            
#         except Exception as e:
#             logger.warning(f"Failed to scrape business info from {url}: {e}")

#     async def get_comprehensive_profile_images(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive profile images from various platforms"""
#         result = {
#             "insta_dp": None, 
#             "whatsapp_dp": None, 
#             "telegram_dp": None,
#             "facebook_dp": None,
#             "twitter_dp": None,
#             "profile_images_found": 0
#         }
        
#         # Method 1: Search for profile images on social platforms
#         await self.search_profile_images(phone_number, result)
        
#         # Method 2: Use reverse image search
#         await self.reverse_image_search(phone_number, result)
        
#         # Method 3: Scrape profile pictures with Selenium
#         await self.scrape_profile_pictures_selenium(phone_number, result)

#         return result

#     async def search_profile_images(self, phone_number: str, result: Dict):
#         """Search for profile images across platforms"""
#         try:
#             # Search for images associated with the phone number
#             search_queries = [
#                 f'"{phone_number}" profile picture',
#                 f'"{phone_number}" avatar',
#                 f'"{phone_number}" photo',
#                 f'"{phone_number}" image'
#             ]
            
#             for query in search_queries:
#                 try:
#                     search_results = list(search(query, num_results=10, stop=10))
                    
#                     for url in search_results:
#                         # Check if URL contains image or profile references
#                         if any(platform in url.lower() for platform in ['instagram', 'facebook', 'twitter', 'telegram']):
#                             await self.extract_profile_image_from_url(url, result)
                    
#                     await asyncio.sleep(random.uniform(2, 4))
#                 except Exception as e:
#                     logger.warning(f"Profile image search failed: {e}")
                    
#         except Exception as e:
#             logger.warning(f"Profile image search failed: {e}")

#     async def extract_profile_image_from_url(self, url: str, result: Dict):
#         """Extract profile image from social media URL"""
#         try:
#             headers = self.get_random_headers()
#             response = self.session.get(url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
                
#                 # Look for profile images
#                 img_selectors = [
#                     'img[alt*="profile"]',
#                     'img[class*="profile"]',
#                     'img[class*="avatar"]',
#                     'img[src*="profile"]',
#                     'meta[property="og:image"]'
#                 ]
                
#                 for selector in img_selectors:
#                     img_elem = soup.select_one(selector)
#                     if img_elem:
#                         img_url = img_elem.get('src') or img_elem.get('content')
#                         if img_url:
#                             # Determine platform and save image URL
#                             platform = self.determine_platform_from_url(url)
#                             if platform:
#                                 result[f'{platform}_dp'] = img_url
#                                 result['profile_images_found'] += 1
                                
#                                 # Download and save image
#                                 await self.download_profile_image(img_url, platform, result)
#                             break
                            
#         except Exception as e:
#             logger.warning(f"Failed to extract profile image from {url}: {e}")

#     def determine_platform_from_url(self, url: str) -> str:
#         """Determine social media platform from URL"""
#         url_lower = url.lower()
#         if 'instagram' in url_lower:
#             return 'insta'
#         elif 'facebook' in url_lower:
#             return 'facebook'
#         elif 'twitter' in url_lower or 'x.com' in url_lower:
#             return 'twitter'
#         elif 'telegram' in url_lower or 't.me' in url_lower:
#             return 'telegram'
#         elif 'whatsapp' in url_lower:
#             return 'whatsapp'
#         return None

#     async def download_profile_image(self, img_url: str, platform: str, result: Dict):
#         """Download and save profile image"""
#         try:
#             if not img_url.startswith('http'):
#                 return
                
#             headers = self.get_random_headers()
#             response = self.session.get(img_url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 # Create filename
#                 phone_clean = result.get('phone_number', 'unknown').replace('+', '').replace(' ', '')
#                 filename = f"output/images/{phone_clean}_{platform}.jpg"
                
#                 # Save image
#                 with open(filename, 'wb') as f:
#                     f.write(response.content)
                
#                 # Update result with local file path
#                 result[f'{platform}_dp'] = filename
                
#         except Exception as e:
#             logger.warning(f"Failed to download profile image: {e}")

#     async def reverse_image_search(self, phone_number: str, result: Dict):
#         """Perform reverse image search for profile pictures"""
#         try:
#             # This would require integration with reverse image search APIs
#             # For now, implement basic search
#             pass
#         except Exception as e:
#             logger.warning(f"Reverse image search failed: {e}")

#     async def scrape_profile_pictures_selenium(self, phone_number: str, result: Dict):
#         """Use Selenium to scrape profile pictures from social platforms"""
#         try:
#             options = Options()
#             options.add_argument('--headless')
#             options.add_argument('--no-sandbox')
#             options.add_argument('--disable-dev-shm-usage')
#             options.add_argument('--disable-gpu')
            
#             driver = webdriver.Chrome(options=options)
            
#             try:
#                 # Search for social media profiles
#                 clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
                
#                 # Instagram search (requires login for full access)
#                 try:
#                     driver.get(f'https://www.instagram.com/explore/tags/{clean_number}/')
#                     time.sleep(3)
                    
#                     # Look for profile images
#                     img_elements = driver.find_elements(By.CSS_SELECTOR, 'img[alt*="profile"], img[class*="avatar"]')
#                     if img_elements:
#                         img_url = img_elements[0].get_attribute('src')
#                         if img_url:
#                             result['insta_dp'] = img_url
#                             await self.download_profile_image(img_url, 'insta', result)
#                 except Exception as e:
#                     logger.warning(f"Instagram Selenium scraping failed: {e}")
                
#                 # Add more platform-specific scraping here
                
#             finally:
#                 driver.quit()
                
#         except Exception as e:
#             logger.warning(f"Selenium profile picture scraping failed: {e}")

#     async def get_comprehensive_reassignment(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive number reassignment information"""
#         result = {
#             "is_reassigned": None, 
#             "original_carrier": None,
#             "current_carrier": None,
#             "reassignment_date": None,
#             "port_history": []
#         }
        
#         # Method 1: HLRLookup API
#         if self.hlrlookup_key:
#             await self.hlr_lookup_api(phone_number, result)
        
#         # Method 2: Carrier history lookup
#         await self.lookup_carrier_history(phone_number, result)
        
#         # Method 3: FCC database search
#         await self.search_fcc_database(phone_number, result)

#         return result

#     async def hlr_lookup_api(self, phone_number: str, result: Dict):
#         """Use HLRLookup API for number reassignment check"""
#         try:
#             url = "https://www.hlrlookup.com/api/hlr/"
#             params = {
#                 'api_key': self.hlrlookup_key,
#                 'number': phone_number
#             }
            
#             response = self.session.get(url, params=params, timeout=15)
#             if response.status_code == 200:
#                 data = response.json()
                
#                 if data.get('success'):
#                     result['current_carrier'] = data.get('network_name')
#                     result['is_reassigned'] = data.get('ported', False)
                    
#                     if data.get('original_network_name'):
#                         result['original_carrier'] = data['original_network_name']
                        
#         except Exception as e:
#             logger.warning(f"HLRLookup API failed: {e}")

#     async def lookup_carrier_history(self, phone_number: str, result: Dict):
#         """Lookup carrier history from various sources"""
#         try:
#             # Search for carrier change information
#             search_queries = [
#                 f'"{phone_number}" carrier change',
#                 f'"{phone_number}" ported number',
#                 f'"{phone_number}" switched carrier'
#             ]
            
#             for query in search_queries:
#                 try:
#                     search_results = list(search(query, num_results=5, stop=5))
                    
#                     for url in search_results:
#                         # Scrape for carrier history information
#                         await self.scrape_carrier_history(url, result)
                    
#                     await asyncio.sleep(random.uniform(2, 3))
#                 except Exception as e:
#                     logger.warning(f"Carrier history search failed: {e}")
                    
#         except Exception as e:
#             logger.warning(f"Carrier history lookup failed: {e}")

#     async def scrape_carrier_history(self, url: str, result: Dict):
#         """Scrape carrier history information"""
#         try:
#             headers = self.get_random_headers()
#             response = self.session.get(url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 text = soup.get_text()
                
#                 # Look for carrier names and dates
#                 carrier_patterns = [
#                     r'(Verizon|AT&T|T-Mobile|Sprint|Idea|Airtel|Jio|BSNL)',
#                     r'switched from (\w+) to (\w+)',
#                     r'ported from (\w+)'
#                 ]
                
#                 for pattern in carrier_patterns:
#                     matches = re.findall(pattern, text, re.I)
#                     if matches:
#                         if isinstance(matches[0], tuple):
#                             result['original_carrier'] = matches[0][0]
#                             if len(matches[0]) > 1:
#                                 result['current_carrier'] = matches[0][1]
#                         else:
#                             if not result.get('current_carrier'):
#                                 result['current_carrier'] = matches[0]
                        
#                         result['is_reassigned'] = True
#                         break
                        
#         except Exception as e:
#             logger.warning(f"Failed to scrape carrier history from {url}: {e}")

#     async def search_fcc_database(self, phone_number: str, result: Dict):
#         """Search FCC reassigned number database"""
#         try:
#             # This would require access to FCC databases
#             # For now, implement basic search
#             search_query = f'"{phone_number}" FCC reassigned database'
            
#             search_results = list(search(search_query, num_results=5, stop=5))
            
#             for url in search_results:
#                 if 'fcc.gov' in url:
#                     # Scrape FCC page for reassignment info
#                     await self.scrape_fcc_page(url, result)
                    
#         except Exception as e:
#             logger.warning(f"FCC database search failed: {e}")

#     async def scrape_fcc_page(self, url: str, result: Dict):
#         """Scrape FCC page for reassignment information"""
#         try:
#             headers = self.get_random_headers()
#             response = self.session.get(url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
#                 text = soup.get_text()
                
#                 # Look for reassignment indicators
#                 if any(word in text.lower() for word in ['reassigned', 'ported', 'transferred']):
#                     result['is_reassigned'] = True
                    
#         except Exception as e:
#             logger.warning(f"Failed to scrape FCC page {url}: {e}")

#     async def get_comprehensive_online_mentions(self, phone_number: str) -> Dict[str, Any]:
#         """Get comprehensive online mentions timeline"""
#         result = {
#             "first_seen_date": None, 
#             "mention_count": 0, 
#             "mention_sources": [],
#             "mention_contexts": [],
#             "latest_mention_date": None,
#             "mention_timeline": []
#         }
        
#         # Method 1: Google/Bing searches with date filters
#         await self.search_mentions_with_dates(phone_number, result)
        
#         # Method 2: Wayback Machine CDX API
#         await self.wayback_machine_search(phone_number, result)
        
#         # Method 3: Social media timeline search
#         await self.social_media_timeline_search(phone_number, result)
        
#         # Method 4: News and article search
#         await self.news_article_search(phone_number, result)

#         return result

#     async def search_mentions_with_dates(self, phone_number: str, result: Dict):
#         """Search for mentions with date filters"""
#         try:
#             # Search with different date ranges
#             date_ranges = [
#                 'after:2020',
#                 'after:2018',
#                 'after:2015',
#                 'after:2010'
#             ]
            
#             for date_range in date_ranges:
#                 search_query = f'"{phone_number}" {date_range}'
                
#                 try:
#                     search_results = list(search(search_query, num_results=10, stop=10))
                    
#                     for url in search_results:
#                         # Scrape page for mention context and date
#                         await self.scrape_mention_page(url, result)
#                         result['mention_count'] += 1
                        
#                         if url not in result['mention_sources']:
#                             result['mention_sources'].append(url)
                    
#                     await asyncio.sleep(random.uniform(2, 4))
#                 except Exception as e:
#                     logger.warning(f"Mention search failed for {date_range}: {e}")
                    
#         except Exception as e:
#             logger.warning(f"Mentions with dates search failed: {e}")

#     async def scrape_mention_page(self, url: str, result: Dict):
#         """Scrape individual page for mention context"""
#         try:
#             headers = self.get_random_headers()
#             response = self.session.get(url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
                
#                 # Look for date information
#                 date_patterns = [
#                     r'\d{4}-\d{2}-\d{2}',
#                     r'\d{2}/\d{2}/\d{4}',
#                     r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
#                 ]
                
#                 text = soup.get_text()
                
#                 for pattern in date_patterns:
#                     matches = re.findall(pattern, text)
#                     if matches:
#                         mention_date = matches[0]
                        
#                         # Update first seen date
#                         if not result['first_seen_date'] or mention_date < result['first_seen_date']:
#                             result['first_seen_date'] = mention_date
                        
#                         # Update latest mention date
#                         if not result['latest_mention_date'] or mention_date > result['latest_mention_date']:
#                             result['latest_mention_date'] = mention_date
                        
#                         # Add to timeline
#                         result['mention_timeline'].append({
#                             'date': mention_date,
#                             'source': url,
#                             'context': text[:200] + '...' if len(text) > 200 else text
#                         })
#                         break
                
#                 # Extract context around phone number
#                 phone_clean = result.get('phone_number', '').replace('+', '').replace('-', '').replace(' ', '')
#                 if phone_clean in text:
#                     # Find context around the phone number
#                     phone_index = text.find(phone_clean)
#                     context_start = max(0, phone_index - 100)
#                     context_end = min(len(text), phone_index + 100)
#                     context = text[context_start:context_end].strip()
                    
#                     if context not in result['mention_contexts']:
#                         result['mention_contexts'].append(context)
                        
#         except Exception as e:
#             logger.warning(f"Failed to scrape mention page {url}: {e}")

#     async def wayback_machine_search(self, phone_number: str, result: Dict):
#         """Search Wayback Machine for historical mentions"""
#         try:
#             # Use Wayback Machine CDX API
#             clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
#             # Search for archived pages containing the phone number
#             cdx_url = f"http://web.archive.org/cdx/search/cdx"
#             params = {
#                 'url': f'*{clean_number}*',
#                 'output': 'json',
#                 'limit': 100
#             }
            
#             response = self.session.get(cdx_url, params=params, timeout=20)
#             if response.status_code == 200:
#                 data = response.json()
                
#                 if data and len(data) > 1:  # First row is headers
#                     for row in data[1:]:  # Skip header row
#                         if len(row) >= 2:
#                             timestamp = row[1]  # Wayback timestamp
#                             original_url = row[2]  # Original URL
                            
#                             # Convert timestamp to readable date
#                             if len(timestamp) >= 8:
#                                 date_str = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}"
                                
#                                 # Update first seen date
#                                 if not result['first_seen_date'] or date_str < result['first_seen_date']:
#                                     result['first_seen_date'] = date_str
                                
#                                 # Add to timeline
#                                 result['mention_timeline'].append({
#                                     'date': date_str,
#                                     'source': f"archive.org: {original_url}",
#                                     'context': 'Historical web archive'
#                                 })
                                
#                                 result['mention_count'] += 1
                                
#         except Exception as e:
#             logger.warning(f"Wayback Machine search failed: {e}")

#     async def social_media_timeline_search(self, phone_number: str, result: Dict):
#         """Search social media for timeline mentions"""
#         try:
#             platforms = ['twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com']
            
#             for platform in platforms:
#                 search_query = f'"{phone_number}" site:{platform}'
                
#                 try:
#                     search_results = list(search(search_query, num_results=5, stop=5))
                    
#                     for url in search_results:
#                         await self.scrape_social_mention(url, result)
#                         result['mention_count'] += 1
                        
#                         if url not in result['mention_sources']:
#                             result['mention_sources'].append(url)
                    
#                     await asyncio.sleep(random.uniform(2, 3))
#                 except Exception as e:
#                     logger.warning(f"Social media search failed for {platform}: {e}")
                    
#         except Exception as e:
#             logger.warning(f"Social media timeline search failed: {e}")

#     async def scrape_social_mention(self, url: str, result: Dict):
#         """Scrape social media mention for context"""
#         try:
#             headers = self.get_random_headers()
#             response = self.session.get(url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
                
#                 # Look for post dates
#                 date_selectors = [
#                     'time[datetime]',
#                     '[data-testid="timestamp"]',
#                     '.timestamp',
#                     '.date'
#                 ]
                
#                 for selector in date_selectors:
#                     date_elem = soup.select_one(selector)
#                     if date_elem:
#                         date_value = date_elem.get('datetime') or date_elem.get_text(strip=True)
#                         if date_value:
#                             # Add to timeline
#                             result['mention_timeline'].append({
#                                 'date': date_value,
#                                 'source': url,
#                                 'context': 'Social media mention'
#                             })
#                             break
                            
#         except Exception as e:
#             logger.warning(f"Failed to scrape social mention {url}: {e}")

#     async def news_article_search(self, phone_number: str, result: Dict):
#         """Search news articles for phone number mentions"""
#         try:
#             news_sites = [
#                 'news.google.com',
#                 'cnn.com',
#                 'bbc.com',
#                 'reuters.com',
#                 'ap.org'
#             ]
            
#             for site in news_sites:
#                 search_query = f'"{phone_number}" site:{site}'
                
#                 try:
#                     search_results = list(search(search_query, num_results=3, stop=3))
                    
#                     for url in search_results:
#                         await self.scrape_news_article(url, result)
#                         result['mention_count'] += 1
                        
#                         if url not in result['mention_sources']:
#                             result['mention_sources'].append(url)
                    
#                     await asyncio.sleep(random.uniform(2, 3))
#                 except Exception as e:
#                     logger.warning(f"News search failed for {site}: {e}")
                    
#         except Exception as e:
#             logger.warning(f"News article search failed: {e}")

#     async def scrape_news_article(self, url: str, result: Dict):
#         """Scrape news article for mention context"""
#         try:
#             headers = self.get_random_headers()
#             response = self.session.get(url, headers=headers, timeout=15)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
                
#                 # Look for article date
#                 date_selectors = [
#                     'meta[property="article:published_time"]',
#                     'time[pubdate]',
#                     '.publish-date',
#                     '.article-date'
#                 ]
                
#                 for selector in date_selectors:
#                     date_elem = soup.select_one(selector)
#                     if date_elem:
#                         date_value = date_elem.get('content') or date_elem.get_text(strip=True)
#                         if date_value:
#                             # Add to timeline
#                             result['mention_timeline'].append({
#                                 'date': date_value,
#                                 'source': url,
#                                 'context': 'News article mention'
#                             })
#                             break
                            
#         except Exception as e:
#             logger.warning(f"Failed to scrape news article {url}: {e}")

#     async def export_comprehensive_results(self, clean_number: str, results: Dict):
#         """Export comprehensive results to CSV and PDF"""
#         try:
#             # Export to CSV
#             csv_file = f"output/{clean_number}.csv"
#             with open(csv_file, 'w', newline='', encoding='utf-8') as f:
#                 writer = csv.writer(f)
#                 writer.writerow(['Category', 'Field', 'Value'])
                
#                 def flatten_dict(d, parent_key='', category=''):
#                     items = []
#                     for k, v in d.items():
#                         new_key = f"{parent_key}.{k}" if parent_key else k
#                         current_category = category or k
                        
#                         if isinstance(v, dict):
#                             items.extend(flatten_dict(v, new_key, current_category).items())
#                         elif isinstance(v, list):
#                             if v:  # Only add non-empty lists
#                                 items.append((current_category, new_key, ', '.join(map(str, v))))
#                         else:
#                             if v is not None:  # Only add non-null values
#                                 items.append((current_category, new_key, str(v)))
#                     return dict(items)
                
#                 flat_results = flatten_dict(results)
#                 for (category, field, value) in [(k.split('.')[0], k, v) for k, v in flat_results.items()]:
#                     writer.writerow([category, field, value])

#             # Export to PDF with enhanced formatting
#             pdf_file = f"output/{clean_number}.pdf"
#             doc = SimpleDocTemplate(pdf_file, pagesize=letter)
#             styles = getSampleStyleSheet()
#             story = []
            
#             # Title
#             story.append(Paragraph(f"📱 Comprehensive Phone Intelligence Report", styles['Title']))
#             story.append(Paragraph(f"Phone Number: {results.get('phone_number', clean_number)}", styles['Heading2']))
#             story.append(Spacer(1, 12))
#             story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
#             story.append(Spacer(1, 20))
            
#             # Executive Summary
#             story.append(Paragraph("📊 Executive Summary", styles['Heading1']))
            
#             summary_points = []
#             if results.get('basic_info', {}).get('carrier_name'):
#                 summary_points.append(f"Carrier: {results['basic_info']['carrier_name']}")
#             if results.get('geolocation', {}).get('city'):
#                 summary_points.append(f"Location: {results['geolocation']['city']}, {results['geolocation'].get('state', '')}")
#             if results.get('owner_spam', {}).get('caller_name'):
#                 summary_points.append(f"Owner: {results['owner_spam']['caller_name']}")
#             if results.get('spam_reports', {}).get('report_count', 0) > 0:
#                 summary_points.append(f"Spam Reports: {results['spam_reports']['report_count']}")
            
#             for point in summary_points:
#                 story.append(Paragraph(f"• {point}", styles['Normal']))
#             story.append(Spacer(1, 20))
            
#             # Detailed sections
#             section_icons = {
#                 'basic_info': '📋',
#                 'geolocation': '🌍',
#                 'owner_spam': '👤',
#                 'messaging_presence': '💬',
#                 'social_media_profiles': '📱',
#                 'breach_data': '🔓',
#                 'spam_reports': '⚠️',
#                 'domain_whois': '🌐',
#                 'profile_images': '🖼️',
#                 'number_reassignment': '🔄',
#                 'online_mentions': '🔍'
#             }
            
#             for section, data in results.items():
#                 if section not in ['phone_number', 'scan_date', 'errors'] and data:
#                     icon = section_icons.get(section, '📄')
#                     section_title = section.replace('_', ' ').title()
#                     story.append(Paragraph(f"{icon} {section_title}", styles['Heading2']))
                    
#                     if isinstance(data, dict):
#                         for key, value in data.items():
#                             if value is not None and value != [] and value != '':
#                                 if isinstance(value, list):
#                                     value_str = ', '.join(map(str, value[:5]))  # Limit to first 5 items
#                                     if len(value) > 5:
#                                         value_str += f" ... (+{len(value)-5} more)"
#                                 else:
#                                     value_str = str(value)
                                
#                                 story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value_str}", styles['Normal']))
                    
#                     story.append(Spacer(1, 12))
            
#             # Errors section
#             if results.get('errors'):
#                 story.append(Paragraph("⚠️ Errors Encountered", styles['Heading2']))
#                 for error in results['errors']:
#                     story.append(Paragraph(f"• {error.get('feature', 'Unknown')}: {error.get('error', 'Unknown error')}", styles['Normal']))
#                 story.append(Spacer(1, 12))
            
#             # Footer
#             story.append(Spacer(1, 20))
#             story.append(Paragraph("Generated by Advanced Phone Intelligence Toolkit v2.0", styles['Normal']))
#             story.append(Paragraph("⚠️ This report is for educational and legitimate OSINT purposes only.", styles['Normal']))
            
#             doc.build(story)
            
#         except Exception as e:
#             logger.error(f"Failed to export comprehensive results: {e}")




#new 

import asyncio
import json
import logging
import os
import csv
import time
import re
import requests
from datetime import datetime
from typing import Dict, Any, Callable, Optional, List
from urllib.parse import quote, urljoin
import random
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import whois
import tldextract
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import httpx
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import google.generativeai as genai
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

# Remove this line:
# from googlesearch import search

# Add these imports instead:
import requests
from urllib.parse import quote
import json

logger = logging.getLogger(__name__)

class AdvancedPhoneIntelService:
    def __init__(self):
        self.session = requests.Session()
        self.fix_ssl_session()  # Add this line
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # API Keys from environment with fallbacks
        self.numverify_key = os.getenv('NUMVERIFY_API_KEY') or ""
        self.veriphone_key = os.getenv('VERIPHONE_API_KEY')
        self.abstractapi_key = os.getenv('ABSTRACTAPI_KEY') or ""
        self.whoisxml_key = os.getenv('WHOISXML_API_KEY') or ""
        self.hlrlookup_key = os.getenv('HLRLOOKUP_API_KEY') or ""
        self.serpapi_key = os.getenv('SERPAPI_API_KEY') or ""
        self.google_api_key = os.getenv('GOOGLE_API_KEY') or ""
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        
        # Configure Gemini
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize HuggingFace models with error handling
        try:
            self.ner_pipeline = pipeline("ner", 
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple"
            )
            self.sentiment_pipeline = pipeline("sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
        except Exception as e:
            logger.warning(f"Failed to load HuggingFace models: {e}")
            self.ner_pipeline = None
            self.sentiment_pipeline = None
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]

    async def google_search_fallback(self, query: str, num_results: int = 10) -> List[str]:
        """Multiple fallback methods for Google search"""
        results = []
        
        # Fallback 1: SerpAPI (if available)
        if self.serpapi_key:
            try:
                import serpapi
                search = serpapi.GoogleSearch({
                    "q": query,
                    "api_key": self.serpapi_key,
                    "num": num_results
                })
                search_results = search.get_dict()
                if 'organic_results' in search_results:
                    for result in search_results['organic_results'][:num_results]:
                        if 'link' in result:
                            results.append(result['link'])
                    return results
            except Exception as e:
                logger.warning(f"SerpAPI search failed: {e}")
        
        # Fallback 2: Google Custom Search API (if available)
        if self.google_api_key:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.google_api_key,
                    'cx': '017576662512468239146:omuauf_lfve',  # Default CSE
                    'q': query,
                    'num': min(num_results, 10)
                }
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if 'items' in data:
                        for item in data['items']:
                            results.append(item['link'])
                    return results
            except Exception as e:
                logger.warning(f"Google Custom Search failed: {e}")
        
        # Fallback 3: DuckDuckGo search
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=num_results))
                for result in search_results:
                    results.append(result['href'])
            return results
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
        
        # Fallback 4: Bing search scraping
        try:
            bing_url = f"https://www.bing.com/search?q={quote(query)}"
            headers = self.get_random_headers()
            response = self.session.get(bing_url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if href.startswith('http') and 'bing.com' not in href:
                        results.append(href)
                        if len(results) >= num_results:
                            break
            return results
        except Exception as e:
            logger.warning(f"Bing search scraping failed: {e}")
        
        # Fallback 5: Yahoo search scraping
        try:
            yahoo_url = f"https://search.yahoo.com/search?p={quote(query)}"
            headers = self.get_random_headers()
            response = self.session.get(yahoo_url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if href.startswith('http') and 'yahoo.com' not in href:
                        results.append(href)
                        if len(results) >= num_results:
                            break
            return results
        except Exception as e:
            logger.warning(f"Yahoo search scraping failed: {e}")
        
        return results

    def fix_ssl_session(self):
        """Fix SSL certificate issues"""
        import ssl
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Create session with SSL verification disabled for problematic sites
        self.session.verify = False
        
        # Add SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    def get_random_headers(self):
        """Get random headers for scraping"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def comprehensive_scan(self, phone_number: str, status_callback: Callable) -> Dict[str, Any]:
        """Main comprehensive scan orchestrator"""
        results = {
            "phone_number": phone_number,
            "scan_date": datetime.now().isoformat(),
            "basic_info": {},
            "geolocation": {},
            "owner_spam": {},
            "messaging_presence": {},
            "social_media_profiles": {},
            "breach_data": {},
            "spam_reports": {},
            "domain_whois": {},
            "profile_images": {},
            "number_reassignment": {},
            "online_mentions": {},
            "errors": []
        }

        # Enhanced feature scanning with multiple methods
        features = [
            ("basic_info", self.get_comprehensive_basic_info),
            ("geolocation", self.get_comprehensive_geolocation),
            ("owner_spam", self.get_comprehensive_owner_spam),
            ("messaging", self.get_comprehensive_messaging_presence),
            ("social_media", self.get_comprehensive_social_media),
            ("breach_data", self.get_comprehensive_breach_data),
            ("spam_reports", self.get_comprehensive_spam_reports),
            ("domain_whois", self.get_comprehensive_domain_whois),
            ("profile_images", self.get_comprehensive_profile_images),
            ("reassignment", self.get_comprehensive_reassignment),
            ("online_mentions", self.get_comprehensive_online_mentions)
        ]

        for feature_name, feature_func in features:
            try:
                status_callback(feature_name, "running")
                logger.info(f"Starting comprehensive {feature_name} for {phone_number}")
                
                feature_data = await feature_func(phone_number)
                results[feature_name.replace("_", "_")] = feature_data
                
                # Save raw data
                clean_number = phone_number.replace('+', '').replace(' ', '')
                raw_file = f"output/raw/{clean_number}_{feature_name}.json"
                with open(raw_file, 'w') as f:
                    json.dump(feature_data, f, indent=2, default=str)
                
                status_callback(feature_name, "success")
                logger.info(f"Completed comprehensive {feature_name} for {phone_number}")
                
                # Add delay between features to avoid rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                error_msg = f"Error in {feature_name}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append({
                    "feature": feature_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                status_callback(feature_name, "failed")

        return results

    async def get_comprehensive_basic_info(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive basic phone info with multiple APIs and scrapers"""
        result = {
            "country_code": None, 
            "region": None, 
            "carrier_name": None, 
            "line_type": None,
            "is_valid": False,
            "international_format": None,
            "national_format": None,
            "country_name": None
        }
        
        # Method 1: Numverify API
        if self.numverify_key:
            try:
                url = "http://apilayer.net/api/validate"
                params = {
                    'access_key': self.numverify_key,
                    'number': phone_number,
                    'country_code': '',
                    'format': 1
                }
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('valid'):
                        result.update({
                            "country_code": f"+{data.get('country_code')}",
                            "region": data.get('location'),
                            "carrier_name": data.get('carrier'),
                            "line_type": data.get('line_type'),
                            "is_valid": True,
                            "international_format": data.get('international_format'),
                            "national_format": data.get('national_format'),
                            "country_name": data.get('country_name')
                        })
                        return result
            except Exception as e:
                logger.warning(f"Numverify API failed: {e}")

        # Method 2: Veriphone API
        if self.veriphone_key:
            try:
                url = "https://api.veriphone.io/v2/verify"
                params = {
                    'key': self.veriphone_key,
                    'phone': phone_number
                }
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        phone_data = data.get('phone', {})
                        result.update({
                            "country_code": f"+{phone_data.get('country_code')}",
                            "region": phone_data.get('location'),
                            "carrier_name": phone_data.get('carrier'),
                            "line_type": phone_data.get('phone_type'),
                            "is_valid": phone_data.get('phone_valid', False),
                            "international_format": phone_data.get('international_format'),
                            "country_name": phone_data.get('country')
                        })
                        return result
            except Exception as e:
                logger.warning(f"Veriphone API failed: {e}")

        # Method 3: AbstractAPI
        if self.abstractapi_key:
            try:
                url = "https://phonevalidation.abstractapi.com/v1/"
                params = {
                    'api_key': self.abstractapi_key,
                    'phone': phone_number
                }
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('valid'):
                        result.update({
                            "country_code": data.get('country', {}).get('code'),
                            "region": data.get('location'),
                            "carrier_name": data.get('carrier'),
                            "line_type": data.get('type'),
                            "is_valid": True,
                            "international_format": data.get('format', {}).get('international'),
                            "national_format": data.get('format', {}).get('national'),
                            "country_name": data.get('country', {}).get('name')
                        })
                        return result
            except Exception as e:
                logger.warning(f"AbstractAPI failed: {e}")

        # Fallback 1: phonenumbers library
        try:
            parsed = phonenumbers.parse(phone_number, None)
            if phonenumbers.is_valid_number(parsed):
                result.update({
                    "country_code": f"+{parsed.country_code}",
                    "region": geocoder.description_for_number(parsed, "en"),
                    "carrier_name": carrier.name_for_number(parsed, "en"),
                    "line_type": "mobile" if phonenumbers.number_type(parsed) in [0, 1] else "landline",
                    "is_valid": True,
                    "international_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                    "national_format": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
                })
                
                # Get country name
                country_code = phonenumbers.region_code_for_number(parsed)
                if country_code:
                    result["country_name"] = country_code
                
                return result
        except Exception as e:
            logger.warning(f"phonenumbers library failed: {e}")

        # Fallback 2: Scrape carrier lookup sites
        await self.scrape_multiple_carrier_sites(phone_number, result)

        # Fallback 3: Use Gemini AI for analysis
        if self.gemini_key and not result.get("carrier_name"):
            try:
                prompt = f"Analyze this phone number: {phone_number}. Provide carrier, country, region, and line type information."
                response = self.gemini_model.generate_content(prompt)
                # Parse AI response and extract relevant info
                ai_text = response.text
                if "carrier" in ai_text.lower():
                    # Extract carrier info using regex or NLP
                    pass
            except Exception as e:
                logger.warning(f"Gemini AI analysis failed: {e}")

        return result

    async def scrape_multiple_carrier_sites(self, phone_number: str, result: Dict):
        """Scrape multiple carrier lookup sites"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        sites = [
            {
                'url': f'https://www.freecarrierlookup.com/lookup.php?number={clean_number}',
                'parser': self.parse_freecarrierlookup
            },
            {
                'url': f'https://www.carrierlookup.com/index.php/lookup/carrier?msisdn={clean_number}',
                'parser': self.parse_carrierlookup
            },
            {
                'url': f'https://www.truecaller.com/search/in/{clean_number}',
                'parser': self.parse_truecaller_basic
            }
        ]
        
        for site in sites:
            try:
                headers = self.get_random_headers()
                response = self.session.get(site['url'], headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    site['parser'](soup, result)
                    if result.get('carrier_name'):
                        break
                await asyncio.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.warning(f"Failed to scrape {site['url']}: {e}")

    def parse_freecarrierlookup(self, soup: BeautifulSoup, result: Dict):
        """Parse freecarrierlookup.com results"""
        try:
            carrier_elem = soup.find('td', string=re.compile('Carrier', re.I))
            if carrier_elem:
                carrier_value = carrier_elem.find_next_sibling('td')
                if carrier_value:
                    result['carrier_name'] = carrier_value.get_text(strip=True)
            
            location_elem = soup.find('td', string=re.compile('Location', re.I))
            if location_elem:
                location_value = location_elem.find_next_sibling('td')
                if location_value:
                    result['region'] = location_value.get_text(strip=True)
        except Exception as e:
            logger.warning(f"Error parsing freecarrierlookup: {e}")

    def parse_carrierlookup(self, soup: BeautifulSoup, result: Dict):
        """Parse carrierlookup.com results"""
        try:
            # Look for carrier information in various formats
            carrier_patterns = [
                r'Carrier[:\s]+([^<\n]+)',
                r'Network[:\s]+([^<\n]+)',
                r'Operator[:\s]+([^<\n]+)'
            ]
            
            text = soup.get_text()
            for pattern in carrier_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    result['carrier_name'] = match.group(1).strip()
                    break
        except Exception as e:
            logger.warning(f"Error parsing carrierlookup: {e}")

    def parse_truecaller_basic(self, soup: BeautifulSoup, result: Dict):
        """Parse basic Truecaller info"""
        try:
            # Look for carrier/operator info
            operator_elem = soup.find(string=re.compile('operator', re.I))
            if operator_elem:
                parent = operator_elem.parent
                if parent:
                    result['carrier_name'] = parent.get_text(strip=True)
        except Exception as e:
            logger.warning(f"Error parsing Truecaller basic: {e}")

    async def get_comprehensive_geolocation(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive geolocation data with multiple sources"""
        result = {
            "city": None, 
            "state": None, 
            "timezone": None, 
            "latitude": None, 
            "longitude": None,
            "country": None,
            "region": None,
            "postal_code": None
        }
        
        # Method 1: phonenumbers library
        try:
            parsed = phonenumbers.parse(phone_number, None)
            if phonenumbers.is_valid_number(parsed):
                # Get timezone
                timezones = timezone.time_zones_for_number(parsed)
                if timezones:
                    result["timezone"] = list(timezones)[0]
                
                # Get location description
                location = geocoder.description_for_number(parsed, "en")
                if location:
                    result["region"] = location
                    # Try to parse city/state from location
                    if ", " in location:
                        parts = location.split(", ")
                        if len(parts) >= 2:
                            result["city"] = parts[0]
                            result["state"] = parts[1]
                    
                # Get country
                country_code = phonenumbers.region_code_for_number(parsed)
                if country_code:
                    result["country"] = country_code
        except Exception as e:
            logger.warning(f"phonenumbers geolocation failed: {e}")

        # Method 2: Scrape location databases
        await self.scrape_location_databases(phone_number, result)
        
        # Method 3: Use area code databases
        await self.lookup_area_code_database(phone_number, result)
        
        # Method 4: Gemini AI for location analysis
        if self.gemini_key and not result.get("city"):
            try:
                prompt = f"What city and state/region is phone number {phone_number} from? Provide specific location details."
                response = self.gemini_model.generate_content(prompt)
                ai_text = response.text
                # Parse AI response for location info
                await self.parse_ai_location_response(ai_text, result)
            except Exception as e:
                logger.warning(f"Gemini location analysis failed: {e}")

        return result

    async def scrape_location_databases(self, phone_number: str, result: Dict):
        """Scrape multiple location databases"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Extract area code for US numbers
        if clean_number.startswith('1') and len(clean_number) == 11:
            area_code = clean_number[1:4]
            
            # Scrape area code databases
            sites = [
                f'https://www.allareacodes.com/{area_code}',
                f'https://www.areacodehelp.com/where/area_code_{area_code}.shtml',
                f'https://www.whitepages.com/phone/1-{area_code}'
            ]
            
            for site in sites:
                try:
                    headers = self.get_random_headers()
                    response = self.session.get(site, headers=headers, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        self.parse_area_code_info(soup, result)
                        if result.get('city'):
                            break
                    await asyncio.sleep(random.uniform(1, 2))
                except Exception as e:
                    logger.warning(f"Failed to scrape {site}: {e}")

    def parse_area_code_info(self, soup: BeautifulSoup, result: Dict):
        """Parse area code information from scraped pages"""
        try:
            # Look for city/state patterns
            text = soup.get_text()
            
            # Common patterns for location info
            patterns = [
                r'(?:City|Cities)[:\s]+([^,\n]+),?\s*([^,\n]+)',
                r'(?:Location|Area)[:\s]+([^,\n]+),?\s*([^,\n]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    city, state = matches[0]
                    result['city'] = city.strip()
                    result['state'] = state.strip()
                    break
        except Exception as e:
            logger.warning(f"Error parsing area code info: {e}")

    async def lookup_area_code_database(self, phone_number: str, result: Dict):
        """Lookup area code in local database or API"""
        # This would use a local area code database
        # For now, implement basic US area code mapping
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        if clean_number.startswith('1') and len(clean_number) == 11:
            area_code = clean_number[1:4]
            
            # Basic area code to location mapping (sample)
            area_code_map = {
                '212': {'city': 'New York', 'state': 'NY'},
                '213': {'city': 'Los Angeles', 'state': 'CA'},
                '312': {'city': 'Chicago', 'state': 'IL'},
                '415': {'city': 'San Francisco', 'state': 'CA'},
                '713': {'city': 'Houston', 'state': 'TX'},
                '305': {'city': 'Miami', 'state': 'FL'},
                '404': {'city': 'Atlanta', 'state': 'GA'},
                '617': {'city': 'Boston', 'state': 'MA'},
                '206': {'city': 'Seattle', 'state': 'WA'},
                '702': {'city': 'Las Vegas', 'state': 'NV'},
                # Add more mappings as needed
            }
            
            if area_code in area_code_map:
                location_info = area_code_map[area_code]
                if not result.get('city'):
                    result['city'] = location_info['city']
                if not result.get('state'):
                    result['state'] = location_info['state']

    async def parse_ai_location_response(self, ai_text: str, result: Dict):
        """Parse AI response for location information"""
        try:
            # Use NER to extract location entities
            if self.ner_pipeline:
                entities = self.ner_pipeline(ai_text)
                for entity in entities:
                    if entity['entity_group'] == 'LOC':
                        location = entity['word']
                        if not result.get('city') and len(location.split()) <= 2:
                            result['city'] = location
                        elif not result.get('state') and len(location) == 2:
                            result['state'] = location
        except Exception as e:
            logger.warning(f"Error parsing AI location response: {e}")

    async def get_comprehensive_owner_spam(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive owner name and spam information"""
        result = {
            "caller_name": None, 
            "spam_score": 0.0, 
            "spam_tags": [],
            "caller_type": None,
            "business_name": None,
            "reputation_score": None,
            "report_count": 0
        }
        
        # Method 1: Scrape Truecaller with multiple approaches
        await self.scrape_truecaller_comprehensive(phone_number, result)
        
        # Method 2: Scrape other caller ID sites
        await self.scrape_multiple_caller_id_sites(phone_number, result)
        
        # Method 3: Use Selenium for dynamic content
        await self.scrape_with_selenium(phone_number, result)
        
        # Method 4: Use NER on scraped text
        if result.get('caller_name') and self.ner_pipeline:
            try:
                entities = self.ner_pipeline(result['caller_name'])
                for entity in entities:
                    if entity['entity_group'] == 'PER':
                        result['caller_name'] = entity['word']
                        break
            except Exception as e:
                logger.warning(f"NER processing failed: {e}")

        return result

    async def scrape_truecaller_comprehensive(self, phone_number: str, result: Dict):
        """Comprehensive Truecaller scraping with multiple methods"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        urls = [
            f'https://www.truecaller.com/search/in/{clean_number}',
            f'https://www.truecaller.com/search/us/{clean_number}',
            f'https://www.truecaller.com/search/global/{clean_number}'
        ]
        
        for url in urls:
            try:
                headers = self.get_random_headers()
                headers['Referer'] = 'https://www.truecaller.com/'
                
                response = self.session.get(url, headers=headers, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for caller name
                    name_selectors = [
                        'h1[data-test-id="search-result-name"]',
                        '.search-result-name',
                        '.caller-name',
                        'h1.name'
                    ]
                    
                    for selector in name_selectors:
                        name_elem = soup.select_one(selector)
                        if name_elem:
                            result['caller_name'] = name_elem.get_text(strip=True)
                            break
                    
                    # Look for spam indicators
                    spam_indicators = soup.find_all(string=re.compile(r'spam|scam|fraud|telemarketer', re.I))
                    if spam_indicators:
                        result['spam_score'] = min(len(spam_indicators) * 0.2, 1.0)
                        result['spam_tags'] = list(set([indicator.strip().lower() for indicator in spam_indicators[:5]]))
                    
                    if result.get('caller_name'):
                        break
                        
                await asyncio.sleep(random.uniform(2, 4))
            except Exception as e:
                logger.warning(f"Truecaller scraping failed for {url}: {e}")

    async def scrape_multiple_caller_id_sites(self, phone_number: str, result: Dict):
        """Scrape multiple caller ID and spam reporting sites"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        sites = [
            {
                'url': f'https://www.whocalld.com/+{clean_number}',
                'parser': self.parse_whocalld
            },
            {
                'url': f'https://www.shouldianswer.com/phone-number/{clean_number}',
                'parser': self.parse_shouldianswer
            },
            {
                'url': f'https://www.callercenter.com/number/{clean_number}',
                'parser': self.parse_callercenter
            },
            {
                'url': f'https://www.spamcalls.net/en/number/{clean_number}',
                'parser': self.parse_spamcalls
            }
        ]
        
        for site in sites:
            try:
                headers = self.get_random_headers()
                response = self.session.get(site['url'], headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    site['parser'](soup, result)
                    
                await asyncio.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.warning(f"Failed to scrape {site['url']}: {e}")

    def parse_whocalld(self, soup: BeautifulSoup, result: Dict):
        """Parse whocalld.com results"""
        try:
            # Look for caller name
            name_elem = soup.find('h1', class_='caller-name')
            if not name_elem:
                name_elem = soup.find('div', class_='caller-info')
            
            if name_elem:
                name = name_elem.get_text(strip=True)
                if name and not result.get('caller_name'):
                    result['caller_name'] = name
            
            # Look for spam indicators
            spam_elem = soup.find('div', class_='spam-score')
            if spam_elem:
                spam_text = spam_elem.get_text(strip=True)
                if 'spam' in spam_text.lower():
                    result['spam_score'] = 0.8
                    result['spam_tags'].append('reported_spam')
        except Exception as e:
            logger.warning(f"Error parsing whocalld: {e}")

    def parse_shouldianswer(self, soup: BeautifulSoup, result: Dict):
        """Parse shouldianswer.com results"""
        try:
            # Look for caller information
            caller_elem = soup.find('div', class_='caller-details')
            if caller_elem:
                name = caller_elem.get_text(strip=True)
                if name and not result.get('caller_name'):
                    result['caller_name'] = name
            
            # Check for negative ratings
            rating_elem = soup.find('div', class_='rating')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                if any(word in rating_text.lower() for word in ['negative', 'spam', 'scam']):
                    result['spam_score'] = 0.7
                    result['spam_tags'].append('negative_rating')
        except Exception as e:
            logger.warning(f"Error parsing shouldianswer: {e}")

    def parse_callercenter(self, soup: BeautifulSoup, result: Dict):
        """Parse callercenter.com results"""
        try:
            # Look for caller name in various elements
            name_selectors = ['h1.caller-name', '.caller-info h2', '.number-info .name']
            for selector in name_selectors:
                name_elem = soup.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    if name and not result.get('caller_name'):
                        result['caller_name'] = name
                        break
        except Exception as e:
            logger.warning(f"Error parsing callercenter: {e}")

    def parse_spamcalls(self, soup: BeautifulSoup, result: Dict):
        """Parse spamcalls.net results"""
        try:
            # Look for spam classification
            spam_elem = soup.find('div', class_='spam-classification')
            if spam_elem:
                classification = spam_elem.get_text(strip=True).lower()
                if 'spam' in classification:
                    result['spam_score'] = 0.9
                    result['spam_tags'].append('classified_spam')
                elif 'scam' in classification:
                    result['spam_score'] = 0.95
                    result['spam_tags'].append('classified_scam')
        except Exception as e:
            logger.warning(f"Error parsing spamcalls: {e}")

    async def scrape_with_selenium(self, phone_number: str, result: Dict):
        """Use Selenium for dynamic content scraping"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
            
            driver = webdriver.Chrome(options=options)
            
            try:
                clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
                url = f'https://www.truecaller.com/search/in/{clean_number}'
                
                driver.get(url)
                wait = WebDriverWait(driver, 10)
                
                # Wait for content to load
                try:
                    name_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'h1, .caller-name, .search-result-name'))
                    )
                    if name_element:
                        name = name_element.text.strip()
                        if name and not result.get('caller_name'):
                            result['caller_name'] = name
                except TimeoutException:
                    pass
                
                # Look for spam indicators
                try:
                    spam_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'spam') or contains(text(), 'scam')]")
                    if spam_elements:
                        result['spam_score'] = 0.8
                        result['spam_tags'].append('selenium_detected_spam')
                except:
                    pass
                    
            finally:
                driver.quit()
                
        except Exception as e:
            logger.warning(f"Selenium scraping failed: {e}")

    async def get_comprehensive_messaging_presence(self, phone_number: str) -> Dict[str, Any]:
        """Check comprehensive messaging app presence"""
        result = {
            "whatsapp_active": None, 
            "telegram_active": None,
            "signal_active": None,
            "viber_active": None,
            "messenger_active": None
        }
        
        # Method 1: WhatsApp Web scraping
        await self.check_whatsapp_presence(phone_number, result)
        
        # Method 2: Telegram username search
        await self.check_telegram_presence(phone_number, result)
        
        # Method 3: Other messaging apps
        await self.check_other_messaging_apps(phone_number, result)

        return result

    async def check_whatsapp_presence(self, phone_number: str, result: Dict):
        """Check WhatsApp presence using web scraping"""
        try:
            # This is a simplified check - in practice, WhatsApp has strong anti-bot measures
            # You would need to use WhatsApp Business API or similar
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Try to access WhatsApp web with the number
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            
            try:
                # This is a placeholder - actual WhatsApp checking requires more complex logic
                url = f'https://wa.me/{clean_number}'
                driver.get(url)
                
                # Check if the page loads successfully (indicates valid WhatsApp number)
                if "WhatsApp" in driver.title:
                    result['whatsapp_active'] = True
                else:
                    result['whatsapp_active'] = False
                    
            finally:
                driver.quit()
                
        except Exception as e:
            logger.warning(f"WhatsApp presence check failed: {e}")
            result['whatsapp_active'] = None

    async def check_telegram_presence(self, phone_number: str, result: Dict):
        """Check Telegram presence"""
        try:
            # Search for Telegram usernames associated with the phone number
            # This would require Telegram API access
            # For now, implement basic search
            
            search_queries = [
                f'"{phone_number}" site:t.me',
                f'"{phone_number}" telegram',
                f'"{phone_number}" @'
            ]
            
            for query in search_queries:
                try:
                    # Use Google search to find Telegram links
                    # search_results = list(search(query, num_results=5, stop=5))
                    search_results = await self.google_search_fallback(query, num_results=5)
                    for url in search_results:
                        if 't.me' in url or 'telegram' in url.lower():
                            result['telegram_active'] = True
                            return
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.warning(f"Telegram search failed: {e}")
            
            result['telegram_active'] = False
            
        except Exception as e:
            logger.warning(f"Telegram presence check failed: {e}")
            result['telegram_active'] = None

    async def check_other_messaging_apps(self, phone_number: str, result: Dict):
        """Check other messaging apps presence"""
        try:
            # Search for presence on other platforms
            apps = ['signal', 'viber', 'messenger']
            
            for app in apps:
                search_query = f'"{phone_number}" {app}'
                try:
                    # search_results = list(search(search_query, num_results=3, stop=3))
                    search_results = await self.google_search_fallback(search_query, num_results=3)
                    if search_results:
                        result[f'{app}_active'] = True
                    else:
                        result[f'{app}_active'] = False
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.warning(f"{app} search failed: {e}")
                    result[f'{app}_active'] = None
                    
        except Exception as e:
            logger.warning(f"Other messaging apps check failed: {e}")

    async def get_comprehensive_social_media(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive social media profiles"""
        result = {
            "instagram_url": None, 
            "twitter_url": None, 
            "facebook_url": None,
            "linkedin_url": None,
            "tiktok_url": None,
            "snapchat_url": None,
            "youtube_url": None
        }
        
        # Method 1: Google dork searches
        await self.google_dork_social_search(phone_number, result)
        
        # Method 2: Direct platform searches
        await self.direct_platform_searches(phone_number, result)
        
        # Method 3: Use SerpAPI if available
        if self.serpapi_key:
            await self.serpapi_social_search(phone_number, result)

        return result

    async def google_dork_social_search(self, phone_number: str, result: Dict):
        """Perform Google dork searches for social media"""
        platforms = {
            'instagram': 'instagram.com',
            'twitter': 'twitter.com OR x.com',
            'facebook': 'facebook.com',
            'linkedin': 'linkedin.com',
            'tiktok': 'tiktok.com',
            'snapchat': 'snapchat.com',
            'youtube': 'youtube.com'
        }
        
        for platform, site in platforms.items():
            search_queries = [
                f'"{phone_number}" site:{site}',
                f'"{phone_number}" {platform}',
                f'{phone_number} inurl:{site}'
            ]
            
            for query in search_queries:
                try:
                    # search_results = list(search(query, num_results=5, stop=5))
                    search_results = await self.google_search_fallback(query, num_results=5)
                    for url in search_results:
                        if site.split()[0] in url:  # Handle OR conditions
                            result[f'{platform}_url'] = url
                            break
                    
                    if result.get(f'{platform}_url'):
                        break
                        
                    await asyncio.sleep(random.uniform(2, 4))
                except Exception as e:
                    logger.warning(f"Google search failed for {platform}: {e}")

    async def direct_platform_searches(self, phone_number: str, result: Dict):
        """Direct searches on social media platforms"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Instagram search
        try:
            headers = self.get_random_headers()
            # Instagram doesn't allow direct phone number searches, but we can try user search
            # This is a placeholder for more complex Instagram API integration
            pass
        except Exception as e:
            logger.warning(f"Instagram direct search failed: {e}")
        
        # Twitter/X search
        try:
            # Twitter API would be needed for proper search
            # This is a placeholder
            pass
        except Exception as e:
            logger.warning(f"Twitter direct search failed: {e}")

    async def serpapi_social_search(self, phone_number: str, result: Dict):
        """Use SerpAPI for social media searches"""
        if not self.serpapi_key:
            return
            
        try:
            import serpapi
            
            platforms = ['instagram', 'twitter', 'facebook', 'linkedin']
            
            for platform in platforms:
                params = {
                    "engine": "google",
                    "q": f'"{phone_number}" site:{platform}.com',
                    "api_key": self.serpapi_key,
                    "num": 5
                }
                
                search = serpapi.GoogleSearch(params)
                results = search.get_dict()
                
                if 'organic_results' in results:
                    for organic_result in results['organic_results']:
                        link = organic_result.get('link', '')
                        if platform in link:
                            result[f'{platform}_url'] = link
                            break
                
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.warning(f"SerpAPI social search failed: {e}")

    async def get_comprehensive_breach_data(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive breach data"""
        result = {
            "breached_emails": [], 
            "breach_dates": [],
            "breach_sources": [],
            "data_types_exposed": [],
            "severity_score": 0.0
        }
        
        # Method 1: Search public breach databases
        await self.search_public_breach_databases(phone_number, result)
        
        # Method 2: Check HaveIBeenPwned style databases
        await self.check_hibp_style_databases(phone_number, result)
        
        # Method 3: Search paste sites
        await self.search_paste_sites(phone_number, result)

        return result

    async def search_public_breach_databases(self, phone_number: str, result: Dict):
        """Search public breach databases"""
        try:
            # Search for phone number in breach data
            search_queries = [
                f'"{phone_number}" breach database',
                f'"{phone_number}" data leak',
                f'"{phone_number}" exposed data',
                f'"{phone_number}" site:pastebin.com',
                f'"{phone_number}" site:ghostbin.com'
            ]
            
            for query in search_queries:
                try:
                    # search_results = list(search(query, num_results=10, stop=10))
                    search_results = await self.google_search_fallback(query, num_results=10)
                    for url in search_results:
                        if any(site in url for site in ['pastebin', 'ghostbin', 'leak', 'breach']):
                            # Scrape the page for breach information
                            await self.scrape_breach_page(url, result)
                    
                    await asyncio.sleep(random.uniform(2, 4))
                except Exception as e:
                    logger.warning(f"Breach database search failed: {e}")
                    
        except Exception as e:
            logger.warning(f"Public breach database search failed: {e}")

    async def scrape_breach_page(self, url: str, result: Dict):
        """Scrape individual breach pages"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Look for email patterns
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, text)
                
                if emails:
                    result['breached_emails'].extend(emails[:5])  # Limit to 5 emails
                    result['breach_sources'].append(url)
                    result['breach_dates'].append(datetime.now().strftime('%Y-%m-%d'))
                    
        except Exception as e:
            logger.warning(f"Failed to scrape breach page {url}: {e}")

    async def check_hibp_style_databases(self, phone_number: str, result: Dict):
        """Check HaveIBeenPwned style databases"""
        try:
            # This would integrate with breach checking APIs
            # For now, implement basic search
            pass
        except Exception as e:
            logger.warning(f"HIBP style database check failed: {e}")

    async def search_paste_sites(self, phone_number: str, result: Dict):
        """Search paste sites for phone number"""
        paste_sites = [
            'pastebin.com',
            'ghostbin.com',
            'justpaste.it',
            'paste.ee'
        ]
        
        for site in paste_sites:
            try:
                search_query = f'"{phone_number}" site:{site}'
                # search_results = list(search(search_query, num_results=5, stop=5))
                search_results = await self.google_search_fallback(search_query, num_results=5)
                
                for url in search_results:
                    await self.scrape_breach_page(url, result)
                
                await asyncio.sleep(random.uniform(2, 3))
            except Exception as e:
                logger.warning(f"Paste site search failed for {site}: {e}")

    async def get_comprehensive_spam_reports(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive spam/fraud reports"""
        result = {
            "report_sources": [], 
            "report_texts": [], 
            "sentiment_score": None,
            "spam_categories": [],
            "report_count": 0,
            "latest_report_date": None
        }
        
        # Method 1: Scrape 800notes.com
        await self.scrape_800notes_comprehensive(phone_number, result)
        
        # Method 2: Scrape who-called.me
        await self.scrape_who_called_comprehensive(phone_number, result)
        
        # Method 3: Scrape additional spam reporting sites
        await self.scrape_additional_spam_sites(phone_number, result)
        
        # Method 4: Analyze sentiment of collected reports
        if result['report_texts'] and self.sentiment_pipeline:
            await self.analyze_report_sentiment(result)

        return result

    async def scrape_800notes_comprehensive(self, phone_number: str, result: Dict):
        """Comprehensive 800notes.com scraping"""
        try:
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Try different URL formats
            urls = [
                f"https://800notes.com/Phone.aspx/{clean_number}",
                f"https://www.800notes.com/Phone.aspx/{clean_number}",
                f"https://800notes.com/Phone.aspx/{clean_number[1:]}" if clean_number.startswith('1') else None
            ]
            
            for url in urls:
                if not url:
                    continue
                    
                try:
                    headers = self.get_random_headers()
                    response = self.session.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for reports
                        report_elements = soup.find_all(['div', 'p'], class_=re.compile(r'report|comment|review', re.I))
                        
                        for elem in report_elements:
                            text = elem.get_text(strip=True)
                            if text and len(text) > 20:  # Filter out short texts
                                result['report_texts'].append(text)
                                result['report_sources'].append('800notes.com')
                                result['report_count'] += 1
                        
                        # Look for spam categories
                        category_elements = soup.find_all(string=re.compile(r'spam|scam|telemarketer|robocall|fraud', re.I))
                        for category in category_elements:
                            category_clean = category.strip().lower()
                            if category_clean not in result['spam_categories']:
                                result['spam_categories'].append(category_clean)
                        
                        if result['report_texts']:
                            break
                            
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    
        except Exception as e:
            logger.warning(f"800notes comprehensive scraping failed: {e}")

    async def scrape_who_called_comprehensive(self, phone_number: str, result: Dict):
        """Comprehensive who-called.me scraping"""
        try:
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            url = f"https://who-called.me/{clean_number}"
            
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for user reports
                report_elements = soup.find_all(['div', 'article'], class_=re.compile(r'report|comment|user', re.I))
                
                for elem in report_elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 30:
                        result['report_texts'].append(text)
                        result['report_sources'].append('who-called.me')
                        result['report_count'] += 1
                
                # Look for dates
                date_elements = soup.find_all(string=re.compile(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}'))
                if date_elements:
                    result['latest_report_date'] = date_elements[0].strip()
                    
        except Exception as e:
            logger.warning(f"who-called.me comprehensive scraping failed: {e}")

    async def scrape_additional_spam_sites(self, phone_number: str, result: Dict):
        """Scrape additional spam reporting sites"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        sites = [
            {
                'url': f'https://www.shouldianswer.com/phone-number/{clean_number}',
                'name': 'shouldianswer.com'
            },
            {
                'url': f'https://www.spamcalls.net/en/number/{clean_number}',
                'name': 'spamcalls.net'
            },
            {
                'url': f'https://www.callercenter.com/number/{clean_number}',
                'name': 'callercenter.com'
            },
            {
                'url': f'https://www.unknownphone.com/phone-number/{clean_number}',
                'name': 'unknownphone.com'
            }
        ]
        
        for site in sites:
            try:
                headers = self.get_random_headers()
                response = self.session.get(site['url'], headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Generic report extraction
                    text_elements = soup.find_all(['p', 'div', 'span'], string=re.compile(r'.{20,}'))
                    
                    for elem in text_elements:
                        text = elem.get_text(strip=True)
                        if any(keyword in text.lower() for keyword in ['spam', 'scam', 'telemarketer', 'robocall']):
                            result['report_texts'].append(text)
                            result['report_sources'].append(site['name'])
                            result['report_count'] += 1
                
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.warning(f"Failed to scrape {site['name']}: {e}")

    async def analyze_report_sentiment(self, result: Dict):
        """Analyze sentiment of collected reports"""
        try:
            if not result['report_texts']:
                return
                
            # Combine all report texts
            combined_text = ' '.join(result['report_texts'][:10])  # Limit to first 10 reports
            
            # Analyze sentiment
            sentiment_result = self.sentiment_pipeline(combined_text[:512])  # Limit text length
            
            if sentiment_result:
                sentiment = sentiment_result[0]
                result['sentiment_score'] = sentiment['score'] if sentiment['label'] == 'NEGATIVE' else 1 - sentiment['score']
                
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")

    async def get_comprehensive_domain_whois(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive domain/WHOIS information"""
        result = {
            "linked_domains": [], 
            "whois_registrar": None, 
            "creation_date": None,
            "domain_count": 0,
            "business_domains": [],
            "suspicious_domains": []
        }
        
        # Method 1: Search for domains with phone number
        await self.search_domains_with_phone(phone_number, result)
        
        # Method 2: WHOIS reverse lookup
        await self.whois_reverse_lookup(phone_number, result)
        
        # Method 3: Business directory search
        await self.search_business_directories(phone_number, result)

        return result

    async def search_domains_with_phone(self, phone_number: str, result: Dict):
        """Search for domains containing the phone number"""
        try:
            search_queries = [
                f'"{phone_number}" site:*.com',
                f'"{phone_number}" site:*.org',
                f'"{phone_number}" site:*.net',
                f'"{phone_number}" contact phone',
                f'"{phone_number}" whois'
            ]
            
            for query in search_queries:
                try:
                    # search_results = list(search(query, num_results=10, stop=10))
                    search_results = await self.google_search_fallback(query, num_results=10)
                    
                    for url in search_results:
                        domain = tldextract.extract(url).registered_domain
                        if domain and domain not in result['linked_domains']:
                            result['linked_domains'].append(domain)
                            result['domain_count'] += 1
                            
                            # Check if domain seems business-related
                            if any(word in domain.lower() for word in ['business', 'company', 'corp', 'inc', 'llc']):
                                result['business_domains'].append(domain)
                            
                            # Check for suspicious patterns
                            if any(word in domain.lower() for word in ['temp', 'fake', 'scam', 'spam']):
                                result['suspicious_domains'].append(domain)
                    
                    await asyncio.sleep(random.uniform(2, 4))
                except Exception as e:
                    logger.warning(f"Domain search failed for query: {e}")
                    
        except Exception as e:
            logger.warning(f"Domain search with phone failed: {e}")

    async def whois_reverse_lookup(self, phone_number: str, result: Dict):
        """Perform WHOIS reverse lookup"""
        try:
            # Use WhoisXML API if available
            if self.whoisxml_key:
                url = "https://reverse-whois.whoisxmlapi.com/api/v2"
                params = {
                    'apiKey': self.whoisxml_key,
                    'searchType': 'current',
                    'mode': 'purchase',
                    'advancedSearchTerms': [
                        {
                            'field': 'RegistrantPhone',
                            'term': phone_number
                        }
                    ]
                }
                
                response = self.session.post(url, json=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if 'domainsList' in data:
                        for domain_info in data['domainsList']:
                            domain = domain_info.get('domainName')
                            if domain:
                                result['linked_domains'].append(domain)
                                result['domain_count'] += 1
                                
                                # Get additional WHOIS info
                                if 'registrarName' in domain_info:
                                    result['whois_registrar'] = domain_info['registrarName']
                                if 'createdDate' in domain_info:
                                    result['creation_date'] = domain_info['createdDate']
            
            # Fallback: Manual WHOIS lookup for known domains
            for domain in result['linked_domains'][:5]:  # Limit to first 5 domains
                try:
                    w = whois.whois(domain)
                    if w:
                        if not result['whois_registrar'] and w.registrar:
                            result['whois_registrar'] = w.registrar
                        if not result['creation_date'] and w.creation_date:
                            result['creation_date'] = str(w.creation_date)
                except Exception as e:
                    logger.warning(f"WHOIS lookup failed for {domain}: {e}")
                    
        except Exception as e:
            logger.warning(f"WHOIS reverse lookup failed: {e}")

    async def search_business_directories(self, phone_number: str, result: Dict):
        """Search business directories for phone number"""
        try:
            directories = [
                'yellowpages.com',
                'whitepages.com',
                'yelp.com',
                'bbb.org',
                'manta.com'
            ]
            
            for directory in directories:
                search_query = f'"{phone_number}" site:{directory}'
                try:
                    # search_results = list(search(search_query, num_results=5, stop=5))
                    search_results = await self.google_search_fallback(search_query, num_results=5)
                    
                    for url in search_results:
                        # Scrape business information
                        await self.scrape_business_info(url, result)
                    
                    await asyncio.sleep(random.uniform(2, 3))
                except Exception as e:
                    logger.warning(f"Business directory search failed for {directory}: {e}")
                    
        except Exception as e:
            logger.warning(f"Business directory search failed: {e}")

    async def scrape_business_info(self, url: str, result: Dict):
        """Scrape business information from directory pages"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for website links
                website_links = soup.find_all('a', href=re.compile(r'https?://(?!.*(?:yellowpages|whitepages|yelp|bbb|manta)).*'))
                
                for link in website_links:
                    href = link.get('href')
                    if href:
                        domain = tldextract.extract(href).registered_domain
                        if domain and domain not in result['linked_domains']:
                            result['linked_domains'].append(domain)
                            result['business_domains'].append(domain)
                            result['domain_count'] += 1
                            
        except Exception as e:
            logger.warning(f"Failed to scrape business info from {url}: {e}")

    async def get_comprehensive_profile_images(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive profile images from various platforms"""
        result = {
            "insta_dp": None, 
            "whatsapp_dp": None, 
            "telegram_dp": None,
            "facebook_dp": None,
            "twitter_dp": None,
            "profile_images_found": 0
        }
        
        # Method 1: Search for profile images on social platforms
        await self.search_profile_images(phone_number, result)
        
        # Method 2: Use reverse image search
        await self.reverse_image_search(phone_number, result)
        
        # Method 3: Scrape profile pictures with Selenium
        await self.scrape_profile_pictures_selenium(phone_number, result)

        return result

    async def search_profile_images(self, phone_number: str, result: Dict):
        """Search for profile images across platforms"""
        try:
            # Search for images associated with the phone number
            search_queries = [
                f'"{phone_number}" profile picture',
                f'"{phone_number}" avatar',
                f'"{phone_number}" photo',
                f'"{phone_number}" image'
            ]
            
            for query in search_queries:
                try:
                    # search_results = list(search(query, num_results=10, stop=10))
                    search_results = await self.google_search_fallback(query, num_results=10)
                    
                    for url in search_results:
                        # Check if URL contains image or profile references
                        if any(platform in url.lower() for platform in ['instagram', 'facebook', 'twitter', 'telegram']):
                            await self.extract_profile_image_from_url(url, result)
                    
                    await asyncio.sleep(random.uniform(2, 4))
                except Exception as e:
                    logger.warning(f"Profile image search failed: {e}")
                    
        except Exception as e:
            logger.warning(f"Profile image search failed: {e}")

    async def extract_profile_image_from_url(self, url: str, result: Dict):
        """Extract profile image from social media URL"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for profile images
                img_selectors = [
                    'img[alt*="profile"]',
                    'img[class*="profile"]',
                    'img[class*="avatar"]',
                    'img[src*="profile"]',
                    'meta[property="og:image"]'
                ]
                
                for selector in img_selectors:
                    img_elem = soup.select_one(selector)
                    if img_elem:
                        img_url = img_elem.get('src') or img_elem.get('content')
                        if img_url:
                            # Determine platform and save image URL
                            platform = self.determine_platform_from_url(url)
                            if platform:
                                result[f'{platform}_dp'] = img_url
                                result['profile_images_found'] += 1
                                
                                # Download and save image
                                await self.download_profile_image(img_url, platform, result)
                            break
                            
        except Exception as e:
            logger.warning(f"Failed to extract profile image from {url}: {e}")

    def determine_platform_from_url(self, url: str) -> str:
        """Determine social media platform from URL"""
        url_lower = url.lower()
        if 'instagram' in url_lower:
            return 'insta'
        elif 'facebook' in url_lower:
            return 'facebook'
        elif 'twitter' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'telegram' in url_lower or 't.me' in url_lower:
            return 'telegram'
        elif 'whatsapp' in url_lower:
            return 'whatsapp'
        return None

    async def download_profile_image(self, img_url: str, platform: str, result: Dict):
        """Download and save profile image"""
        try:
            if not img_url.startswith('http'):
                return
                
            headers = self.get_random_headers()
            response = self.session.get(img_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Create filename
                phone_clean = result.get('phone_number', 'unknown').replace('+', '').replace(' ', '')
                filename = f"output/images/{phone_clean}_{platform}.jpg"
                
                # Save image
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                # Update result with local file path
                result[f'{platform}_dp'] = filename
                
        except Exception as e:
            logger.warning(f"Failed to download profile image: {e}")

    async def reverse_image_search(self, phone_number: str, result: Dict):
        """Perform reverse image search for profile pictures"""
        try:
            # This would require integration with reverse image search APIs
            # For now, implement basic search
            pass
        except Exception as e:
            logger.warning(f"Reverse image search failed: {e}")

    async def scrape_profile_pictures_selenium(self, phone_number: str, result: Dict):
        """Use Selenium to scrape profile pictures from social platforms"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            driver = webdriver.Chrome(options=options)
            
            try:
                # Search for social media profiles
                clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
                
                # Instagram search (requires login for full access)
                try:
                    driver.get(f'https://www.instagram.com/explore/tags/{clean_number}/')
                    time.sleep(3)
                    
                    # Look for profile images
                    img_elements = driver.find_elements(By.CSS_SELECTOR, 'img[alt*="profile"], img[class*="avatar"]')
                    if img_elements:
                        img_url = img_elements[0].get_attribute('src')
                        if img_url:
                            result['insta_dp'] = img_url
                            await self.download_profile_image(img_url, 'insta', result)
                except Exception as e:
                    logger.warning(f"Instagram Selenium scraping failed: {e}")
                
                # Add more platform-specific scraping here
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.warning(f"Selenium profile picture scraping failed: {e}")

    async def get_comprehensive_reassignment(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive number reassignment information"""
        result = {
            "is_reassigned": None, 
            "original_carrier": None,
            "current_carrier": None,
            "reassignment_date": None,
            "port_history": []
        }
        
        # Method 1: HLRLookup API
        if self.hlrlookup_key:
            await self.hlr_lookup_api(phone_number, result)
        
        # Method 2: Carrier history lookup
        await self.lookup_carrier_history(phone_number, result)
        
        # Method 3: FCC database search
        await self.search_fcc_database(phone_number, result)

        return result

    async def hlr_lookup_api(self, phone_number: str, result: Dict):
        """Use HLRLookup API for number reassignment check"""
        try:
            url = "https://www.hlrlookup.com/api/hlr/"
            params = {
                'api_key': self.hlrlookup_key,
                'number': phone_number
            }
            
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    result['current_carrier'] = data.get('network_name')
                    result['is_reassigned'] = data.get('ported', False)
                    
                    if data.get('original_network_name'):
                        result['original_carrier'] = data['original_network_name']
                        
        except Exception as e:
            logger.warning(f"HLRLookup API failed: {e}")

    async def lookup_carrier_history(self, phone_number: str, result: Dict):
        """Lookup carrier history from various sources"""
        try:
            # Search for carrier change information
            search_queries = [
                f'"{phone_number}" carrier change',
                f'"{phone_number}" ported number',
                f'"{phone_number}" switched carrier'
            ]
            
            for query in search_queries:
                try:
                    # search_results = list(search(query, num_results=5, stop=5))
                    search_results = await self.google_search_fallback(query, num_results=5)
                    
                    for url in search_results:
                        # Scrape for carrier history information
                        await self.scrape_carrier_history(url, result)
                    
                    await asyncio.sleep(random.uniform(2, 3))
                except Exception as e:
                    logger.warning(f"Carrier history search failed: {e}")
                    
        except Exception as e:
            logger.warning(f"Carrier history lookup failed: {e}")

    async def scrape_carrier_history(self, url: str, result: Dict):
        """Scrape carrier history information"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Look for carrier names and dates
                carrier_patterns = [
                    r'(Verizon|AT&T|T-Mobile|Sprint|Idea|Airtel|Jio|BSNL)',
                    r'switched from (\w+) to (\w+)',
                    r'ported from (\w+)'
                ]
                
                for pattern in carrier_patterns:
                    matches = re.findall(pattern, text, re.I)
                    if matches:
                        if isinstance(matches[0], tuple):
                            result['original_carrier'] = matches[0][0]
                            if len(matches[0]) > 1:
                                result['current_carrier'] = matches[0][1]
                        else:
                            if not result.get('current_carrier'):
                                result['current_carrier'] = matches[0]
                        
                        result['is_reassigned'] = True
                        break
                        
        except Exception as e:
            logger.warning(f"Failed to scrape carrier history from {url}: {e}")

    async def search_fcc_database(self, phone_number: str, result: Dict):
        """Search FCC reassigned number database"""
        try:
            # This would require access to FCC databases
            # For now, implement basic search
            search_query = f'"{phone_number}" FCC reassigned database'
            
            # search_results = list(search(search_query, num_results=5, stop=5))
            search_results = await self.google_search_fallback(search_query, num_results=5)
            
            for url in search_results:
                if 'fcc.gov' in url:
                    # Scrape FCC page for reassignment info
                    await self.scrape_fcc_page(url, result)
                    
        except Exception as e:
            logger.warning(f"FCC database search failed: {e}")

    async def scrape_fcc_page(self, url: str, result: Dict):
        """Scrape FCC page for reassignment information"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Look for reassignment indicators
                if any(word in text.lower() for word in ['reassigned', 'ported', 'transferred']):
                    result['is_reassigned'] = True
                    
        except Exception as e:
            logger.warning(f"Failed to scrape FCC page {url}: {e}")

    async def get_comprehensive_online_mentions(self, phone_number: str) -> Dict[str, Any]:
        """Get comprehensive online mentions timeline"""
        result = {
            "first_seen_date": None, 
            "mention_count": 0, 
            "mention_sources": [],
            "mention_contexts": [],
            "latest_mention_date": None,
            "mention_timeline": []
        }
        
        # Method 1: Google/Bing searches with date filters
        await self.search_mentions_with_dates(phone_number, result)
        
        # Method 2: Wayback Machine CDX API
        await self.wayback_machine_search(phone_number, result)
        
        # Method 3: Social media timeline search
        await self.social_media_timeline_search(phone_number, result)
        
        # Method 4: News and article search
        await self.news_article_search(phone_number, result)

        return result

    async def search_mentions_with_dates(self, phone_number: str, result: Dict):
        """Search for mentions with date filters"""
        try:
            # Search with different date ranges
            date_ranges = [
                'after:2020',
                'after:2018',
                'after:2015',
                'after:2010'
            ]
            
            for date_range in date_ranges:
                search_query = f'"{phone_number}" {date_range}'
                
                try:
                    # search_results = list(search(search_query, num_results=10, stop=10))
                    search_results = await self.google_search_fallback(search_query, num_results=10)
                    
                    for url in search_results:
                        # Scrape page for mention context and date
                        await self.scrape_mention_page(url, result)
                        result['mention_count'] += 1
                        
                        if url not in result['mention_sources']:
                            result['mention_sources'].append(url)
                    
                    await asyncio.sleep(random.uniform(2, 4))
                except Exception as e:
                    logger.warning(f"Mention search failed for {date_range}: {e}")
                    
        except Exception as e:
            logger.warning(f"Mentions with dates search failed: {e}")

    async def scrape_mention_page(self, url: str, result: Dict):
        """Scrape individual page for mention context"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for date information
                date_patterns = [
                    r'\d{4}-\d{2}-\d{2}',
                    r'\d{2}/\d{2}/\d{4}',
                    r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
                ]
                
                text = soup.get_text()
                
                for pattern in date_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        mention_date = matches[0]
                        
                        # Update first seen date
                        if not result['first_seen_date'] or mention_date < result['first_seen_date']:
                            result['first_seen_date'] = mention_date
                        
                        # Update latest mention date
                        if not result['latest_mention_date'] or mention_date > result['latest_mention_date']:
                            result['latest_mention_date'] = mention_date
                        
                        # Add to timeline
                        result['mention_timeline'].append({
                            'date': mention_date,
                            'source': url,
                            'context': text[:200] + '...' if len(text) > 200 else text
                        })
                        break
                
                # Extract context around phone number
                phone_clean = result.get('phone_number', '').replace('+', '').replace('-', '').replace(' ', '')
                if phone_clean in text:
                    # Find context around the phone number
                    phone_index = text.find(phone_clean)
                    context_start = max(0, phone_index - 100)
                    context_end = min(len(text), phone_index + 100)
                    context = text[context_start:context_end].strip()
                    
                    if context not in result['mention_contexts']:
                        result['mention_contexts'].append(context)
                        
        except Exception as e:
            logger.warning(f"Failed to scrape mention page {url}: {e}")

    async def wayback_machine_search(self, phone_number: str, result: Dict):
        """Search Wayback Machine for historical mentions"""
        try:
            # Use Wayback Machine CDX API
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Search for archived pages containing the phone number
            cdx_url = f"http://web.archive.org/cdx/search/cdx"
            params = {
                'url': f'*{clean_number}*',
                'output': 'json',
                'limit': 100
            }
            
            response = self.session.get(cdx_url, params=params, timeout=20)
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 1:  # First row is headers
                    for row in data[1:]:  # Skip header row
                        if len(row) >= 2:
                            timestamp = row[1]  # Wayback timestamp
                            original_url = row[2]  # Original URL
                            
                            # Convert timestamp to readable date
                            if len(timestamp) >= 8:
                                date_str = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}"
                                
                                # Update first seen date
                                if not result['first_seen_date'] or date_str < result['first_seen_date']:
                                    result['first_seen_date'] = date_str
                                
                                # Add to timeline
                                result['mention_timeline'].append({
                                    'date': date_str,
                                    'source': f"archive.org: {original_url}",
                                    'context': 'Historical web archive'
                                })
                                
                                result['mention_count'] += 1
                                
        except Exception as e:
            logger.warning(f"Wayback Machine search failed: {e}")

    async def social_media_timeline_search(self, phone_number: str, result: Dict):
        """Search social media for timeline mentions"""
        try:
            platforms = ['twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com']
            
            for platform in platforms:
                search_query = f'"{phone_number}" site:{platform}'
                
                try:
                    # search_results = list(search(search_query, num_results=5, stop=5))
                    search_results = await self.google_search_fallback(search_query, num_results=5)
                    
                    for url in search_results:
                        await self.scrape_social_mention(url, result)
                        result['mention_count'] += 1
                        
                        if url not in result['mention_sources']:
                            result['mention_sources'].append(url)
                    
                    await asyncio.sleep(random.uniform(2, 3))
                except Exception as e:
                    logger.warning(f"Social media search failed for {platform}: {e}")
                    
        except Exception as e:
            logger.warning(f"Social media timeline search failed: {e}")

    async def scrape_social_mention(self, url: str, result: Dict):
        """Scrape social media mention for context"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for post dates
                date_selectors = [
                    'time[datetime]',
                    '[data-testid="timestamp"]',
                    '.timestamp',
                    '.date'
                ]
                
                for selector in date_selectors:
                    date_elem = soup.select_one(selector)
                    if date_elem:
                        date_value = date_elem.get('datetime') or date_elem.get_text(strip=True)
                        if date_value:
                            # Add to timeline
                            result['mention_timeline'].append({
                                'date': date_value,
                                'source': url,
                                'context': 'Social media mention'
                            })
                            break
                            
        except Exception as e:
            logger.warning(f"Failed to scrape social mention {url}: {e}")

    async def news_article_search(self, phone_number: str, result: Dict):
        """Search news articles for phone number mentions"""
        try:
            news_sites = [
                'news.google.com',
                'cnn.com',
                'bbc.com',
                'reuters.com',
                'ap.org'
            ]
            
            for site in news_sites:
                search_query = f'"{phone_number}" site:{site}'
                
                try:
                    # search_results = list(search(search_query, num_results=3, stop=3))
                    search_results = await self.google_search_fallback(search_query, num_results=3)
                    
                    for url in search_results:
                        await self.scrape_news_article(url, result)
                        result['mention_count'] += 1
                        
                        if url not in result['mention_sources']:
                            result['mention_sources'].append(url)
                    
                    await asyncio.sleep(random.uniform(2, 3))
                except Exception as e:
                    logger.warning(f"News search failed for {site}: {e}")
                    
        except Exception as e:
            logger.warning(f"News article search failed: {e}")

    async def scrape_news_article(self, url: str, result: Dict):
        """Scrape news article for mention context"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for article date
                date_selectors = [
                    'meta[property="article:published_time"]',
                    'time[pubdate]',
                    '.publish-date',
                    '.article-date'
                ]
                
                for selector in date_selectors:
                    date_elem = soup.select_one(selector)
                    if date_elem:
                        date_value = date_elem.get('content') or date_elem.get_text(strip=True)
                        if date_value:
                            # Add to timeline
                            result['mention_timeline'].append({
                                'date': date_value,
                                'source': url,
                                'context': 'News article mention'
                            })
                            break
                            
        except Exception as e:
            logger.warning(f"Failed to scrape news article {url}: {e}")

    async def export_comprehensive_results(self, clean_number: str, results: Dict):
        """Export comprehensive results to CSV and PDF"""
        try:
            # Export to CSV
            csv_file = f"output/{clean_number}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Category', 'Field', 'Value'])
                
                # def flatten_dict(d, parent_key='', category=''):
                #     items = []
                #     for k, v in d.items():
                #         new_key = f"{parent_key}.{k}" if parent_key else k
                #         current_category = category or k
                        
                #         if isinstance(v, dict):
                #             items.extend(flatten_dict(v, new_key, current_category).items())
                #         elif isinstance(v, list):
                #             if v:  # Only add non-empty lists
                #                 items.append((current_category, new_key, ', '.join(map(str, v))))
                #         else:
                #             if v is not None:  # Only add non-null values
                #                 items.append((current_category, new_key, str(v)))
                #     return dict(items)
                
                # flat_results = flatten_dict(results)
                # for (category, field, value) in [(k.split('.')[0], k, v) for k, v in flat_results.items()]:
                #     writer.writerow([category, field, value])

                def flatten_dict(d, parent_key=''):
                    items = []
                    for k, v in d.items():
                        new_key = f"{parent_key}.{k}" if parent_key else k
                        if isinstance(v, dict):
                            items.extend(flatten_dict(v, new_key))
                        elif isinstance(v, list):
                            items.append((new_key, ', '.join(map(str, v))))
                        else:
                            items.append((new_key, str(v)))
                    return items

                flat_results = flatten_dict(results)
                for key, value in flat_results:
                    writer.writerow([key, value])

            # Export to PDF with enhanced formatting
            pdf_file = f"output/{clean_number}.pdf"
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            story.append(Paragraph(f"📱 Comprehensive Phone Intelligence Report", styles['Title']))
            story.append(Paragraph(f"Phone Number: {results.get('phone_number', clean_number)}", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("📊 Executive Summary", styles['Heading1']))
            
            summary_points = []
            if results.get('basic_info', {}).get('carrier_name'):
                summary_points.append(f"Carrier: {results['basic_info']['carrier_name']}")
            if results.get('geolocation', {}).get('city'):
                summary_points.append(f"Location: {results['geolocation']['city']}, {results['geolocation'].get('state', '')}")
            if results.get('owner_spam', {}).get('caller_name'):
                summary_points.append(f"Owner: {results['owner_spam']['caller_name']}")
            if results.get('spam_reports', {}).get('report_count', 0) > 0:
                summary_points.append(f"Spam Reports: {results['spam_reports']['report_count']}")
            
            for point in summary_points:
                story.append(Paragraph(f"• {point}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Detailed sections
            section_icons = {
                'basic_info': '📋',
                'geolocation': '🌍',
                'owner_spam': '👤',
                'messaging_presence': '💬',
                'social_media_profiles': '📱',
                'breach_data': '🔓',
                'spam_reports': '⚠️',
                'domain_whois': '🌐',
                'profile_images': '🖼️',
                'number_reassignment': '🔄',
                'online_mentions': '🔍'
            }
            
            for section, data in results.items():
                if section not in ['phone_number', 'scan_date', 'errors'] and data:
                    icon = section_icons.get(section, '📄')
                    section_title = section.replace('_', ' ').title()
                    story.append(Paragraph(f"{icon} {section_title}", styles['Heading2']))
                    
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if value is not None and value != [] and value != '':
                                if isinstance(value, list):
                                    value_str = ', '.join(map(str, value[:5]))  # Limit to first 5 items
                                    if len(value) > 5:
                                        value_str += f" ... (+{len(value)-5} more)"
                                else:
                                    value_str = str(value)
                                
                                story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value_str}", styles['Normal']))
                    
                    story.append(Spacer(1, 12))
            
            # Errors section
            if results.get('errors'):
                story.append(Paragraph("⚠️ Errors Encountered", styles['Heading2']))
                for error in results['errors']:
                    story.append(Paragraph(f"• {error.get('feature', 'Unknown')}: {error.get('error', 'Unknown error')}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Footer
            story.append(Spacer(1, 20))
            story.append(Paragraph("Generated by Advanced Phone Intelligence Toolkit v2.0", styles['Normal']))
            story.append(Paragraph("⚠️ This report is for educational and legitimate OSINT purposes only.", styles['Normal']))
            
            doc.build(story)
            
        except Exception as e:
            logger.error(f"Failed to export comprehensive results: {e}")

