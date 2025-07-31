# import asyncio
# import json
# import logging
# import os
# import re
# import requests
# from datetime import datetime
# from typing import Dict, Any, List, Optional
# from urllib.parse import quote, urljoin
# import random
# from bs4 import BeautifulSoup
# import phonenumbers
# from phonenumbers import geocoder, carrier, timezone
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import httpx
# import ssl
# import urllib3

# logger = logging.getLogger(__name__)

# class EnhancedPhoneScrapers:
#     def __init__(self, session, api_keys):
#         self.session = session
#         self.api_keys = api_keys
        
#         # Disable SSL warnings
#         urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
#         # Enhanced user agents
#         self.user_agents = [
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
#         ]

#     async def enhanced_geolocation_search(self, phone_number: str) -> Dict[str, Any]:
#         """5 fallback methods for geolocation"""
#         result = {"city": None, "state": None, "timezone": None, "latitude": None, "longitude": None}
        
#         # Method 1: Area code database lookup
#         await self.area_code_database_lookup(phone_number, result)
        
#         # Method 2: Carrier location databases
#         await self.carrier_location_lookup(phone_number, result)
        
#         # Method 3: Google Maps API geocoding
#         await self.google_maps_geocoding(phone_number, result)
        
#         # Method 4: Multiple location scraping sites
#         await self.scrape_location_sites(phone_number, result)
        
#         # Method 5: Social media location extraction
#         await self.social_media_location_extraction(phone_number, result)
        
#         return result

#     async def area_code_database_lookup(self, phone_number: str, result: Dict):
#         """Enhanced area code database with Indian numbers"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         # Indian area codes (first 4 digits after country code)
#         if clean_number.startswith('91') and len(clean_number) >= 6:
#             area_code = clean_number[2:6]  # Get area code
            
#             # Enhanced Indian area code mapping
#             indian_area_codes = {
#                 # Rajasthan
#                 '8744': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
#                 '9414': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
#                 '9829': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
#                 '7597': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
#                 '8290': {'city': 'Udaipur', 'state': 'Rajasthan', 'region': 'North India'},
#                 '9928': {'city': 'Jodhpur', 'state': 'Rajasthan', 'region': 'North India'},
                
#                 # Delhi
#                 '9811': {'city': 'New Delhi', 'state': 'Delhi', 'region': 'North India'},
#                 '9999': {'city': 'New Delhi', 'state': 'Delhi', 'region': 'North India'},
#                 '8447': {'city': 'New Delhi', 'state': 'Delhi', 'region': 'North India'},
                
#                 # Mumbai
#                 '9820': {'city': 'Mumbai', 'state': 'Maharashtra', 'region': 'West India'},
#                 '9821': {'city': 'Mumbai', 'state': 'Maharashtra', 'region': 'West India'},
#                 '8080': {'city': 'Mumbai', 'state': 'Maharashtra', 'region': 'West India'},
                
#                 # Bangalore
#                 '9845': {'city': 'Bangalore', 'state': 'Karnataka', 'region': 'South India'},
#                 '9844': {'city': 'Bangalore', 'state': 'Karnataka', 'region': 'South India'},
#                 '8050': {'city': 'Bangalore', 'state': 'Karnataka', 'region': 'South India'},
                
#                 # Chennai
#                 '9840': {'city': 'Chennai', 'state': 'Tamil Nadu', 'region': 'South India'},
#                 '9841': {'city': 'Chennai', 'state': 'Tamil Nadu', 'region': 'South India'},
#                 '8939': {'city': 'Chennai', 'state': 'Tamil Nadu', 'region': 'South India'},
                
#                 # Hyderabad
#                 '9849': {'city': 'Hyderabad', 'state': 'Telangana', 'region': 'South India'},
#                 '9866': {'city': 'Hyderabad', 'state': 'Telangana', 'region': 'South India'},
#                 '8179': {'city': 'Hyderabad', 'state': 'Telangana', 'region': 'South India'},
                
#                 # Kolkata
#                 '9830': {'city': 'Kolkata', 'state': 'West Bengal', 'region': 'East India'},
#                 '9831': {'city': 'Kolkata', 'state': 'West Bengal', 'region': 'East India'},
#                 '8017': {'city': 'Kolkata', 'state': 'West Bengal', 'region': 'East India'},
                
#                 # Pune
#                 '9822': {'city': 'Pune', 'state': 'Maharashtra', 'region': 'West India'},
#                 '9823': {'city': 'Pune', 'state': 'Maharashtra', 'region': 'West India'},
#                 '8888': {'city': 'Pune', 'state': 'Maharashtra', 'region': 'West India'},
#             }
            
#             if area_code in indian_area_codes:
#                 location_info = indian_area_codes[area_code]
#                 result.update(location_info)
#                 result['timezone'] = 'Asia/Calcutta'
#                 logger.info(f"Found location from area code {area_code}: {location_info}")

#     async def carrier_location_lookup(self, phone_number: str, result: Dict):
#         """Lookup location from carrier databases"""
#         try:
#             # Multiple carrier lookup sites
#             sites = [
#                 f'https://www.hlrlookup.com/lookup/{phone_number}',
#                 f'https://www.carrierlookup.com/index.php/lookup/carrier?msisdn={phone_number.replace("+", "")}',
#                 f'https://www.freecarrierlookup.com/lookup.php?number={phone_number.replace("+", "")}',
#                 f'https://www.phonevalidator.com/index.php/api/v1/validate?phone={phone_number}',
#                 f'https://numverify.com/php_helper_scripts/phone_api.php?secret_key=demo&number={phone_number}'
#             ]
            
#             for site in sites:
#                 try:
#                     headers = {'User-Agent': random.choice(self.user_agents)}
#                     response = self.session.get(site, headers=headers, timeout=15, verify=False)
                    
#                     if response.status_code == 200:
#                         soup = BeautifulSoup(response.content, 'html.parser')
#                         text = soup.get_text().lower()
                        
#                         # Look for Indian cities
#                         indian_cities = ['jaipur', 'delhi', 'mumbai', 'bangalore', 'chennai', 'hyderabad', 'kolkata', 'pune', 'ahmedabad', 'surat']
#                         for city in indian_cities:
#                             if city in text and not result.get('city'):
#                                 result['city'] = city.title()
                                
#                                 # Map city to state
#                                 city_state_map = {
#                                     'jaipur': 'Rajasthan', 'delhi': 'Delhi', 'mumbai': 'Maharashtra',
#                                     'bangalore': 'Karnataka', 'chennai': 'Tamil Nadu', 'hyderabad': 'Telangana',
#                                     'kolkata': 'West Bengal', 'pune': 'Maharashtra', 'ahmedabad': 'Gujarat', 'surat': 'Gujarat'
#                                 }
#                                 result['state'] = city_state_map.get(city, '')
#                                 break
                        
#                         if result.get('city'):
#                             break
                    
#                     await asyncio.sleep(random.uniform(1, 2))
#                 except Exception as e:
#                     logger.warning(f"Carrier location lookup failed for {site}: {e}")
                    
#         except Exception as e:
#             logger.warning(f"Carrier location lookup failed: {e}")

#     async def google_maps_geocoding(self, phone_number: str, result: Dict):
#         """Use Google Maps API for geocoding"""
#         try:
#             if self.api_keys.get('google_api_key'):
#                 # Search for businesses with this phone number
#                 url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
#                 params = {
#                     'query': phone_number,
#                     'key': self.api_keys['google_api_key']
#                 }
                
