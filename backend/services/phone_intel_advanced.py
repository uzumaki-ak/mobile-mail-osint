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
import google.generativeai as genai
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import ssl
import urllib3

logger = logging.getLogger(__name__)

class AdvancedPhoneIntelService:
    def __init__(self):
        self.session = requests.Session()
        self.fix_ssl_session()
        
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
        
        # Skip HuggingFace models to avoid errors
        self.ner_pipeline = None
        self.sentiment_pipeline = None
        
        # Enhanced user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0'
        ]

    def fix_ssl_session(self):
        """Fix SSL certificate issues"""
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.session.verify = False
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    async def google_search_fallback(self, query: str, num_results: int = 10) -> List[str]:
        """Multiple fallback methods for Google search - FIXED VERSION"""
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
                    if results:
                        return results
            except Exception as e:
                logger.warning(f"SerpAPI search failed: {e}")
        
        # Fallback 2: Google Custom Search API (if available)
        if self.google_api_key:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.google_api_key,
                    'cx': '017576662512468239146:omuauf_lfve',
                    'q': query,
                    'num': min(num_results, 10)
                }
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if 'items' in data:
                        for item in data['items']:
                            results.append(item['link'])
                    if results:
                        return results
            except Exception as e:
                logger.warning(f"Google Custom Search failed: {e}")
        
        # Fallback 3: Direct Google scraping
        try:
            google_url = f"https://www.google.com/search?q={quote(query)}&num={num_results}"
            headers = {'User-Agent': random.choice(self.user_agents)}
            response = self.session.get(google_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Look for result links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/url?q='):
                        # Extract actual URL from Google redirect
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        if actual_url.startswith('http'):
                            results.append(actual_url)
                            if len(results) >= num_results:
                                break
                if results:
                    return results
        except Exception as e:
            logger.warning(f"Google scraping failed: {e}")
        
        # Fallback 4: Bing search scraping
        try:
            bing_url = f"https://www.bing.com/search?q={quote(query)}"
            headers = {'User-Agent': random.choice(self.user_agents)}
            response = self.session.get(bing_url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http') and 'bing.com' not in href and 'microsoft.com' not in href:
                        results.append(href)
                        if len(results) >= num_results:
                            break
                if results:
                    return results
        except Exception as e:
            logger.warning(f"Bing search scraping failed: {e}")
        
        # Fallback 5: Yahoo search scraping
        try:
            yahoo_url = f"https://search.yahoo.com/search?p={quote(query)}"
            headers = {'User-Agent': random.choice(self.user_agents)}
            response = self.session.get(yahoo_url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http') and 'yahoo.com' not in href:
                        results.append(href)
                        if len(results) >= num_results:
                            break
        except Exception as e:
            logger.warning(f"Yahoo search scraping failed: {e}")
        
        return results

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
                os.makedirs("output/raw", exist_ok=True)
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

        # Method 2: AbstractAPI
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

        # Fallback: phonenumbers library
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

        return result

    async def get_comprehensive_geolocation(self, phone_number: str) -> Dict[str, Any]:
        """ENHANCED geolocation with city detection"""
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
        
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Method 1: Enhanced Indian area code mapping
        if clean_number.startswith('91') and len(clean_number) >= 6:
            area_code = clean_number[2:6]
            
            # Comprehensive Indian area code database
            indian_area_codes = {
                # Rajasthan - Enhanced
                '8744': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '8929': {'city': 'Jodhpur', 'state': 'Rajasthan', 'region': 'North India'},
                '9414': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '9829': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '7597': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '8290': {'city': 'Udaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '9928': {'city': 'Jodhpur', 'state': 'Rajasthan', 'region': 'North India'},
                '9982': {'city': 'Jodhpur', 'state': 'Rajasthan', 'region': 'North India'},
                '9784': {'city': 'Kota', 'state': 'Rajasthan', 'region': 'North India'},
                '9460': {'city': 'Ajmer', 'state': 'Rajasthan', 'region': 'North India'},
                
                # Delhi
                '9811': {'city': 'New Delhi', 'state': 'Delhi', 'region': 'North India'},
                '9999': {'city': 'New Delhi', 'state': 'Delhi', 'region': 'North India'},
                '8447': {'city': 'New Delhi', 'state': 'Delhi', 'region': 'North India'},
                
                # Mumbai
                '9820': {'city': 'Mumbai', 'state': 'Maharashtra', 'region': 'West India'},
                '9821': {'city': 'Mumbai', 'state': 'Maharashtra', 'region': 'West India'},
                '8080': {'city': 'Mumbai', 'state': 'Maharashtra', 'region': 'West India'},
                
                # Add more as needed...
            }
            
            if area_code in indian_area_codes:
                location_info = indian_area_codes[area_code]
                result.update(location_info)
                result['timezone'] = 'Asia/Calcutta'
                result['country'] = 'IN'
                logger.info(f"Found location from area code {area_code}: {location_info}")

        # Method 2: phonenumbers library
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
                            if not result.get('city'):
                                result["city"] = parts[0]
                            if not result.get('state'):
                                result["state"] = parts[1]
                    
                # Get country
                country_code = phonenumbers.region_code_for_number(parsed)
                if country_code:
                    result["country"] = country_code
        except Exception as e:
            logger.warning(f"phonenumbers geolocation failed: {e}")

        # Method 3: Aggressive city search from multiple sources
        await self.aggressive_city_search(phone_number, result)
        
        # Method 4: Business directory location search
        await self.business_directory_location_search(phone_number, result)
        
        # Method 5: Social media location extraction
        await self.social_media_location_search(phone_number, result)

        return result

    async def aggressive_city_search(self, phone_number: str, result: Dict):
        """Aggressively search for city information"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Search queries for location
        location_queries = [
            f'"{phone_number}" city location address',
            f'"{phone_number}" contact address India',
            f'"{clean_number}" location city state',
            f'"{phone_number}" business address contact',
            f'"{phone_number}" office location city'
        ]
        
        for query in location_queries:
            try:
                search_results = await self.google_search_fallback(query, 10)
                
                for url in search_results:
                    try:
                        headers = self.get_random_headers()
                        response = self.session.get(url, headers=headers, timeout=15)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            text = soup.get_text().lower()
                            
                            # Look for Indian cities
                            indian_cities = [
                                'jaipur', 'jodhpur', 'udaipur', 'kota', 'ajmer', 'bikaner', 'alwar',
                                'delhi', 'mumbai', 'bangalore', 'chennai', 'hyderabad', 'kolkata', 
                                'pune', 'ahmedabad', 'surat', 'lucknow', 'kanpur', 'nagpur', 'indore'
                            ]
                            
                            for city in indian_cities:
                                if city in text and not result.get('city'):
                                    result['city'] = city.title()
                                    
                                    # Map city to state
                                    city_state_map = {
                                        'jaipur': 'Rajasthan', 'jodhpur': 'Rajasthan', 'udaipur': 'Rajasthan',
                                        'kota': 'Rajasthan', 'ajmer': 'Rajasthan', 'bikaner': 'Rajasthan',
                                        'alwar': 'Rajasthan', 'delhi': 'Delhi', 'mumbai': 'Maharashtra',
                                        'bangalore': 'Karnataka', 'chennai': 'Tamil Nadu', 'hyderabad': 'Telangana',
                                        'kolkata': 'West Bengal', 'pune': 'Maharashtra', 'ahmedabad': 'Gujarat',
                                        'surat': 'Gujarat', 'lucknow': 'Uttar Pradesh', 'kanpur': 'Uttar Pradesh',
                                        'nagpur': 'Maharashtra', 'indore': 'Madhya Pradesh'
                                    }
                                    
                                    if not result.get('state'):
                                        result['state'] = city_state_map.get(city, '')
                                    
                                    logger.info(f"Found city from search: {city.title()}")
                                    return
                    except Exception as e:
                        continue
                
                await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                logger.warning(f"Aggressive city search failed: {e}")

    async def business_directory_location_search(self, phone_number: str, result: Dict):
        """Search business directories for location"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        directories = [
            f'https://www.justdial.com/search/sp:{clean_number}',
            f'https://www.sulekha.com/search/{clean_number}',
            f'https://www.indiamart.com/search.mp?ss={clean_number}',
            f'https://www.tradeindia.com/search/{clean_number}',
            f'https://www.yellowpages.co.in/search/{clean_number}',
        ]
        
        for directory in directories:
            try:
                headers = self.get_random_headers()
                response = self.session.get(directory, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for address patterns
                    address_patterns = [
                        r'([A-Z][a-z]+),\s*([A-Z][a-z]+)',
                        r'Address[:\s]+([^,\n]+),?\s*([^,\n]+)',
                        r'Location[:\s]+([^,\n]+),?\s*([^,\n]+)'
                    ]
                    
                    text = soup.get_text()
                    for pattern in address_patterns:
                        matches = re.findall(pattern, text)
                        if matches:
                            city, state = matches[0]
                            if not result.get('city') and len(city.strip()) > 2:
                                result['city'] = city.strip()
                            if not result.get('state') and len(state.strip()) > 2:
                                result['state'] = state.strip()
                            break
                    
                    if result.get('city'):
                        break
                
                await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                logger.warning(f"Business directory search failed: {e}")

    async def social_media_location_search(self, phone_number: str, result: Dict):
        """Extract location from social media"""
        try:
            search_queries = [
                f'"{phone_number}" location site:facebook.com',
                f'"{phone_number}" address site:instagram.com',
                f'"{phone_number}" city site:linkedin.com'
            ]
            
            for query in search_queries:
                search_results = await self.google_search_fallback(query, 5)
                
                for url in search_results:
                    try:
                        headers = self.get_random_headers()
                        response = self.session.get(url, headers=headers, timeout=15)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            
                            # Look for location in meta tags
                            location_meta = soup.find('meta', property='og:location') or soup.find('meta', name='location')
                            if location_meta:
                                location = location_meta.get('content', '')
                                if ',' in location:
                                    parts = location.split(',')
                                    if not result.get('city'):
                                        result['city'] = parts[0].strip()
                                    if not result.get('state') and len(parts) > 1:
                                        result['state'] = parts[1].strip()
                    except Exception as e:
                        continue
                
                await asyncio.sleep(2)
        except Exception as e:
            logger.warning(f"Social media location search failed: {e}")

    async def get_comprehensive_owner_spam(self, phone_number: str) -> Dict[str, Any]:
        """SUPER AGGRESSIVE owner name detection"""
        result = {
            "caller_name": None, 
            "spam_score": 0.0, 
            "spam_tags": [],
            "caller_type": None,
            "business_name": None,
            "reputation_score": None,
            "report_count": 0
        }
        
        # Method 1: Enhanced Truecaller scraping
        await self.super_aggressive_truecaller(phone_number, result)
        
        # Method 2: Multiple caller ID databases
        await self.comprehensive_caller_id_scraping(phone_number, result)
        
        # Method 3: Business directory name search
        await self.business_directory_name_search(phone_number, result)
        
        # Method 4: Social media name extraction
        await self.social_media_name_extraction(phone_number, result)
        
        # Method 5: PDF and document search
        await self.pdf_document_name_search(phone_number, result)

        return result

    async def super_aggressive_truecaller(self, phone_number: str, result: Dict):
        """Super aggressive Truecaller scraping"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Multiple Truecaller approaches
        truecaller_urls = [
            f'https://www.truecaller.com/search/in/{clean_number}',
            f'https://www.truecaller.com/search/global/{clean_number}',
            f'https://www.truecaller.com/phone/{clean_number}',
            f'https://m.truecaller.com/search/{clean_number}',
            f'https://m.truecaller.com/in/{clean_number}',
        ]
        
        for url in truecaller_urls:
            try:
                # Try with different user agents
                for ua in self.user_agents:
                    headers = {
                        'User-Agent': ua,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    
                    response = self.session.get(url, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Multiple selectors for name
                        name_selectors = [
                            'h1[data-test-id="search-result-name"]',
                            '.search-result-name',
                            '.caller-name',
                            'h1.name',
                            '[class*="name"]',
                            '[data-name]',
                            'title',
                            'h1', 'h2', 'h3'
                        ]
                        
                        for selector in name_selectors:
                            elements = soup.select(selector)
                            for elem in elements:
                                name = elem.get_text(strip=True)
                                if name and len(name) > 2 and len(name) < 50:
                                    # Filter out common non-names
                                    if name.lower() not in ['unknown', 'private', 'hidden', 'truecaller', 'search']:
                                        result['caller_name'] = name
                                        logger.info(f"Found caller name from Truecaller: {name}")
                                        return
                        
                        # Look for spam indicators
                        spam_keywords = ['spam', 'scam', 'fraud', 'telemarketer', 'robocall', 'unwanted']
                        text_content = soup.get_text().lower()
                        
                        spam_count = sum(1 for keyword in spam_keywords if keyword in text_content)
                        if spam_count > 0:
                            result['spam_score'] = min(spam_count * 0.2, 1.0)
                            result['spam_tags'].extend([kw for kw in spam_keywords if kw in text_content])
                    
                    await asyncio.sleep(random.uniform(1, 2))
                    if result.get('caller_name'):
                        return
                        
            except Exception as e:
                logger.warning(f"Truecaller scraping failed for {url}: {e}")

    async def comprehensive_caller_id_scraping(self, phone_number: str, result: Dict):
        """Scrape ALL possible caller ID sites"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        caller_id_sites = [
            # Indian specific sites
            f'https://www.bharat-calls.com/{clean_number}',
            f'https://www.showcaller.com/phone-number/{clean_number}',
            f'https://www.findandtrace.com/trace-mobile-number-location/{clean_number}',
            f'https://www.mobilenumbertrackeronline.com/track/{clean_number}',
            f'https://www.getcontact.com/en/number/{clean_number}',
            f'https://sync.me/search/?q={clean_number}',
            
            # International sites
            f'https://www.whocalld.com/+{clean_number}',
            f'https://www.shouldianswer.com/phone-number/{clean_number}',
            f'https://www.callercenter.com/number/{clean_number}',
            f'https://www.spamcalls.net/en/number/{clean_number}',
            f'https://www.unknownphone.com/phone-number/{clean_number}',
            f'https://www.reversephonelookup.com/number/{clean_number}',
            f'https://www.phoneowner.net/lookup/{clean_number}',
            f'https://www.calleridtest.com/{clean_number}',
        ]
        
        for site in caller_id_sites:
            try:
                headers = self.get_random_headers()
                response = self.session.get(site, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for name patterns
                    name_patterns = [
                        r'(?:Name|Caller|Owner)[:\s]+([A-Za-z\s]{3,30})',
                        r'(?:Belongs to|Registered to)[:\s]+([A-Za-z\s]{3,30})',
                        r'<h[1-6][^>]*>([A-Za-z\s]{3,30})</h[1-6]>',
                    ]
                    
                    text = soup.get_text()
                    for pattern in name_patterns:
                        matches = re.findall(pattern, text, re.I)
                        if matches:
                            name = matches[0].strip()
                            if name and len(name) > 2 and not result.get('caller_name'):
                                result['caller_name'] = name
                                logger.info(f"Found caller name from {site}: {name}")
                                return
                
                await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                logger.warning(f"Caller ID scraping failed for {site}: {e}")

    async def business_directory_name_search(self, phone_number: str, result: Dict):
        """Search business directories for names"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        business_directories = [
            f'https://www.justdial.com/search/sp:{clean_number}',
            f'https://www.sulekha.com/search/{clean_number}',
            f'https://www.indiamart.com/search.mp?ss={clean_number}',
            f'https://www.tradeindia.com/search/{clean_number}',
            f'https://www.yellowpages.co.in/search/{clean_number}',
            f'https://www.olx.in/search?q={clean_number}',
            f'https://www.quikr.com/search/{clean_number}',
        ]
        
        for directory in business_directories:
            try:
                headers = self.get_random_headers()
                response = self.session.get(directory, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for business/person names
                    name_selectors = [
                        'h1', 'h2', 'h3',
                        '.business-name',
                        '.company-name',
                        '[class*="title"]',
                        '[class*="name"]'
                    ]
                    
                    for selector in name_selectors:
                        elements = soup.select(selector)
                        for elem in elements:
                            text = elem.get_text(strip=True)
                            if text and len(text) > 3 and len(text) < 50:
                                # Check if it looks like a name or business
                                if any(word in text.lower() for word in ['shop', 'store', 'company', 'service', 'restaurant', 'hotel']):
                                    result['business_name'] = text
                                    result['caller_type'] = 'business'
                                    if not result.get('caller_name'):
                                        result['caller_name'] = text
                                    logger.info(f"Found business name: {text}")
                                    return
                                elif re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', text):  # Looks like a person name
                                    result['caller_name'] = text
                                    result['caller_type'] = 'person'
                                    logger.info(f"Found person name: {text}")
                                    return
                
                await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                logger.warning(f"Business directory search failed: {e}")

    async def social_media_name_extraction(self, phone_number: str, result: Dict):
        """Extract names from social media profiles"""
        try:
            search_queries = [
                f'"{phone_number}" name profile',
                f'"{phone_number}" contact person',
                f'"{phone_number}" owner name',
                f'"{phone_number}" site:facebook.com',
                f'"{phone_number}" site:instagram.com',
                f'"{phone_number}" site:linkedin.com'
            ]
            
            for query in search_queries:
                search_results = await self.google_search_fallback(query, 10)
                
                for url in search_results:
                    if any(platform in url.lower() for platform in ['facebook', 'instagram', 'linkedin', 'twitter']):
                        try:
                            headers = self.get_random_headers()
                            response = self.session.get(url, headers=headers, timeout=15)
                            
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                
                                # Look for names in various places
                                name_sources = [
                                    soup.find('meta', property='og:title'),
                                    soup.find('meta', name='twitter:title'),
                                    soup.find('title'),
                                    soup.find('h1'),
                                ]
                                
                                for source in name_sources:
                                    if source:
                                        name = source.get('content') or source.get_text(strip=True)
                                        if name and len(name) > 2 and len(name) < 50:
                                            # Clean up the name
                                            name = re.sub(r'\s*\|\s*.*$', '', name)
                                            name = re.sub(r'\s*-\s*.*$', '', name)
                                            if name and not result.get('caller_name'):
                                                result['caller_name'] = name.strip()
                                                logger.info(f"Found name from social media: {name}")
                                                return
                        except Exception as e:
                            continue
                
                await asyncio.sleep(random.uniform(1, 2))
        except Exception as e:
            logger.warning(f"Social media name extraction failed: {e}")

    async def pdf_document_name_search(self, phone_number: str, result: Dict):
        """Search for phone number in PDFs and documents"""
        try:
            search_queries = [
                f'"{phone_number}" filetype:pdf',
                f'"{phone_number}" filetype:doc',
                f'"{phone_number}" filetype:docx',
                f'"{phone_number}" contact list filetype:pdf',
                f'"{phone_number}" directory filetype:pdf'
            ]
            
            for query in search_queries:
                search_results = await self.google_search_fallback(query, 5)
                
                for url in search_results:
                    if any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx']):
                        try:
                            headers = self.get_random_headers()
                            response = self.session.get(url, headers=headers, timeout=20)
                            
                            if response.status_code == 200:
                                # For PDFs, try to extract text (basic approach)
                                if '.pdf' in url.lower():
                                    # This is a simplified approach - in production you'd use PyPDF2 or similar
                                    content = response.content.decode('utf-8', errors='ignore')
                                    
                                    # Look for name patterns near the phone number
                                    phone_clean = phone_number.replace('+', '').replace('-', '').replace(' ', '')
                                    if phone_clean in content:
                                        # Extract text around the phone number
                                        phone_index = content.find(phone_clean)
                                        context = content[max(0, phone_index-200):phone_index+200]
                                        
                                        # Look for name patterns
                                        name_patterns = [
                                            r'([A-Z][a-z]+ [A-Z][a-z]+)',
                                            r'Name[:\s]+([A-Za-z\s]{3,30})',
                                            r'Contact[:\s]+([A-Za-z\s]{3,30})'
                                        ]
                                        
                                        for pattern in name_patterns:
                                            matches = re.findall(pattern, context)
                                            if matches:
                                                name = matches[0].strip()
                                                if name and not result.get('caller_name'):
                                                    result['caller_name'] = name
                                                    logger.info(f"Found name from PDF: {name}")
                                                    return
                        except Exception as e:
                            continue
                
                await asyncio.sleep(random.uniform(2, 3))
        except Exception as e:
            logger.warning(f"PDF document search failed: {e}")

    async def get_comprehensive_messaging_presence(self, phone_number: str) -> Dict[str, Any]:
        """ENHANCED messaging app detection"""
        result = {
            "whatsapp_active": None, 
            "telegram_active": None,
            "signal_active": None,
            "viber_active": None,
            "messenger_active": None
        }
        
        # Method 1: WhatsApp presence check
        await self.enhanced_whatsapp_check(phone_number, result)
        
        # Method 2: Telegram presence check
        await self.enhanced_telegram_check(phone_number, result)
        
        # Method 3: Other messaging apps
        await self.other_messaging_apps_check(phone_number, result)
        
        # Method 4: Social media messaging indicators
        await self.social_messaging_indicators(phone_number, result)
        
        # Method 5: Contact app searches
        await self.contact_app_searches(phone_number, result)

        return result

    async def enhanced_whatsapp_check(self, phone_number: str, result: Dict):
        """Enhanced WhatsApp presence detection"""
        try:
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Method 1: Try WhatsApp web link
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            
            try:
                url = f'https://wa.me/{clean_number}'
                driver.get(url)
                
                # Check if redirected to WhatsApp
                current_url = driver.current_url
                if 'whatsapp.com' in current_url or 'wa.me' in current_url:
                    result['whatsapp_active'] = True
                    logger.info(f"WhatsApp active for {phone_number}")
                else:
                    result['whatsapp_active'] = False
                    
            finally:
                driver.quit()
                
            # Method 2: Search for WhatsApp mentions
            search_queries = [
                f'"{phone_number}" whatsapp',
                f'"{phone_number}" wa.me',
                f'"{phone_number}" whatsapp contact'
            ]
            
            for query in search_queries:
                search_results = await self.google_search_fallback(query, 5)
                for url in search_results:
                    if 'whatsapp' in url.lower() or 'wa.me' in url.lower():
                        result['whatsapp_active'] = True
                        logger.info(f"Found WhatsApp mention for {phone_number}")
                        return
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.warning(f"WhatsApp check failed: {e}")
            result['whatsapp_active'] = None

    async def enhanced_telegram_check(self, phone_number: str, result: Dict):
        """Enhanced Telegram presence detection"""
        try:
            search_queries = [
                f'"{phone_number}" site:t.me',
                f'"{phone_number}" telegram',
                f'"{phone_number}" @telegram',
                f'"{phone_number}" telegram contact'
            ]
            
            for query in search_queries:
                try:
                    search_results = await self.google_search_fallback(query, 5)
                    for url in search_results:
                        if 't.me' in url or 'telegram' in url.lower():
                            result['telegram_active'] = True
                            logger.info(f"Found Telegram presence for {phone_number}")
                            return
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"Telegram search failed: {e}")
            
            result['telegram_active'] = False
            
        except Exception as e:
            logger.warning(f"Telegram check failed: {e}")
            result['telegram_active'] = None

    async def other_messaging_apps_check(self, phone_number: str, result: Dict):
        """Check other messaging apps"""
        apps = ['signal', 'viber', 'messenger']
        
        for app in apps:
            try:
                search_query = f'"{phone_number}" {app}'
                search_results = await self.google_search_fallback(search_query, 3)
                
                if search_results:
                    # Check if any results are relevant
                    for url in search_results:
                        if app in url.lower():
                            result[f'{app}_active'] = True
                            logger.info(f"Found {app} presence for {phone_number}")
                            break
                    else:
                        result[f'{app}_active'] = False
                else:
                    result[f'{app}_active'] = False
                    
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"{app} check failed: {e}")
                result[f'{app}_active'] = None

    async def social_messaging_indicators(self, phone_number: str, result: Dict):
        """Look for messaging indicators on social media"""
        try:
            search_queries = [
                f'"{phone_number}" contact whatsapp site:facebook.com',
                f'"{phone_number}" telegram site:instagram.com',
                f'"{phone_number}" message me'
            ]
            
            for query in search_queries:
                search_results = await self.google_search_fallback(query, 3)
                
                for url in search_results:
                    try:
                        headers = self.get_random_headers()
                        response = self.session.get(url, headers=headers, timeout=15)
                        
                        if response.status_code == 200:
                            text = response.text.lower()
                            
                            if 'whatsapp' in text and not result.get('whatsapp_active'):
                                result['whatsapp_active'] = True
                            if 'telegram' in text and not result.get('telegram_active'):
                                result['telegram_active'] = True
                    except Exception as e:
                        continue
                
                await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"Social messaging indicators failed: {e}")

    async def contact_app_searches(self, phone_number: str, result: Dict):
        """Search contact and directory apps"""
        try:
            contact_queries = [
                f'"{phone_number}" getcontact',
                f'"{phone_number}" sync.me',
                f'"{phone_number}" contact app'
            ]
            
            for query in contact_queries:
                search_results = await self.google_search_fallback(query, 3)
                
                for url in search_results:
                    if any(app in url.lower() for app in ['getcontact', 'sync.me', 'contact']):
                        # These apps often show messaging app presence
                        try:
                            headers = self.get_random_headers()
                            response = self.session.get(url, headers=headers, timeout=15)
                            
                            if response.status_code == 200:
                                text = response.text.lower()
                                
                                if 'whatsapp' in text:
                                    result['whatsapp_active'] = True
                                if 'telegram' in text:
                                    result['telegram_active'] = True
                        except Exception as e:
                            continue
                
                await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"Contact app searches failed: {e}")

    async def get_comprehensive_social_media(self, phone_number: str) -> Dict[str, Any]:
        """SUPER AGGRESSIVE social media detection"""
        result = {
            "instagram_url": None, 
            "twitter_url": None, 
            "facebook_url": None,
            "linkedin_url": None,
            "tiktok_url": None,
            "snapchat_url": None,
            "youtube_url": None
        }
        
        # Method 1: Direct platform searches
        await self.direct_social_platform_search(phone_number, result)
        
        # Method 2: Advanced Google dork searches
        await self.advanced_social_dork_search(phone_number, result)
        
        # Method 3: Username generation and testing
        await self.username_generation_search(phone_number, result)
        
        # Method 4: Social aggregator sites
        await self.social_aggregator_search(phone_number, result)
        
        # Method 5: Cached and archived searches
        await self.cached_social_search(phone_number, result)

        return result

    async def direct_social_platform_search(self, phone_number: str, result: Dict):
        """Direct searches on social platforms"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        platforms = {
            'instagram': [
                f'https://www.instagram.com/explore/tags/{clean_number}/',
                f'https://www.instagram.com/{clean_number}/',
                f'https://www.instagram.com/web/search/topsearch/?query={clean_number}'
            ],
            'facebook': [
                f'https://www.facebook.com/search/people/?q={clean_number}',
                f'https://www.facebook.com/public/{clean_number}',
                f'https://m.facebook.com/search/?q={clean_number}'
            ],
            'twitter': [
                f'https://twitter.com/search?q={clean_number}',
                f'https://twitter.com/{clean_number}',
                f'https://x.com/search?q={clean_number}'
            ],
            'linkedin': [
                f'https://www.linkedin.com/search/results/people/?keywords={clean_number}',
                f'https://www.linkedin.com/in/{clean_number}'
            ]
        }
        
        for platform, urls in platforms.items():
            for url in urls:
                try:
                    headers = self.get_random_headers()
                    response = self.session.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 200 and platform in response.url.lower():
                        # Check if page has actual content (not just search page)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for profile indicators
                        profile_indicators = [
                            'profile', 'user', 'account', 'posts', 'followers', 'following'
                        ]
                        
                        text = soup.get_text().lower()
                        if any(indicator in text for indicator in profile_indicators):
                            result[f'{platform}_url'] = response.url
                            logger.info(f"Found {platform} profile: {response.url}")
                            break
                    
                    await asyncio.sleep(random.uniform(1, 2))
                except Exception as e:
                    logger.warning(f"Direct {platform} search failed: {e}")

    async def advanced_social_dork_search(self, phone_number: str, result: Dict):
        """Advanced Google dork searches for social media"""
        platforms = {
            'instagram': ['instagram.com', 'insta'],
            'facebook': ['facebook.com', 'fb.com'],
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'tiktok': ['tiktok.com'],
            'youtube': ['youtube.com', 'youtu.be']
        }
        
        for platform, domains in platforms.items():
            # Multiple search strategies
            search_queries = [
                f'"{phone_number}" site:{domains[0]}',
                f'"{phone_number}" inurl:{domains[0]}',
                f'"{phone_number}" {platform} profile',
                f'"{phone_number}" contact {platform}',
                f'intitle:"{phone_number}" site:{domains[0]}',
                f'"{phone_number}" {platform} account',
                f'"{phone_number}" {platform} page'
            ]
            
            for query in search_queries:
                try:
                    search_results = await self.google_search_fallback(query, 5)
                    
                    for url in search_results:
                        if any(domain in url.lower() for domain in domains):
                            result[f'{platform}_url'] = url
                            logger.info(f"Found {platform} via dork search: {url}")
                            break
                    
                    if result.get(f'{platform}_url'):
                        break
                    
                    await asyncio.sleep(random.uniform(1, 2))
                except Exception as e:
                    logger.warning(f"Social dork search failed for {platform}: {e}")

    async def username_generation_search(self, phone_number: str, result: Dict):
        """Generate possible usernames and test them"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Generate possible usernames
        possible_usernames = [
            clean_number,
            clean_number[-10:],  # Last 10 digits
            clean_number[-8:],   # Last 8 digits
            clean_number[-6:],   # Last 6 digits
            f"user{clean_number[-6:]}",
            f"{clean_number[:3]}{clean_number[-4:]}",
            f"phone{clean_number[-4:]}",
            f"mobile{clean_number[-4:]}"
        ]
        
        platforms = {
            'instagram': 'instagram.com',
            'twitter': 'twitter.com',
            'facebook': 'facebook.com',
            'tiktok': 'tiktok.com',
            'youtube': 'youtube.com'
        }
        
        for username in possible_usernames:
            for platform, domain in platforms.items():
                try:
                    url = f'https://{domain}/{username}'
                    headers = self.get_random_headers()
                    response = self.session.head(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        result[f'{platform}_url'] = url
                        logger.info(f"Found {platform} profile via username: {url}")
                    
                    await asyncio.sleep(0.5)
                except Exception as e:
                    continue

    async def social_aggregator_search(self, phone_number: str, result: Dict):
        """Search social media aggregator sites"""
        aggregator_sites = [
            f'https://pipl.com/search/?q={phone_number}',
            f'https://www.spokeo.com/search?q={phone_number}',
            f'https://www.whitepages.com/phone/1-{phone_number.replace("+", "").replace("-", "")}',
            f'https://www.truepeoplesearch.com/results?phoneno={phone_number}',
            f'https://www.fastpeoplesearch.com/phone/{phone_number.replace("+", "").replace("-", "")}',
            f'https://www.beenverified.com/people/{phone_number}',
            f'https://www.intelius.com/people-search/phone/{phone_number}'
        ]
        
        for site in aggregator_sites:
            try:
                headers = self.get_random_headers()
                response = self.session.get(site, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for social media links
                    social_links = soup.find_all('a', href=True)
                    for link in social_links:
                        href = link['href'].lower()
                        
                        if 'instagram.com' in href and not result.get('instagram_url'):
                            result['instagram_url'] = link['href']
                        elif 'facebook.com' in href and not result.get('facebook_url'):
                            result['facebook_url'] = link['href']
                        elif ('twitter.com' in href or 'x.com' in href) and not result.get('twitter_url'):
                            result['twitter_url'] = link['href']
                        elif 'linkedin.com' in href and not result.get('linkedin_url'):
                            result['linkedin_url'] = link['href']
                        elif 'tiktok.com' in href and not result.get('tiktok_url'):
                            result['tiktok_url'] = link['href']
                        elif 'youtube.com' in href and not result.get('youtube_url'):
                            result['youtube_url'] = link['href']
                
                await asyncio.sleep(random.uniform(2, 3))
            except Exception as e:
                logger.warning(f"Social aggregator search failed for {site}: {e}")

    async def cached_social_search(self, phone_number: str, result: Dict):
        """Search cached and archived social media pages"""
        try:
            # Wayback Machine search
            wayback_url = f'http://web.archive.org/cdx/search/cdx?url=*{phone_number}*&output=json&limit=50'
            response = self.session.get(wayback_url, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 1:
                    for row in data[1:]:  # Skip header
                        if len(row) >= 3:
                            original_url = row[2]
                            
                            if 'instagram.com' in original_url and not result.get('instagram_url'):
                                result['instagram_url'] = original_url
                            elif 'facebook.com' in original_url and not result.get('facebook_url'):
                                result['facebook_url'] = original_url
                            elif 'twitter.com' in original_url and not result.get('twitter_url'):
                                result['twitter_url'] = original_url
                            elif 'linkedin.com' in original_url and not result.get('linkedin_url'):
                                result['linkedin_url'] = original_url
            
            # Google Cache search
            cache_queries = [
                f'cache:{phone_number} site:instagram.com',
                f'cache:{phone_number} site:facebook.com',
                f'cache:{phone_number} site:twitter.com',
                f'cache:{phone_number} site:linkedin.com'
            ]
            
            for query in cache_queries:
                search_results = await self.google_search_fallback(query, 3)
                
                for url in search_results:
                    if 'webcache.googleusercontent.com' in url:
                        # Extract platform from cache URL
                        if 'instagram.com' in url and not result.get('instagram_url'):
                            result['instagram_url'] = url
                        elif 'facebook.com' in url and not result.get('facebook_url'):
                            result['facebook_url'] = url
                        elif 'twitter.com' in url and not result.get('twitter_url'):
                            result['twitter_url'] = url
                        elif 'linkedin.com' in url and not result.get('linkedin_url'):
                            result['linkedin_url'] = url
                
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.warning(f"Cached social search failed: {e}")

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
            search_queries = [
                f'"{phone_number}" breach database',
                f'"{phone_number}" data leak',
                f'"{phone_number}" exposed data',
                f'"{phone_number}" site:pastebin.com',
                f'"{phone_number}" site:ghostbin.com'
            ]
            
            for query in search_queries:
                try:
                    search_results = await self.google_search_fallback(query, 10)
                    for url in search_results:
                        if any(site in url for site in ['pastebin', 'ghostbin', 'leak', 'breach']):
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
                    result['breached_emails'].extend(emails[:5])
                    result['breach_sources'].append(url)
                    result['breach_dates'].append(datetime.now().strftime('%Y-%m-%d'))
                    
        except Exception as e:
            logger.warning(f"Failed to scrape breach page {url}: {e}")

    async def check_hibp_style_databases(self, phone_number: str, result: Dict):
        """Check HaveIBeenPwned style databases"""
        try:
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
                search_results = await self.google_search_fallback(search_query, 5)
                
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

        return result

    async def scrape_800notes_comprehensive(self, phone_number: str, result: Dict):
        """Comprehensive 800notes.com scraping"""
        try:
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
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
                            if text and len(text) > 20:
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
                    search_results = await self.google_search_fallback(query, 10)
                    
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
            for domain in result['linked_domains'][:5]:
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
                    search_results = await self.google_search_fallback(search_query, 5)
                    
                    for url in search_results:
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
        """ENHANCED profile image detection"""
        result = {
            "insta_dp": None, 
            "whatsapp_dp": None, 
            "telegram_dp": None,
            "facebook_dp": None,
            "twitter_dp": None,
            "profile_images_found": 0
        }
        
        # Method 1: Search for profile images on social platforms
        await self.aggressive_profile_image_search(phone_number, result)
        
        # Method 2: Scrape profile pictures with Selenium
        await self.selenium_profile_scraping(phone_number, result)
        
        # Method 3: Contact app profile searches
        await self.contact_app_profile_search(phone_number, result)
        
        # Method 4: Business profile images
        await self.business_profile_image_search(phone_number, result)
        
        # Method 5: Cached image searches
        await self.cached_image_search(phone_number, result)

        return result

    async def aggressive_profile_image_search(self, phone_number: str, result: Dict):
        """Aggressively search for profile images"""
        try:
            search_queries = [
                f'"{phone_number}" profile picture',
                f'"{phone_number}" avatar',
                f'"{phone_number}" photo',
                f'"{phone_number}" image',
                f'"{phone_number}" dp',
                f'"{phone_number}" profile photo'
            ]
            
            for query in search_queries:
                try:
                    search_results = await self.google_search_fallback(query, 15)
                    
                    for url in search_results:
                        if any(platform in url.lower() for platform in ['instagram', 'facebook', 'twitter', 'telegram', 'whatsapp']):
                            await self.extract_profile_image_from_url(url, result, phone_number)
                    
                    await asyncio.sleep(random.uniform(2, 4))
                except Exception as e:
                    logger.warning(f"Profile image search failed: {e}")
                    
        except Exception as e:
            logger.warning(f"Aggressive profile image search failed: {e}")

    async def extract_profile_image_from_url(self, url: str, result: Dict, phone_number: str):
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
                    'meta[property="og:image"]',
                    'img[class*="user"]',
                    'img[class*="photo"]'
                ]
                
                for selector in img_selectors:
                    img_elem = soup.select_one(selector)
                    if img_elem:
                        img_url = img_elem.get('src') or img_elem.get('content')
                        if img_url:
                            platform = self.determine_platform_from_url(url)
                            if platform:
                                result[f'{platform}_dp'] = img_url
                                result['profile_images_found'] += 1
                                
                                # Download and save image
                                await self.download_profile_image(img_url, platform, phone_number)
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

    async def download_profile_image(self, img_url: str, platform: str, phone_number: str):
        """Download and save profile image"""
        try:
            if not img_url.startswith('http'):
                return
                
            headers = self.get_random_headers()
            response = self.session.get(img_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Create directories
                os.makedirs("output/images", exist_ok=True)
                
                # Create filename
                phone_clean = phone_number.replace('+', '').replace(' ', '')
                filename = f"output/images/{phone_clean}_{platform}.jpg"
                
                # Save image
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Downloaded profile image: {filename}")
                
        except Exception as e:
            logger.warning(f"Failed to download profile image: {e}")

    async def selenium_profile_scraping(self, phone_number: str, result: Dict):
        """Use Selenium for dynamic profile scraping"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            driver = webdriver.Chrome(options=options)
            
            try:
                clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
                
                # Try Instagram
                try:
                    driver.get(f'https://www.instagram.com/explore/tags/{clean_number}/')
                    time.sleep(3)
                    
                    img_elements = driver.find_elements(By.CSS_SELECTOR, 'img[alt*="profile"], img[class*="avatar"]')
                    if img_elements:
                        img_url = img_elements[0].get_attribute('src')
                        if img_url:
                            result['insta_dp'] = img_url
                            result['profile_images_found'] += 1
                            await self.download_profile_image(img_url, 'insta', phone_number)
                except Exception as e:
                    logger.warning(f"Instagram Selenium scraping failed: {e}")
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.warning(f"Selenium profile scraping failed: {e}")

    async def contact_app_profile_search(self, phone_number: str, result: Dict):
        """Search contact apps for profile images"""
        try:
            contact_queries = [
                f'"{phone_number}" getcontact profile',
                f'"{phone_number}" sync.me photo',
                f'"{phone_number}" truecaller image'
            ]
            
            for query in contact_queries:
                search_results = await self.google_search_fallback(query, 5)
                
                for url in search_results:
                    await self.extract_profile_image_from_url(url, result)
                
                await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"Contact app profile search failed: {e}")

    async def business_profile_image_search(self, phone_number: str, result: Dict):
        """Search for business profile images"""
        try:
            business_queries = [
                f'"{phone_number}" business logo',
                f'"{phone_number}" company photo',
                f'"{phone_number}" office image'
            ]
            
            for query in business_queries:
                search_results = await self.google_search_fallback(query, 5)
                
                for url in search_results:
                    await self.extract_profile_image_from_url(url, result)
                
                await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"Business profile image search failed: {e}")

    async def cached_image_search(self, phone_number: str, result: Dict):
        """Search cached images"""
        try:
            cache_queries = [
                f'"{phone_number}" image cache:',
                f'"{phone_number}" photo cached'
            ]
            
            for query in cache_queries:
                search_results = await self.google_search_fallback(query, 5)
                
                for url in search_results:
                    if 'webcache' in url or 'cache' in url:
                        await self.extract_profile_image_from_url(url, result)
                
                await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"Cached image search failed: {e}")

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
            search_queries = [
                f'"{phone_number}" carrier change',
                f'"{phone_number}" ported number',
                f'"{phone_number}" switched carrier'
            ]
            
            for query in search_queries:
                try:
                    search_results = await self.google_search_fallback(query, 5)
                    
                    for url in search_results:
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
            search_query = f'"{phone_number}" FCC reassigned database'
            
            search_results = await self.google_search_fallback(search_query, 5)
            
            for url in search_results:
                if 'fcc.gov' in url:
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
                
                if any(word in text.lower() for word in ['reassigned', 'ported', 'transferred']):
                    result['is_reassigned'] = True
                    
        except Exception as e:
            logger.warning(f"Failed to scrape FCC page {url}: {e}")

    async def get_comprehensive_online_mentions(self, phone_number: str) -> Dict[str, Any]:
        """SUPER AGGRESSIVE online mentions search"""
        result = {
            "first_seen_date": None, 
            "mention_count": 0, 
            "mention_sources": [],
            "mention_contexts": [],
            "latest_mention_date": None,
            "mention_timeline": []
        }
        
        # Method 1: Comprehensive search with date filters
        await self.comprehensive_mentions_search(phone_number, result)
        
        # Method 2: Wayback Machine search
        await self.wayback_machine_search(phone_number, result)
        
        # Method 3: PDF and document mentions
        await self.pdf_document_mentions_search(phone_number, result)
        
        # Method 4: Social media timeline search
        await self.social_media_timeline_search(phone_number, result)
        
        # Method 5: News and article search
        await self.news_article_search(phone_number, result)

        return result

    async def comprehensive_mentions_search(self, phone_number: str, result: Dict):
        """Comprehensive search for online mentions"""
        try:
            # Multiple search strategies
            search_strategies = [
                f'"{phone_number}"',
                f'"{phone_number}" contact',
                f'"{phone_number}" phone',
                f'"{phone_number}" mobile',
                f'"{phone_number}" number',
                f'"{phone_number}" call',
                f'"{phone_number}" address',
                f'"{phone_number}" business',
                f'"{phone_number}" person',
                f'"{phone_number}" owner'
            ]
            
            for query in search_strategies:
                try:
                    search_results = await self.google_search_fallback(query, 20)
                    
                    for url in search_results:
                        await self.scrape_mention_page(url, result)
                        result['mention_count'] += 1
                        
                        if url not in result['mention_sources']:
                            result['mention_sources'].append(url)
                    
                    await asyncio.sleep(random.uniform(2, 4))
                except Exception as e:
                    logger.warning(f"Comprehensive mention search failed: {e}")
                    
        except Exception as e:
            logger.warning(f"Comprehensive mentions search failed: {e}")

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
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            cdx_url = f"http://web.archive.org/cdx/search/cdx"
            params = {
                'url': f'*{clean_number}*',
                'output': 'json',
                'limit': 100
            }
            
            response = self.session.get(cdx_url, params=params, timeout=20)
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 1:
                    for row in data[1:]:
                        if len(row) >= 2:
                            timestamp = row[1]
                            original_url = row[2]
                            
                            if len(timestamp) >= 8:
                                date_str = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}"
                                
                                if not result['first_seen_date'] or date_str < result['first_seen_date']:
                                    result['first_seen_date'] = date_str
                                
                                result['mention_timeline'].append({
                                    'date': date_str,
                                    'source': f"archive.org: {original_url}",
                                    'context': 'Historical web archive'
                                })
                                
                                result['mention_count'] += 1
                                
        except Exception as e:
            logger.warning(f"Wayback Machine search failed: {e}")

    async def pdf_document_mentions_search(self, phone_number: str, result: Dict):
        """Search for mentions in PDF documents"""
        try:
            pdf_queries = [
                f'"{phone_number}" filetype:pdf',
                f'"{phone_number}" filetype:doc',
                f'"{phone_number}" filetype:docx',
                f'"{phone_number}" filetype:xls',
                f'"{phone_number}" filetype:ppt'
            ]
            
            for query in pdf_queries:
                search_results = await self.google_search_fallback(query, 10)
                
                for url in search_results:
                    if any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.ppt']):
                        try:
                            headers = self.get_random_headers()
                            response = self.session.get(url, headers=headers, timeout=20)
                            
                            if response.status_code == 200:
                                # Basic text extraction for documents
                                content = response.content.decode('utf-8', errors='ignore')
                                
                                phone_clean = phone_number.replace('+', '').replace('-', '').replace(' ', '')
                                if phone_clean in content:
                                    result['mention_sources'].append(url)
                                    result['mention_count'] += 1
                                    
                                    # Extract context
                                    phone_index = content.find(phone_clean)
                                    context = content[max(0, phone_index-200):phone_index+200]
                                    result['mention_contexts'].append(context)
                                    
                                    logger.info(f"Found phone number in document: {url}")
                        except Exception as e:
                            continue
                
                await asyncio.sleep(random.uniform(2, 3))
        except Exception as e:
            logger.warning(f"PDF document mentions search failed: {e}")

    async def social_media_timeline_search(self, phone_number: str, result: Dict):
        """Search social media for timeline mentions"""
        try:
            platforms = ['twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com']
            
            for platform in platforms:
                search_query = f'"{phone_number}" site:{platform}'
                
                try:
                    search_results = await self.google_search_fallback(search_query, 5)
                    
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
                    search_results = await self.google_search_fallback(search_query, 3)
                    
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
            # Create output directory
            os.makedirs("output", exist_ok=True)
            
            # Export to CSV
            csv_file = f"output/{clean_number}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Category', 'Field', 'Value'])
                
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

            # Export to PDF
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
                                    value_str = ', '.join(map(str, value[:5]))
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
            story.append(Paragraph("Generated by Advanced Phone Intelligence Toolkit v3.0", styles['Normal']))
            story.append(Paragraph("⚠️ This report is for educational and legitimate OSINT purposes only.", styles['Normal']))
            
            doc.build(story)
            
        except Exception as e:
            logger.error(f"Failed to export comprehensive results: {e}")
