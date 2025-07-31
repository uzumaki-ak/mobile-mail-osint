from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ScanRequest(BaseModel):
    phone_number: str

class ScanStatus(BaseModel):
    scan_id: str
    phone_number: str
    status: str
    progress: int
    features: Dict[str, str]
    started_at: str
    completed_at: Optional[str] = None
    errors: List[Dict[str, Any]] = []

class BasicInfo(BaseModel):
    country_code: Optional[str] = None
    region: Optional[str] = None
    carrier_name: Optional[str] = None
    line_type: Optional[str] = None

class Geolocation(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    timezone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class OwnerSpam(BaseModel):
    caller_name: Optional[str] = None
    spam_score: Optional[float] = None
    spam_tags: List[str] = []

class MessagingPresence(BaseModel):
    whatsapp_active: Optional[bool] = None
    telegram_active: Optional[bool] = None

class SocialMediaProfiles(BaseModel):
    instagram_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None

class BreachData(BaseModel):
    breached_emails: List[str] = []
    breach_dates: List[str] = []

class SpamReports(BaseModel):
    report_sources: List[str] = []
    report_texts: List[str] = []
    sentiment_score: Optional[float] = None

class DomainWhois(BaseModel):
    linked_domains: List[str] = []
    whois_registrar: Optional[str] = None
    creation_date: Optional[str] = None

class ProfileImages(BaseModel):
    insta_dp: Optional[str] = None
    whatsapp_dp: Optional[str] = None
    telegram_dp: Optional[str] = None

class NumberReassignment(BaseModel):
    is_reassigned: Optional[bool] = None
    original_carrier: Optional[str] = None

class OnlineMentions(BaseModel):
    first_seen_date: Optional[str] = None
    mention_count: Optional[int] = None
    mention_sources: List[str] = []

class PhoneIntelResponse(BaseModel):
    phone_number: str
    scan_date: str
    basic_info: BasicInfo
    geolocation: Geolocation
    owner_spam: OwnerSpam
    messaging_presence: MessagingPresence
    social_media_profiles: SocialMediaProfiles
    breach_data: BreachData
    spam_reports: SpamReports
    domain_whois: DomainWhois
    profile_images: ProfileImages
    number_reassignment: NumberReassignment
    online_mentions: OnlineMentions
    errors: List[Dict[str, Any]] = []