#                 response = self.session.get(url, params=params, timeout=15)
#                 if response.status_code == 200:
#                     data = response.json()
#                     if data.get('results'):
#                         place = data['results'][0]
#                         if 'geometry' in place:
#                             location = place['geometry']['location']
#                             result['latitude'] = location.get('lat')
#                             result['longitude'] = location.get('lng')
                        
#                         if 'formatted_address' in place:
#                             address = place['formatted_address']
#                             # Extract city and state from address
#                             parts = address.split(', ')
#                             if len(parts) >= 2:
#                                 result['city'] = parts[-3] if len(parts) > 2 else parts[0]
#                                 result['state'] = parts[-2] if len(parts) > 1 else ''
                                
#         except Exception as e:
#             logger.warning(f"Google Maps geocoding failed: {e}")

#     async def scrape_location_sites(self, phone_number: str, result: Dict):
#         """Scrape multiple location sites"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         sites = [
#             f'https://www.truecaller.com/search/in/{clean_number}',
#             f'https://www.justdial.com/search/sp:{clean_number}',
#             f'https://www.sulekha.com/search/{clean_number}',
#             f'https://www.indiamart.com/search.mp?ss={clean_number}',
#             f'https://www.olx.in/search?q={clean_number}'
#         ]
        
#         for site in sites:
#             try:
#                 headers = {'User-Agent': random.choice(self.user_agents)}
#                 response = self.session.get(site, headers=headers, timeout=15, verify=False)
                
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
                    
#                     # Look for location indicators
#                     location_patterns = [
#                         r'([A-Z][a-z]+),\s*([A-Z][a-z]+)',  # City, State
#                         r'Location[:\s]+([^,\n]+),?\s*([^,\n]+)',
#                         r'Address[:\s]+([^,\n]+),?\s*([^,\n]+)'
#                     ]
                    
#                     text = soup.get_text()
#                     for pattern in location_patterns:
#                         matches = re.findall(pattern, text)
#                         if matches:
#                             city, state = matches[0]
#                             if not result.get('city') and len(city.strip()) > 2:
#                                 result['city'] = city.strip()
#                             if not result.get('state') and len(state.strip()) > 2:
#                                 result['state'] = state.strip()
#                             break
                    
#                     if result.get('city'):
#                         break
                
#                 await asyncio.sleep(random.uniform(1, 3))
#             except Exception as e:
#                 logger.warning(f"Location site scraping failed for {site}: {e}")

#     async def social_media_location_extraction(self, phone_number: str, result: Dict):
#         """Extract location from social media profiles"""
#         try:
#             # Search for social media profiles with location
#             search_queries = [
#                 f'"{phone_number}" location india',
#                 f'"{phone_number}" city state',
#                 f'"{phone_number}" address contact'
#             ]
            
#             for query in search_queries:
#                 try:
#                     # Use multiple search engines
#                     search_results = await self.multi_search_engine_query(query, 5)
                    
#                     for url in search_results:
#                         if any(platform in url.lower() for platform in ['facebook', 'instagram', 'linkedin', 'twitter']):
#                             await self.extract_location_from_social_url(url, result)
#                             if result.get('city'):
#                                 return
                    
#                     await asyncio.sleep(random.uniform(2, 3))
#                 except Exception as e:
#                     logger.warning(f"Social media location search failed: {e}")
                    
#         except Exception as e:
#             logger.warning(f"Social media location extraction failed: {e}")

#     async def multi_search_engine_query(self, query: str, num_results: int) -> List[str]:
#         """Query multiple search engines"""
#         results = []
        
#         # Try different search engines
#         search_engines = [
#             f'https://www.google.com/search?q={quote(query)}',
#             f'https://www.bing.com/search?q={quote(query)}',
#             f'https://search.yahoo.com/search?p={quote(query)}',
#             f'https://duckduckgo.com/?q={quote(query)}'
#         ]   
        
#         for engine_url in search_engines:
#             try:
#                 headers = {'User-Agent': random.choice(self.user_agents)}
#                 response = self.session.get(engine_url, headers=headers, timeout=15, verify=False)
                
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
#                     links = soup.find_all('a', href=True)
                    
#                     for link in links:
#                         href = link['href']
#                         if href.startswith('http') and not any(se in href for se in ['google.com', 'bing.com', 'yahoo.com']):
#                             results.append(href)
#                             if len(results) >= num_results:
#                                 return results
                
#                 await asyncio.sleep(random.uniform(1, 2))
#             except Exception as e:
#                 logger.warning(f"Search engine query failed: {e}")
        
#         return results

#     async def extract_location_from_social_url(self, url: str, result: Dict):
#         """Extract location from social media URL"""
#         try:
#             headers = {'User-Agent': random.choice(self.user_agents)}
#             response = self.session.get(url, headers=headers, timeout=15, verify=False)
            
#             if response.status_code == 200:
#                 soup = BeautifulSoup(response.content, 'html.parser')
                
#                 # Look for location in meta tags
#                 location_selectors = [
#                     'meta[property="og:location"]',
#                     'meta[name="location"]',
#                     '[class*="location"]',
#                     '[class*="address"]',
#                     '[data-location]'
#                 ]
                
#                 for selector in location_selectors:
#                     elem = soup.select_one(selector)
#                     if elem:
#                         location_text = elem.get('content') or elem.get_text(strip=True)
#                         if location_text:
#                             # Parse location
#                             if ',' in location_text:
#                                 parts = location_text.split(',')
#                                 if not result.get('city'):
#                                     result['city'] = parts[0].strip()
#                                 if not result.get('state') and len(parts) > 1:
#                                     result['state'] = parts[1].strip()
#                             break
                            
#         except Exception as e:
#             logger.warning(f"Social media location extraction failed for {url}: {e}")

#     async def enhanced_social_media_search(self, phone_number: str) -> Dict[str, Any]:
#         """5 fallback methods for social media search"""
#         result = {
#             "instagram_url": None, "twitter_url": None, "facebook_url": None,
#             "linkedin_url": None, "tiktok_url": None, "snapchat_url": None, "youtube_url": None
#         }
        
#         # Method 1: Direct platform API searches
#         await self.direct_platform_api_search(phone_number, result)
        
#         # Method 2: Google dork searches with advanced operators
#         await self.advanced_google_dork_search(phone_number, result)
        
#         # Method 3: Social media aggregator sites
#         await self.social_aggregator_search(phone_number, result)
        
#         # Method 4: Reverse username search
#         await self.reverse_username_search(phone_number, result)
        
#         # Method 5: Deep web and cached page search
#         await self.deep_web_cached_search(phone_number, result)
        
#         return result

#     async def direct_platform_api_search(self, phone_number: str, result: Dict):
#         """Direct API searches on social platforms"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         # Instagram search
#         try:
#             instagram_urls = [
#                 f'https://www.instagram.com/web/search/topsearch/?query={clean_number}',
#                 f'https://www.instagram.com/explore/tags/{clean_number}/',
#                 f'https://www.instagram.com/{clean_number}/'
#             ]
            
#             for url in instagram_urls:
#                 headers = {'User-Agent': random.choice(self.user_agents)}
#                 response = self.session.get(url, headers=headers, timeout=15, verify=False)
#                 if response.status_code == 200 and 'instagram.com' in response.url:
#                     result['instagram_url'] = response.url
#                     break
#                 await asyncio.sleep(1)
#         except Exception as e:
#             logger.warning(f"Instagram API search failed: {e}")
        
