import asyncio
import json
import logging
import os
import csv
from datetime import datetime
from typing import Dict, Any, Callable, Optional
import aiohttp
import requests
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
import re
from urllib.parse import quote
import time

from models.phone_data import *

logger = logging.getLogger(__name__)

class PhoneIntelService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # API Keys from environment
        self.numverify_key = os.getenv('NUMVERIFY_API_KEY')
        self.abstractapi_key = os.getenv('ABSTRACTAPI_KEY')
        self.whoisxml_key = os.getenv('WHOISXML_API_KEY')
        self.hlrlookup_key = os.getenv('HLRLOOKUP_API_KEY')
        self.breach_directory_key = os.getenv('BREACH_DIRECTORY_API_KEY')

    async def scan_phone_number(self, phone_number: str, status_callback: Callable) -> Dict[str, Any]:
        """Main scan orchestrator"""
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

        # Feature scanning functions
        features = [
            ("basic_info", self.get_basic_info),
            ("geolocation", self.get_geolocation),
            ("owner_spam", self.get_owner_spam),
            ("messaging", self.get_messaging_presence),
            ("social_media", self.get_social_media_profiles),
            ("breach_data", self.get_breach_data),
            ("spam_reports", self.get_spam_reports),
            ("domain_whois", self.get_domain_whois),
            ("profile_images", self.get_profile_images),
            ("reassignment", self.get_number_reassignment),
            ("online_mentions", self.get_online_mentions)
        ]

        for feature_name, feature_func in features:
            try:
                status_callback(feature_name, "running")
                logger.info(f"Starting {feature_name} for {phone_number}")
                
                feature_data = await feature_func(phone_number)
                results[feature_name.replace("_", "_")] = feature_data
                
                # Save raw data
                raw_file = f"output/raw/{phone_number}_{feature_name}.json"
                with open(raw_file, 'w') as f:
                    json.dump(feature_data, f, indent=2, default=str)
                
                status_callback(feature_name, "success")
                logger.info(f"Completed {feature_name} for {phone_number}")
                
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

    async def get_basic_info(self, phone_number: str) -> Dict[str, Any]:
        """Get basic phone info with API + fallbacks"""
        result = {"country_code": None, "region": None, "carrier_name": None, "line_type": None}
        
        # Method 1: Numverify API
        if self.numverify_key:
            try:
                url = f"http://apilayer.net/api/validate"
                params = {
                    'access_key': self.numverify_key,
                    'number': phone_number
                }
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('valid'):
                        result.update({
                            "country_code": data.get('country_code'),
                            "region": data.get('location'),
                            "carrier_name": data.get('carrier'),
                            "line_type": data.get('line_type')
                        })
                        return result
            except Exception as e:
                logger.warning(f"Numverify API failed: {e}")

        # Method 2: AbstractAPI
        if self.abstractapi_key:
            try:
                url = f"https://phonevalidation.abstractapi.com/v1/"
                params = {
                    'api_key': self.abstractapi_key,
                    'phone': phone_number
                }
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('valid'):
                        result.update({
                            "country_code": data.get('country', {}).get('code'),
                            "region": data.get('location'),
                            "carrier_name": data.get('carrier'),
                            "line_type": data.get('type')
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
                    "line_type": "mobile" if phonenumbers.number_type(parsed) in [0, 1] else "landline"
                })
                return result
        except Exception as e:
            logger.warning(f"phonenumbers library failed: {e}")

        # Fallback 2: Scrape carrier lookup sites
        try:
            await self.scrape_carrier_info(phone_number, result)
        except Exception as e:
            logger.warning(f"Carrier scraping failed: {e}")

        return result

    async def get_geolocation(self, phone_number: str) -> Dict[str, Any]:
        """Get geolocation data"""
        result = {"city": None, "state": None, "timezone": None, "latitude": None, "longitude": None}
        
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
                    # Try to parse city/state from location
                    parts = location.split(", ")
                    if len(parts) >= 2:
                        result["city"] = parts[0]
                        result["state"] = parts[1]
                    else:
                        result["region"] = location
        except Exception as e:
            logger.warning(f"Geolocation failed: {e}")

        return result

    async def get_owner_spam(self, phone_number: str) -> Dict[str, Any]:
        """Get owner name and spam information"""
        result = {"caller_name": None, "spam_score": 0.0, "spam_tags": []}
        
        # Scrape Truecaller
        try:
            await self.scrape_truecaller(phone_number, result)
        except Exception as e:
            logger.warning(f"Truecaller scraping failed: {e}")

        # Scrape other caller ID sites
        try:
            await self.scrape_caller_id_sites(phone_number, result)
        except Exception as e:
            logger.warning(f"Caller ID scraping failed: {e}")

        return result

    async def get_messaging_presence(self, phone_number: str) -> Dict[str, Any]:
        """Check WhatsApp and Telegram presence"""
        result = {"whatsapp_active": None, "telegram_active": None}
        
        # Check WhatsApp (simplified check)
        try:
            # This would require WhatsApp Web automation
            # For now, return None to indicate not implemented
            pass
        except Exception as e:
            logger.warning(f"WhatsApp check failed: {e}")

        # Check Telegram
        try:
            # This would require Telegram API
            # For now, return None to indicate not implemented
            pass
        except Exception as e:
            logger.warning(f"Telegram check failed: {e}")

        return result

    async def get_social_media_profiles(self, phone_number: str) -> Dict[str, Any]:
        """Search for social media profiles"""
        result = {"instagram_url": None, "twitter_url": None, "facebook_url": None}
        
        # Google dork searches
        search_queries = [
            f'"{phone_number}" site:instagram.com',
            f'"{phone_number}" site:twitter.com',
            f'"{phone_number}" site:facebook.com'
        ]
        
        for query in search_queries:
            try:
                await self.google_dork_search(query, result)
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                logger.warning(f"Social media search failed: {e}")

        return result

    async def get_breach_data(self, phone_number: str) -> Dict[str, Any]:
        """Check for data breaches"""
        result = {"breached_emails": [], "breach_dates": []}
        
        # BreachDirectory API
        if self.breach_directory_key:
            try:
                # This would require actual BreachDirectory API implementation
                pass
            except Exception as e:
                logger.warning(f"BreachDirectory API failed: {e}")

        # Scrape public breach databases
        try:
            await self.scrape_breach_databases(phone_number, result)
        except Exception as e:
            logger.warning(f"Breach database scraping failed: {e}")

        return result

    async def get_spam_reports(self, phone_number: str) -> Dict[str, Any]:
        """Get spam/fraud reports"""
        result = {"report_sources": [], "report_texts": [], "sentiment_score": None}
        
        # Scrape 800notes.com
        try:
            await self.scrape_800notes(phone_number, result)
        except Exception as e:
            logger.warning(f"800notes scraping failed: {e}")

        # Scrape who-called.me
        try:
            await self.scrape_who_called(phone_number, result)
        except Exception as e:
            logger.warning(f"who-called.me scraping failed: {e}")

        return result

    async def get_domain_whois(self, phone_number: str) -> Dict[str, Any]:
        """Get domain/WHOIS information"""
        result = {"linked_domains": [], "whois_registrar": None, "creation_date": None}
        
        # WhoisXML API
        if self.whoisxml_key:
            try:
                # This would require actual WhoisXML API implementation
                pass
            except Exception as e:
                logger.warning(f"WhoisXML API failed: {e}")

        # Search for domains associated with phone number
        try:
            await self.search_associated_domains(phone_number, result)
        except Exception as e:
            logger.warning(f"Domain search failed: {e}")

        return result

    async def get_profile_images(self, phone_number: str) -> Dict[str, Any]:
        """Get profile images from various platforms"""
        result = {"insta_dp": None, "whatsapp_dp": None, "telegram_dp": None}
        
        # This would require complex automation and login
        # For now, return empty results
        return result

    async def get_number_reassignment(self, phone_number: str) -> Dict[str, Any]:
        """Check if number was reassigned"""
        result = {"is_reassigned": None, "original_carrier": None}
        
        # HLRLookup API
        if self.hlrlookup_key:
            try:
                # This would require actual HLRLookup API implementation
                pass
            except Exception as e:
                logger.warning(f"HLRLookup API failed: {e}")

        return result

    async def get_online_mentions(self, phone_number: str) -> Dict[str, Any]:
        """Get online mentions timeline"""
        result = {"first_seen_date": None, "mention_count": 0, "mention_sources": []}
        
        # Google/Bing searches with date filters
        try:
            await self.search_online_mentions(phone_number, result)
        except Exception as e:
            logger.warning(f"Online mentions search failed: {e}")

        return result

    # Helper scraping methods
    async def scrape_carrier_info(self, phone_number: str, result: Dict):
        """Scrape carrier information from lookup sites"""
        sites = [
            f"https://www.freecarrierlookup.com/lookup.php?number={phone_number}",
            f"https://www.carrierlookup.com/index.php/lookup/carrier?msisdn={phone_number}"
        ]
        
        for site in sites:
            try:
                response = self.session.get(site, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Parse carrier information from HTML
                    # This would need site-specific parsing logic
                    pass
            except Exception as e:
                logger.warning(f"Failed to scrape {site}: {e}")

    async def scrape_truecaller(self, phone_number: str, result: Dict):
        """Scrape Truecaller for caller name and spam info"""
        # This would require complex automation due to Truecaller's anti-bot measures
        pass

    async def scrape_caller_id_sites(self, phone_number: str, result: Dict):
        """Scrape various caller ID sites"""
        sites = [
            f"https://www.whocalld.com/+{phone_number.replace('+', '')}",
            f"https://www.shouldianswer.com/phone-number/{phone_number.replace('+', '')}"
        ]
        
        for site in sites:
            try:
                response = self.session.get(site, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Parse caller information
                    # This would need site-specific parsing logic
                    pass
            except Exception as e:
                logger.warning(f"Failed to scrape {site}: {e}")

    async def google_dork_search(self, query: str, result: Dict):
        """Perform Google dork searches"""
        # This would require Google Search API or scraping
        # For now, return empty results due to Google's anti-bot measures
        pass

    async def scrape_breach_databases(self, phone_number: str, result: Dict):
        """Scrape public breach databases"""
        # This would require access to breach databases
        pass

    async def scrape_800notes(self, phone_number: str, result: Dict):
        """Scrape 800notes.com for spam reports"""
        try:
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            url = f"https://800notes.com/Phone.aspx/{clean_number}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse spam reports
                reports = soup.find_all('div', class_='report')
                for report in reports:
                    text = report.get_text(strip=True)
                    if text:
                        result["report_texts"].append(text)
                        result["report_sources"].append("800notes.com")
        except Exception as e:
            logger.warning(f"800notes scraping failed: {e}")

    async def scrape_who_called(self, phone_number: str, result: Dict):
        """Scrape who-called.me for reports"""
        try:
            clean_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            url = f"https://who-called.me/{clean_number}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse reports
                # This would need site-specific parsing logic
                pass
        except Exception as e:
            logger.warning(f"who-called.me scraping failed: {e}")

    async def search_associated_domains(self, phone_number: str, result: Dict):
        """Search for domains associated with phone number"""
        # This would require WHOIS database searches
        pass

    async def search_online_mentions(self, phone_number: str, result: Dict):
        """Search for online mentions with timeline"""
        # This would require search engine APIs or scraping
        pass

    async def export_results(self, phone_number: str, results: Dict):
        """Export results to CSV and PDF"""
        # Export to CSV
        csv_file = f"output/{phone_number}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Field', 'Value'])
            
            def flatten_dict(d, parent_key=''):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key).items())
                    elif isinstance(v, list):
                        items.append((new_key, ', '.join(map(str, v))))
                    else:
                        items.append((new_key, str(v)))
                return dict(items)
            
            flat_results = flatten_dict(results)
            for key, value in flat_results.items():
                writer.writerow([key, value])

        # Export to PDF
        pdf_file = f"output/{phone_number}.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph(f"Phone Intelligence Report: {phone_number}", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        for section, data in results.items():
            if section not in ['phone_number', 'scan_date', 'errors'] and data:
                story.append(Paragraph(section.replace('_', ' ').title(), styles['Heading2']))
                if isinstance(data, dict):
                    for key, value in data.items():
                        if value:
                            story.append(Paragraph(f"{key}: {value}", styles['Normal']))
                story.append(Spacer(1, 12))
        
        doc.build(story)