#         # Facebook search
#         try:
#             facebook_urls = [
#                 f'https://www.facebook.com/search/people/?q={clean_number}',
#                 f'https://www.facebook.com/public/{clean_number}',
#                 f'https://m.facebook.com/search/?q={clean_number}'
#             ]
            
#             for url in facebook_urls:
#                 headers = {'User-Agent': random.choice(self.user_agents)}
#                 response = self.session.get(url, headers=headers, timeout=15, verify=False)
#                 if response.status_code == 200 and 'facebook.com' in response.url:
#                     result['facebook_url'] = response.url
#                     break
#                 await asyncio.sleep(1)
#         except Exception as e:
#             logger.warning(f"Facebook API search failed: {e}")

#     async def advanced_google_dork_search(self, phone_number: str, result: Dict):
#         """Advanced Google dork searches"""
#         platforms = {
#             'instagram': ['instagram.com', 'insta'],
#             'facebook': ['facebook.com', 'fb.com'],
#             'twitter': ['twitter.com', 'x.com'],
#             'linkedin': ['linkedin.com'],
#             'tiktok': ['tiktok.com'],
#             'youtube': ['youtube.com', 'youtu.be']
#         }
        
#         for platform, domains in platforms.items():
#             # Advanced search operators
#             search_queries = [
#                 f'"{phone_number}" site:{domains[0]}',
#                 f'"{phone_number}" inurl:{domains[0]}',
#                 f'"{phone_number}" {platform} profile',
#                 f'"{phone_number}" contact {platform}',
#                 f'intitle:"{phone_number}" site:{domains[0]}'
#             ]
            
#             for query in search_queries:
#                 try:
#                     search_results = await self.multi_search_engine_query(query, 3)
#                     for url in search_results:
#                         if any(domain in url.lower() for domain in domains):
#                             result[f'{platform}_url'] = url
#                             break
                    
#                     if result.get(f'{platform}_url'):
#                         break
                    
#                     await asyncio.sleep(random.uniform(1, 2))
#                 except Exception as e:
#                     logger.warning(f"Google dork search failed for {platform}: {e}")

#     async def social_aggregator_search(self, phone_number: str, result: Dict):
#         """Search social media aggregator sites"""
#         aggregator_sites = [
#             f'https://pipl.com/search/?q={phone_number}',
#             f'https://www.spokeo.com/search?q={phone_number}',
#             f'https://www.whitepages.com/phone/1-{phone_number.replace("+", "").replace("-", "")}',
#             f'https://www.truepeoplesearch.com/results?phoneno={phone_number}',
#             f'https://www.fastpeoplesearch.com/phone/{phone_number.replace("+", "").replace("-", "")}'
#         ]
        
#         for site in aggregator_sites:
#             try:
#                 headers = {'User-Agent': random.choice(self.user_agents)}
#                 response = self.session.get(site, headers=headers, timeout=15, verify=False)
                
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
                    
#                     # Look for social media links
#                     social_links = soup.find_all('a', href=True)
#                     for link in social_links:
#                         href = link['href'].lower()
#                         if 'instagram.com' in href and not result.get('instagram_url'):
#                             result['instagram_url'] = link['href']
#                         elif 'facebook.com' in href and not result.get('facebook_url'):
#                             result['facebook_url'] = link['href']
#                         elif 'twitter.com' in href or 'x.com' in href and not result.get('twitter_url'):
#                             result['twitter_url'] = link['href']
#                         elif 'linkedin.com' in href and not result.get('linkedin_url'):
#                             result['linkedin_url'] = link['href']
                
#                 await asyncio.sleep(random.uniform(2, 3))
#             except Exception as e:
#                 logger.warning(f"Social aggregator search failed for {site}: {e}")

#     async def reverse_username_search(self, phone_number: str, result: Dict):
#         """Reverse username search using phone number"""
#         try:
#             # Generate possible usernames from phone number
#             clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
#             possible_usernames = [
#                 clean_number,
#                 clean_number[-10:],  # Last 10 digits
#                 clean_number[-8:],   # Last 8 digits
#                 f"user{clean_number[-6:]}",
#                 f"{clean_number[:3]}{clean_number[-4:]}"
#             ]
            
#             platforms = ['instagram.com', 'twitter.com', 'facebook.com', 'tiktok.com']
            
#             for username in possible_usernames:
#                 for platform in platforms:
#                     try:
#                         url = f'https://{platform}/{username}'
#                         headers = {'User-Agent': random.choice(self.user_agents)}
#                         response = self.session.head(url, headers=headers, timeout=10, verify=False)
                        
#                         if response.status_code == 200:
#                             platform_key = platform.split('.')[0]
#                             if platform_key == 'twitter':
#                                 platform_key = 'twitter'
#                             result[f'{platform_key}_url'] = url
                        
#                         await asyncio.sleep(0.5)
#                     except Exception as e:
#                         continue
                        
#         except Exception as e:
#             logger.warning(f"Reverse username search failed: {e}")

#     async def deep_web_cached_search(self, phone_number: str, result: Dict):
#         """Search cached pages and deep web"""
#         try:
#             # Wayback Machine search
#             wayback_url = f'http://web.archive.org/cdx/search/cdx?url=*{phone_number}*&output=json&limit=50'
#             response = self.session.get(wayback_url, timeout=20, verify=False)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 if data and len(data) > 1:
#                     for row in data[1:]:  # Skip header
#                         if len(row) >= 3:
#                             original_url = row[2]
#                             if any(platform in original_url.lower() for platform in ['instagram', 'facebook', 'twitter']):
#                                 platform = 'instagram' if 'instagram' in original_url else 'facebook' if 'facebook' in original_url else 'twitter'
#                                 if not result.get(f'{platform}_url'):
#                                     result[f'{platform}_url'] = original_url
            
#             # Google Cache search
#             cache_queries = [
#                 f'cache:{phone_number} site:instagram.com',
#                 f'cache:{phone_number} site:facebook.com',
#                 f'cache:{phone_number} site:twitter.com'
#             ]
            
#             for query in cache_queries:
#                 search_results = await self.multi_search_engine_query(query, 2)
#                 for url in search_results:
#                     if 'webcache.googleusercontent.com' in url:
#                         # Extract original URL from cache URL
#                         if 'instagram.com' in url and not result.get('instagram_url'):
#                             result['instagram_url'] = url
#                         elif 'facebook.com' in url and not result.get('facebook_url'):
#                             result['facebook_url'] = url
#                         elif 'twitter.com' in url and not result.get('twitter_url'):
#                             result['twitter_url'] = url
                
#                 await asyncio.sleep(2)
                
#         except Exception as e:
#             logger.warning(f"Deep web cached search failed: {e}")

#     async def enhanced_owner_spam_detection(self, phone_number: str) -> Dict[str, Any]:
#         """5 fallback methods for owner and spam detection"""
#         result = {
#             "caller_name": None, "spam_score": 0.0, "spam_tags": [],
#             "caller_type": None, "business_name": None, "reputation_score": None, "report_count": 0
#         }
        
#         # Method 1: Truecaller with multiple approaches
#         await self.enhanced_truecaller_scraping(phone_number, result)
        
#         # Method 2: Multiple caller ID databases
#         await self.comprehensive_caller_id_scraping(phone_number, result)
        
#         # Method 3: Business directory searches
#         await self.business_directory_name_search(phone_number, result)
        
#         # Method 4: Social media name extraction
#         await self.social_media_name_extraction(phone_number, result)
        
#         # Method 5: Government and official database search
#         await self.official_database_search(phone_number, result)
        
#         return result

#     async def enhanced_truecaller_scraping(self, phone_number: str, result: Dict):
#         """Enhanced Truecaller scraping with multiple methods"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         # Multiple Truecaller URLs and approaches
#         truecaller_approaches = [
#             # Direct search URLs
#             f'https://www.truecaller.com/search/in/{clean_number}',
#             f'https://www.truecaller.com/search/global/{clean_number}',
#             f'https://www.truecaller.com/phone/{clean_number}',
            
#             # Mobile URLs
#             f'https://m.truecaller.com/search/{clean_number}',
#             f'https://m.truecaller.com/in/{clean_number}',
#         ]
        
#         for url in truecaller_approaches:
#             try:
#                 # Try different user agents
#                 user_agents = [
#                     'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
#                     'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
#                     'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
#                 ]
                
#                 for ua in user_agents:
#                     headers = {
#                         'User-Agent': ua,
#                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#                         'Accept-Language': 'en-US,en;q=0.5',
#                         'Accept-Encoding': 'gzip, deflate',
#                         'Connection': 'keep-alive',
#                         'Upgrade-Insecure-Requests': '1',
#                     }
                    
#                     response = self.session.get(url, headers=headers, timeout=20, verify=False)
                    
#                     if response.status_code == 200:
#                         soup = BeautifulSoup(response.content, 'html.parser')
                        
#                         # Multiple selectors for name
#                         name_selectors = [
#                             'h1[data-test-id="search-result-name"]',
#                             '.search-result-name',
#                             '.caller-name',
#                             'h1.name',
#                             '[class*="name"]',
#                             '[data-name]',
#                             'title'
#                         ]
                        
#                         for selector in name_selectors:
#                             name_elem = soup.select_one(selector)
#                             if name_elem:
#                                 name = name_elem.get_text(strip=True)
#                                 if name and len(name) > 2 and name.lower() not in ['unknown', 'private', 'hidden']:
#                                     result['caller_name'] = name
#                                     logger.info(f"Found caller name from Truecaller: {name}")
#                                     break
                        
#                         # Look for spam indicators
#                         spam_keywords = ['spam', 'scam', 'fraud', 'telemarketer', 'robocall', 'unwanted']
#                         text_content = soup.get_text().lower()
                        
#                         spam_count = sum(1 for keyword in spam_keywords if keyword in text_content)
#                         if spam_count > 0:
#                             result['spam_score'] = min(spam_count * 0.2, 1.0)
#                             result['spam_tags'].extend([kw for kw in spam_keywords if kw in text_content])
                        
#                         if result.get('caller_name'):
#                             return
                    
#                     await asyncio.sleep(random.uniform(1, 2))
                    
#             except Exception as e:
#                 logger.warning(f"Truecaller scraping failed for {url}: {e}")
#                 continue

#     async def comprehensive_caller_id_scraping(self, phone_number: str, result: Dict):
#         """Scrape multiple caller ID databases"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         caller_id_sites = [
#             # Indian specific sites
#             f'https://www.bharat-calls.com/{clean_number}',
#             f'https://www.showcaller.com/phone-number/{clean_number}',
#             f'https://www.findandtrace.com/trace-mobile-number-location/{clean_number}',
#             f'https://www.mobilenumbertrackeronline.com/track/{clean_number}',
            
#             # International sites
#             f'https://www.whocalld.com/+{clean_number}',
#             f'https://www.shouldianswer.com/phone-number/{clean_number}',
#             f'https://www.callercenter.com/number/{clean_number}',
#             f'https://www.spamcalls.net/en/number/{clean_number}',
#             f'https://www.unknownphone.com/phone-number/{clean_number}',
#             f'https://www.reversephonelookup.com/number/{clean_number}',
#         ]
        
#         for site in caller_id_sites:
#             try:
#                 headers = {'User-Agent': random.choice(self.user_agents)}
#                 response = self.session.get(site, headers=headers, timeout=15, verify=False)
                
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
                    
#                     # Look for caller name patterns
#                     name_patterns = [
#                         r'(?:Name|Caller|Owner)[:\s]+([A-Za-z\s]{3,30})',
#                         r'(?:Belongs to|Registered to)[:\s]+([A-Za-z\s]{3,30})',
#                         r'<h[1-6][^>]*>([A-Za-z\s]{3,30})</h[1-6]>',
#                     ]
                    
#                     text = soup.get_text()
#                     for pattern in name_patterns:
#                         matches = re.findall(pattern, text, re.I)
#                         if matches:
#                             name = matches[0].strip()
#                             if name and len(name) > 2 and not result.get('caller_name'):
#                                 result['caller_name'] = name
#                                 logger.info(f"Found caller name from {site}: {name}")
#                                 break
                    
#                     # Look for business indicators
#                     business_keywords = ['company', 'business', 'shop', 'store', 'service', 'ltd', 'pvt', 'inc']
#                     if any(keyword in text.lower() for keyword in business_keywords):
#                         result['caller_type'] = 'business'
                    
#                     if result.get('caller_name'):
#                         break
                
#                 await asyncio.sleep(random.uniform(1, 3))
#             except Exception as e:
#                 logger.warning(f"Caller ID scraping failed for {site}: {e}")

#     async def business_directory_name_search(self, phone_number: str, result: Dict):
#         """Search business directories for name"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         business_directories = [
#             # Indian directories
#             f'https://www.justdial.com/search/sp:{clean_number}',
#             f'https://www.sulekha.com/search/{clean_number}',
#             f'https://www.indiamart.com/search.mp?ss={clean_number}',
#             f'https://www.tradeindia.com/search/{clean_number}',
#             f'https://www.yellowpages.co.in/search/{clean_number}',
            
#             # International directories
#             f'https://www.yellowpages.com/search?search_terms={clean_number}',
#             f'https://www.whitepages.com/phone/1-{clean_number}',
#             f'https://www.yelp.com/search?find_desc={clean_number}',
#             f'https://www.bbb.org/search?query={clean_number}',
#         ]
        
#         for directory in business_directories:
#             try:
#                 headers = {'User-Agent': random.choice(self.user_agents)}
#                 response = self.session.get(directory, headers=headers, timeout=15, verify=False)
                
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
                    
#                     # Look for business names
#                     business_selectors = [
#                         'h1', 'h2', 'h3',
#                         '.business-name',
#                         '.company-name',
#                         '[class*="title"]',
#                         '[class*="name"]'
#                     ]
                    
#                     for selector in business_selectors:
#                         elements = soup.select(selector)
#                         for elem in elements:
#                             text = elem.get_text(strip=True)
#                             if text and len(text) > 3 and len(text) < 50:
#                                 # Check if it looks like a business name
#                                 if any(word in text.lower() for word in ['shop', 'store', 'company', 'service', 'restaurant', 'hotel']):
#                                     result['business_name'] = text
#                                     result['caller_type'] = 'business'
#                                     if not result.get('caller_name'):
#                                         result['caller_name'] = text
#                                     logger.info(f"Found business name: {text}")
#                                     return
                
#                 await asyncio.sleep(random.uniform(2, 3))
#             except Exception as e:
#                 logger.warning(f"Business directory search failed for {directory}: {e}")

#     async def social_media_name_extraction(self, phone_number: str, result: Dict):
#         """Extract names from social media profiles"""
#         try:
#             # Search for social media profiles
#             search_queries = [
#                 f'"{phone_number}" name profile',
#                 f'"{phone_number}" contact person',
#                 f'"{phone_number}" owner name'
#             ]
            
#             for query in search_queries:
#                 search_results = await self.multi_search_engine_query(query, 5)
                
#                 for url in search_results:
#                     if any(platform in url.lower() for platform in ['facebook', 'instagram', 'linkedin', 'twitter']):
#                         try:
#                             headers = {'User-Agent': random.choice(self.user_agents)}
#                             response = self.session.get(url, headers=headers, timeout=15, verify=False)
                            
#                             if response.status_code == 200:
#                                 soup = BeautifulSoup(response.content, 'html.parser')
                                
#                                 # Look for names in meta tags and titles
#                                 name_sources = [
#                                     soup.find('meta', property='og:title'),
#                                     soup.find('meta', name='twitter:title'),
#                                     soup.find('title'),
#                                     soup.find('h1'),
#                                 ]
                                
#                                 for source in name_sources:
#                                     if source:
#                                         name = source.get('content') or source.get_text(strip=True)
#                                         if name and len(name) > 2 and len(name) < 50:
#                                             # Clean up the name
#                                             name = re.sub(r'\s*\|\s*.*$', '', name)  # Remove site name
#                                             name = re.sub(r'\s*-\s*.*$', '', name)   # Remove taglines
#                                             if name and not result.get('caller_name'):
#                                                 result['caller_name'] = name.strip()
#                                                 logger.info(f"Found name from social media: {name}")
#                                                 return
#                         except Exception as e:
#                             continue
                
#                 await asyncio.sleep(random.uniform(2, 3))
                
#         except Exception as e:
#             logger.warning(f"Social media name extraction failed: {e}")

#     async def official_database_search(self, phone_number: str, result: Dict):
#         """Search official and government databases"""
#         clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
#         # Indian government and official sites
#         official_sites = [
#             f'https://www.trai.gov.in/search?query={clean_number}',
#             f'https://www.dot.gov.in/search/{clean_number}',
#             f'https://www.mca.gov.in/mcafoportal/companyLLPMasterData.do?companyName={clean_number}',
#         ]
        
#         for site in official_sites:
#             try:
#                 headers = {'User-Agent': random.choice(self.user_agents)}
#                 response = self.session.get(site, headers=headers, timeout=20, verify=False)
                
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.content, 'html.parser')
#                     text = soup.get_text()
                    
#                     # Look for official registrations
#                     if 'registered' in text.lower() or 'license' in text.lower():
#                         # Extract potential names
#                         name_patterns = [
#                             r'(?:Registered to|Licensed to|Owner)[:\s]+([A-Za-z\s]{3,50})',
#                             r'(?:Company|Business)[:\s]+([A-Za-z\s]{3,50})',
#                         ]
                        
#                         for pattern in name_patterns:
#                             matches = re.findall(pattern, text, re.I)
#                             if matches:
#                                 name = matches[0].strip()
#                                 if name and not result.get('caller_name'):
#                                     result['caller_name'] = name
#                                     result['caller_type'] = 'registered_business'
#                                     logger.info(f"Found official registration: {name}")
#                                     return
                
#                 await asyncio.sleep(random.uniform(3, 5))
#             except Exception as e:
#                 logger.warning(f"Official database search failed for {site}: {e}")



# //new above best 



import asyncio
import json
import logging
import os
import re
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import quote, urljoin
import random
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import httpx
import ssl
import urllib3

logger = logging.getLogger(__name__)

class EnhancedPhoneScrapers:
    def __init__(self, session, api_keys):
        self.session = session
        self.api_keys = api_keys
        
        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Enhanced user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]

    async def enhanced_geolocation_search(self, phone_number: str) -> Dict[str, Any]:
        """5 fallback methods for geolocation"""
        result = {"city": None, "state": None, "timezone": None, "latitude": None, "longitude": None}
        
        # Method 1: Area code database lookup
        await self.area_code_database_lookup(phone_number, result)
        
        # Method 2: Carrier location databases
        await self.carrier_location_lookup(phone_number, result)
        
        # Method 3: Google Maps API geocoding
        await self.google_maps_geocoding(phone_number, result)
        
        # Method 4: Multiple location scraping sites
        await self.scrape_location_sites(phone_number, result)
        
        # Method 5: Social media location extraction
        await self.social_media_location_extraction(phone_number, result)
        
        return result

    async def area_code_database_lookup(self, phone_number: str, result: Dict):
        """Enhanced area code database with Indian numbers"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Indian area codes (first 4 digits after country code)
        if clean_number.startswith('91') and len(clean_number) >= 6:
            area_code = clean_number[2:6]  # Get area code
            
            # Enhanced Indian area code mapping
            indian_area_codes = {
                # Rajasthan
                '8744': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '9414': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '9829': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '7597': {'city': 'Jaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '8290': {'city': 'Udaipur', 'state': 'Rajasthan', 'region': 'North India'},
                '9928': {'city': 'Jodhpur', 'state': 'Rajasthan', 'region': 'North India'},
                
                # Delhi
                '9811': {'city': 'New Delhi', 'state': 'Delhi', 'region': 'North India'},
                '9999': {'city': 'New Delhi', 'state': 'Delhi', 'region': 'North India'},
                '8447': {'city': 'New Delhi', 'state': 'Delhi', 'region': 'North India'},
                
                # Mumbai
                '9820': {'city': 'Mumbai', 'state': 'Maharashtra', 'region': 'West India'},
                '9821': {'city': 'Mumbai', 'state': 'Maharashtra', 'region': 'West India'},
                '8080': {'city': 'Mumbai', 'state': 'Maharashtra', 'region': 'West India'},
                
                # Bangalore
                '9845': {'city': 'Bangalore', 'state': 'Karnataka', 'region': 'South India'},
                '9844': {'city': 'Bangalore', 'state': 'Karnataka', 'region': 'South India'},
                '8050': {'city': 'Bangalore', 'state': 'Karnataka', 'region': 'South India'},
                
                # Chennai
                '9840': {'city': 'Chennai', 'state': 'Tamil Nadu', 'region': 'South India'},
                '9841': {'city': 'Chennai', 'state': 'Tamil Nadu', 'region': 'South India'},
                '8939': {'city': 'Chennai', 'state': 'Tamil Nadu', 'region': 'South India'},
                
                # Hyderabad
                '9849': {'city': 'Hyderabad', 'state': 'Telangana', 'region': 'South India'},
                '9866': {'city': 'Hyderabad', 'state': 'Telangana', 'region': 'South India'},
                '8179': {'city': 'Hyderabad', 'state': 'Telangana', 'region': 'South India'},
                
                # Kolkata
                '9830': {'city': 'Kolkata', 'state': 'West Bengal', 'region': 'East India'},
                '9831': {'city': 'Kolkata', 'state': 'West Bengal', 'region': 'East India'},
                '8017': {'city': 'Kolkata', 'state': 'West Bengal', 'region': 'East India'},
                
                # Pune
                '9822': {'city': 'Pune', 'state': 'Maharashtra', 'region': 'West India'},
                '9823': {'city': 'Pune', 'state': 'Maharashtra', 'region': 'West India'},
                '8888': {'city': 'Pune', 'state': 'Maharashtra', 'region': 'West India'},
            }
            
            if area_code in indian_area_codes:
                location_info = indian_area_codes[area_code]
                result.update(location_info)
                result['timezone'] = 'Asia/Calcutta'
                logger.info(f"Found location from area code {area_code}: {location_info}")

    async def carrier_location_lookup(self, phone_number: str, result: Dict):
        """Lookup location from carrier databases"""
        try:
            # Multiple carrier lookup sites
            sites = [
                f'https://www.hlrlookup.com/lookup/{phone_number}',
                f'https://www.carrierlookup.com/index.php/lookup/carrier?msisdn={phone_number.replace("+", "")}',
                f'https://www.freecarrierlookup.com/lookup.php?number={phone_number.replace("+", "")}',
                f'https://www.phonevalidator.com/index.php/api/v1/validate?phone={phone_number}',
                f'https://numverify.com/php_helper_scripts/phone_api.php?secret_key=demo&number={phone_number}'
            ]
            
            for site in sites:
                try:
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    response = self.session.get(site, headers=headers, timeout=15, verify=False)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text = soup.get_text().lower()
                        
                        # Look for Indian cities
                        indian_cities = ['jaipur', 'delhi', 'mumbai', 'bangalore', 'chennai', 'hyderabad', 'kolkata', 'pune', 'ahmedabad', 'surat']
                        for city in indian_cities:
                            if city in text and not result.get('city'):
                                result['city'] = city.title()
                                
                                # Map city to state
                                city_state_map = {
                                    'jaipur': 'Rajasthan', 'delhi': 'Delhi', 'mumbai': 'Maharashtra',
                                    'bangalore': 'Karnataka', 'chennai': 'Tamil Nadu', 'hyderabad': 'Telangana',
                                    'kolkata': 'West Bengal', 'pune': 'Maharashtra', 'ahmedabad': 'Gujarat', 'surat': 'Gujarat'
                                }
                                result['state'] = city_state_map.get(city, '')
                                break
                        
                        if result.get('city'):
                            break
                    
                    await asyncio.sleep(random.uniform(1, 2))
                except Exception as e:
                    logger.warning(f"Carrier location lookup failed for {site}: {e}")
                    
        except Exception as e:
            logger.warning(f"Carrier location lookup failed: {e}")

    async def google_maps_geocoding(self, phone_number: str, result: Dict):
        """Use Google Maps API for geocoding"""
        try:
            if self.api_keys.get('google_api_key'):
                # Search for businesses with this phone number
                url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                params = {
                    'query': phone_number,
                    'key': self.api_keys['google_api_key']
                }
                
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        place = data['results'][0]
                        if 'geometry' in place:
                            location = place['geometry']['location']
                            result['latitude'] = location.get('lat')
                            result['longitude'] = location.get('lng')
                        
                        if 'formatted_address' in place:
                            address = place['formatted_address']
                            # Extract city and state from address
                            parts = address.split(', ')
                            if len(parts) >= 2:
                                result['city'] = parts[-3] if len(parts) > 2 else parts[0]
                                result['state'] = parts[-2] if len(parts) > 1 else ''
                                
        except Exception as e:
            logger.warning(f"Google Maps geocoding failed: {e}")

    async def scrape_location_sites(self, phone_number: str, result: Dict):
        """Scrape multiple location sites"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        sites = [
            f'https://www.truecaller.com/search/in/{clean_number}',
            f'https://www.justdial.com/search/sp:{clean_number}',
            f'https://www.sulekha.com/search/{clean_number}',
            f'https://www.indiamart.com/search.mp?ss={clean_number}',
            f'https://www.olx.in/search?q={clean_number}'
        ]
        
        for site in sites:
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = self.session.get(site, headers=headers, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for location indicators
                    location_patterns = [
                        r'([A-Z][a-z]+),\s*([A-Z][a-z]+)',  # City, State
                        r'Location[:\s]+([^,\n]+),?\s*([^,\n]+)',
                        r'Address[:\s]+([^,\n]+),?\s*([^,\n]+)'
                    ]
                    
                    text = soup.get_text()
                    for pattern in location_patterns:
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
                
                await asyncio.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.warning(f"Location site scraping failed for {site}: {e}")

    async def social_media_location_extraction(self, phone_number: str, result: Dict):
        """Extract location from social media profiles"""
        try:
            # Search for social media profiles with location
            search_queries = [
                f'"{phone_number}" location india',
                f'"{phone_number}" city state',
                f'"{phone_number}" address contact'
            ]
            
            for query in search_queries:
                try:
                    # Use multiple search engines
                    search_results = await self.multi_search_engine_query(query, 5)
                    
                    for url in search_results:
                        if any(platform in url.lower() for platform in ['facebook', 'instagram', 'linkedin', 'twitter']):
                            await self.extract_location_from_social_url(url, result)
                            if result.get('city'):
                                return
                    
                    await asyncio.sleep(random.uniform(2, 3))
                except Exception as e:
                    logger.warning(f"Social media location search failed: {e}")
                    
        except Exception as e:
            logger.warning(f"Social media location extraction failed: {e}")

    async def multi_search_engine_query(self, query: str, num_results: int) -> List[str]:
        """Query multiple search engines"""
        results = []
        
        # Try different search engines
        search_engines = [
            f'https://www.google.com/search?q={quote(query)}',
            f'https://www.bing.com/search?q={quote(query)}',
            f'https://search.yahoo.com/search?p={quote(query)}',
            f'https://duckduckgo.com/?q={quote(query)}'
        ]
        
        for engine_url in search_engines:
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = self.session.get(engine_url, headers=headers, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        href = link['href']
                        if href.startswith('http') and not any(se in href for se in ['google.com', 'bing.com', 'yahoo.com']):
                            results.append(href)
                            if len(results) >= num_results:
                                return results
                
                await asyncio.sleep(random.uniform(1, 2))
            except Exception as e:
                logger.warning(f"Search engine query failed: {e}")
        
        return results

    async def extract_location_from_social_url(self, url: str, result: Dict):
        """Extract location from social media URL"""
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            response = self.session.get(url, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for location in meta tags
                location_selectors = [
                    'meta[property="og:location"]',
                    'meta[name="location"]',
                    '[class*="location"]',
                    '[class*="address"]',
                    '[data-location]'
                ]
                
                for selector in location_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        location_text = elem.get('content') or elem.get_text(strip=True)
                        if location_text:
                            # Parse location
                            if ',' in location_text:
                                parts = location_text.split(',')
                                if not result.get('city'):
                                    result['city'] = parts[0].strip()
                                if not result.get('state') and len(parts) > 1:
                                    result['state'] = parts[1].strip()
                            break
                            
        except Exception as e:
            logger.warning(f"Social media location extraction failed for {url}: {e}")

    async def enhanced_social_media_search(self, phone_number: str) -> Dict[str, Any]:
        """5 fallback methods for social media search"""
        result = {
            "instagram_url": None, "twitter_url": None, "facebook_url": None,
            "linkedin_url": None, "tiktok_url": None, "snapchat_url": None, "youtube_url": None
        }
        
        # Method 1: Direct platform API searches
        await self.direct_platform_api_search(phone_number, result)
        
        # Method 2: Google dork searches with advanced operators
        await self.advanced_google_dork_search(phone_number, result)
        
        # Method 3: Social media aggregator sites
        await self.social_aggregator_search(phone_number, result)
        
        # Method 4: Reverse username search
        await self.reverse_username_search(phone_number, result)
        
        # Method 5: Deep web and cached page search
        await self.deep_web_cached_search(phone_number, result)
        
        return result

    async def direct_platform_api_search(self, phone_number: str, result: Dict):
        """Direct API searches on social platforms"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Instagram search
        try:
            instagram_urls = [
                f'https://www.instagram.com/web/search/topsearch/?query={clean_number}',
                f'https://www.instagram.com/explore/tags/{clean_number}/',
                f'https://www.instagram.com/{clean_number}/'
            ]
            
            for url in instagram_urls:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = self.session.get(url, headers=headers, timeout=15, verify=False)
                if response.status_code == 200 and 'instagram.com' in response.url:
                    result['instagram_url'] = response.url
                    break
                await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"Instagram API search failed: {e}")
        
        # Facebook search
        try:
            facebook_urls = [
                f'https://www.facebook.com/search/people/?q={clean_number}',
                f'https://www.facebook.com/public/{clean_number}',
                f'https://m.facebook.com/search/?q={clean_number}'
            ]
            
            for url in facebook_urls:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = self.session.get(url, headers=headers, timeout=15, verify=False)
                if response.status_code == 200 and 'facebook.com' in response.url:
                    result['facebook_url'] = response.url
                    break
                await asyncio.sleep(1)
        except Exception as e:
            logger.warning(f"Facebook API search failed: {e}")

    async def advanced_google_dork_search(self, phone_number: str, result: Dict):
        """Advanced Google dork searches"""
        platforms = {
            'instagram': ['instagram.com', 'insta'],
            'facebook': ['facebook.com', 'fb.com'],
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'tiktok': ['tiktok.com'],
            'youtube': ['youtube.com', 'youtu.be']
        }
        
        for platform, domains in platforms.items():
            # Advanced search operators
            search_queries = [
                f'"{phone_number}" site:{domains[0]}',
                f'"{phone_number}" inurl:{domains[0]}',
                f'"{phone_number}" {platform} profile',
                f'"{phone_number}" contact {platform}',
                f'intitle:"{phone_number}" site:{domains[0]}'
            ]
            
            for query in search_queries:
                try:
                    search_results = await self.multi_search_engine_query(query, 3)
                    for url in search_results:
                        if any(domain in url.lower() for domain in domains):
                            result[f'{platform}_url'] = url
                            break
                    
                    if result.get(f'{platform}_url'):
                        break
                    
                    await asyncio.sleep(random.uniform(1, 2))
                except Exception as e:
                    logger.warning(f"Google dork search failed for {platform}: {e}")

    async def social_aggregator_search(self, phone_number: str, result: Dict):
        """Search social media aggregator sites"""
        aggregator_sites = [
            f'https://pipl.com/search/?q={phone_number}',
            f'https://www.spokeo.com/search?q={phone_number}',
            f'https://www.whitepages.com/phone/1-{phone_number.replace("+", "").replace("-", "")}',
            f'https://www.truepeoplesearch.com/results?phoneno={phone_number}',
            f'https://www.fastpeoplesearch.com/phone/{phone_number.replace("+", "").replace("-", "")}'
        ]
        
        for site in aggregator_sites:
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = self.session.get(site, headers=headers, timeout=15, verify=False)
                
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
                        elif 'twitter.com' in href or 'x.com' in href and not result.get('twitter_url'):
                            result['twitter_url'] = link['href']
                        elif 'linkedin.com' in href and not result.get('linkedin_url'):
                            result['linkedin_url'] = link['href']
                
                await asyncio.sleep(random.uniform(2, 3))
            except Exception as e:
                logger.warning(f"Social aggregator search failed for {site}: {e}")

    async def reverse_username_search(self, phone_number: str, result: Dict):
        """Reverse username search using phone number"""
        try:
            # Generate possible usernames from phone number
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            possible_usernames = [
                clean_number,
                clean_number[-10:],  # Last 10 digits
                clean_number[-8:],   # Last 8 digits
                f"user{clean_number[-6:]}",
                f"{clean_number[:3]}{clean_number[-4:]}"
            ]
            
            platforms = ['instagram.com', 'twitter.com', 'facebook.com', 'tiktok.com']
            
            for username in possible_usernames:
                for platform in platforms:
                    try:
                        url = f'https://{platform}/{username}'
                        headers = {'User-Agent': random.choice(self.user_agents)}
                        response = self.session.head(url, headers=headers, timeout=10, verify=False)
                        
                        if response.status_code == 200:
                            platform_key = platform.split('.')[0]
                            if platform_key == 'twitter':
                                platform_key = 'twitter'
                            result[f'{platform_key}_url'] = url
                        
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            logger.warning(f"Reverse username search failed: {e}")

    async def deep_web_cached_search(self, phone_number: str, result: Dict):
        """Search cached pages and deep web"""
        try:
            # Wayback Machine search
            wayback_url = f'http://web.archive.org/cdx/search/cdx?url=*{phone_number}*&output=json&limit=50'
            response = self.session.get(wayback_url, timeout=20, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 1:
                    for row in data[1:]:  # Skip header
                        if len(row) >= 3:
                            original_url = row[2]
                            if any(platform in original_url.lower() for platform in ['instagram', 'facebook', 'twitter']):
                                platform = 'instagram' if 'instagram' in original_url else 'facebook' if 'facebook' in original_url else 'twitter'
                                if not result.get(f'{platform}_url'):
                                    result[f'{platform}_url'] = original_url
            
            # Google Cache search
            cache_queries = [
                f'cache:{phone_number} site:instagram.com',
                f'cache:{phone_number} site:facebook.com',
                f'cache:{phone_number} site:twitter.com'
            ]
            
            for query in cache_queries:
                search_results = await self.multi_search_engine_query(query, 2)
                for url in search_results:
                    if 'webcache.googleusercontent.com' in url:
                        # Extract original URL from cache URL
                        if 'instagram.com' in url and not result.get('instagram_url'):
                            result['instagram_url'] = url
                        elif 'facebook.com' in url and not result.get('facebook_url'):
                            result['facebook_url'] = url
                        elif 'twitter.com' in url and not result.get('twitter_url'):
                            result['twitter_url'] = url
                
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.warning(f"Deep web cached search failed: {e}")

    async def enhanced_owner_spam_detection(self, phone_number: str) -> Dict[str, Any]:
        """5 fallback methods for owner and spam detection"""
        result = {
            "caller_name": None, "spam_score": 0.0, "spam_tags": [],
            "caller_type": None, "business_name": None, "reputation_score": None, "report_count": 0
        }
        
        # Method 1: Truecaller with multiple approaches
        await self.enhanced_truecaller_scraping(phone_number, result)
        
        # Method 2: Multiple caller ID databases
        await self.comprehensive_caller_id_scraping(phone_number, result)
        
        # Method 3: Business directory searches
        await self.business_directory_name_search(phone_number, result)
        
        # Method 4: Social media name extraction
        await self.social_media_name_extraction(phone_number, result)
        
        # Method 5: Government and official database search
        await self.official_database_search(phone_number, result)
        
        return result

    async def enhanced_truecaller_scraping(self, phone_number: str, result: Dict):
        """Enhanced Truecaller scraping with multiple methods"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Multiple Truecaller URLs and approaches
        truecaller_approaches = [
            # Direct search URLs
            f'https://www.truecaller.com/search/in/{clean_number}',
            f'https://www.truecaller.com/search/global/{clean_number}',
            f'https://www.truecaller.com/phone/{clean_number}',
            
            # Mobile URLs
            f'https://m.truecaller.com/search/{clean_number}',
            f'https://m.truecaller.com/in/{clean_number}',
        ]
        
        for url in truecaller_approaches:
            try:
                # Try different user agents
                user_agents = [
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                    'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
                    'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
                ]
                
                for ua in user_agents:
                    headers = {
                        'User-Agent': ua,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    
                    response = self.session.get(url, headers=headers, timeout=20, verify=False)
                    
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
                            'title'
                        ]
                        
                        for selector in name_selectors:
                            name_elem = soup.select_one(selector)
                            if name_elem:
                                name = name_elem.get_text(strip=True)
                                if name and len(name) > 2 and name.lower() not in ['unknown', 'private', 'hidden']:
                                    result['caller_name'] = name
                                    logger.info(f"Found caller name from Truecaller: {name}")
                                    break
                        
                        # Look for spam indicators
                        spam_keywords = ['spam', 'scam', 'fraud', 'telemarketer', 'robocall', 'unwanted']
                        text_content = soup.get_text().lower()
                        
                        spam_count = sum(1 for keyword in spam_keywords if keyword in text_content)
                        if spam_count > 0:
                            result['spam_score'] = min(spam_count * 0.2, 1.0)
                            result['spam_tags'].extend([kw for kw in spam_keywords if kw in text_content])
                        
                        if result.get('caller_name'):
                            return
                    
                    await asyncio.sleep(random.uniform(1, 2))
                    
            except Exception as e:
                logger.warning(f"Truecaller scraping failed for {url}: {e}")
                continue

    async def comprehensive_caller_id_scraping(self, phone_number: str, result: Dict):
        """Scrape multiple caller ID databases"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        caller_id_sites = [
            # Indian specific sites
            f'https://www.bharat-calls.com/{clean_number}',
            f'https://www.showcaller.com/phone-number/{clean_number}',
            f'https://www.findandtrace.com/trace-mobile-number-location/{clean_number}',
            f'https://www.mobilenumbertrackeronline.com/track/{clean_number}',
            
            # International sites
            f'https://www.whocalld.com/+{clean_number}',
            f'https://www.shouldianswer.com/phone-number/{clean_number}',
            f'https://www.callercenter.com/number/{clean_number}',
            f'https://www.spamcalls.net/en/number/{clean_number}',
            f'https://www.unknownphone.com/phone-number/{clean_number}',
            f'https://www.reversephonelookup.com/number/{clean_number}',
        ]
        
        for site in caller_id_sites:
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = self.session.get(site, headers=headers, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for caller name patterns
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
                                break
                    
                    # Look for business indicators
                    business_keywords = ['company', 'business', 'shop', 'store', 'service', 'ltd', 'pvt', 'inc']
                    if any(keyword in text.lower() for keyword in business_keywords):
                        result['caller_type'] = 'business'
                    
                    if result.get('caller_name'):
                        break
                
                await asyncio.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.warning(f"Caller ID scraping failed for {site}: {e}")

    async def business_directory_name_search(self, phone_number: str, result: Dict):
        """Search business directories for name"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        business_directories = [
            # Indian directories
            f'https://www.justdial.com/search/sp:{clean_number}',
            f'https://www.sulekha.com/search/{clean_number}',
            f'https://www.indiamart.com/search.mp?ss={clean_number}',
            f'https://www.tradeindia.com/search/{clean_number}',
            f'https://www.yellowpages.co.in/search/{clean_number}',
            
            # International directories
            f'https://www.yellowpages.com/search?search_terms={clean_number}',
            f'https://www.whitepages.com/phone/1-{clean_number}',
            f'https://www.yelp.com/search?find_desc={clean_number}',
            f'https://www.bbb.org/search?query={clean_number}',
        ]
        
        for directory in business_directories:
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = self.session.get(directory, headers=headers, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for business names
                    business_selectors = [
                        'h1', 'h2', 'h3',
                        '.business-name',
                        '.company-name',
                        '[class*="title"]',
                        '[class*="name"]'
                    ]
                    
                    for selector in business_selectors:
                        elements = soup.select(selector)
                        for elem in elements:
                            text = elem.get_text(strip=True)
                            if text and len(text) > 3 and len(text) < 50:
                                # Check if it looks like a business name
                                if any(word in text.lower() for word in ['shop', 'store', 'company', 'service', 'restaurant', 'hotel']):
                                    result['business_name'] = text
                                    result['caller_type'] = 'business'
                                    if not result.get('caller_name'):
                                        result['caller_name'] = text
                                    logger.info(f"Found business name: {text}")
                                    return
                
                await asyncio.sleep(random.uniform(2, 3))
            except Exception as e:
                logger.warning(f"Business directory search failed for {directory}: {e}")

    async def social_media_name_extraction(self, phone_number: str, result: Dict):
        """Extract names from social media profiles"""
        try:
            # Search for social media profiles
            search_queries = [
                f'"{phone_number}" name profile',
                f'"{phone_number}" contact person',
                f'"{phone_number}" owner name'
            ]
            
            for query in search_queries:
                search_results = await self.multi_search_engine_query(query, 5)
                
                for url in search_results:
                    if any(platform in url.lower() for platform in ['facebook', 'instagram', 'linkedin', 'twitter']):
                        try:
                            headers = {'User-Agent': random.choice(self.user_agents)}
                            response = self.session.get(url, headers=headers, timeout=15, verify=False)
                            
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                
                                # Look for names in meta tags and titles
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
                                            name = re.sub(r'\s*\|\s*.*$', '', name)  # Remove site name
                                            name = re.sub(r'\s*-\s*.*$', '', name)   # Remove taglines
                                            if name and not result.get('caller_name'):
                                                result['caller_name'] = name.strip()
                                                logger.info(f"Found name from social media: {name}")
                                                return
                        except Exception as e:
                            continue
                
                await asyncio.sleep(random.uniform(2, 3))
                
        except Exception as e:
            logger.warning(f"Social media name extraction failed: {e}")

    async def official_database_search(self, phone_number: str, result: Dict):
        """Search official and government databases"""
        clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # Indian government and official sites
        official_sites = [
            f'https://www.trai.gov.in/search?query={clean_number}',
            f'https://www.dot.gov.in/search/{clean_number}',
            f'https://www.mca.gov.in/mcafoportal/companyLLPMasterData.do?companyName={clean_number}',
        ]
        
        for site in official_sites:
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                response = self.session.get(site, headers=headers, timeout=20, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text()
                    
                    # Look for official registrations
                    if 'registered' in text.lower() or 'license' in text.lower():
                        # Extract potential names
                        name_patterns = [
                            r'(?:Registered to|Licensed to|Owner)[:\s]+([A-Za-z\s]{3,50})',
                            r'(?:Company|Business)[:\s]+([A-Za-z\s]{3,50})',
                        ]
                        
                        for pattern in name_patterns:
                            matches = re.findall(pattern, text, re.I)
                            if matches:
                                name = matches[0].strip()
                                if name and not result.get('caller_name'):
                                    result['caller_name'] = name
                                    result['caller_type'] = 'registered_business'
                                    logger.info(f"Found official registration: {name}")
                                    return
                
                await asyncio.sleep(random.uniform(3, 5))
            except Exception as e:
                logger.warning(f"Official database search failed for {site}: {e}")
