# Phone Intelligence Toolkit

A comprehensive OSINT (Open Source Intelligence) toolkit for phone number analysis with Python FastAPI backend and Next.js 15 TypeScript frontend.

## Features

### 🔍 Intelligence Gathering
- **Basic Info**: Country code, region, carrier name, line type
- **Geolocation**: City, state, timezone coordinates
- **Owner & Spam**: Caller name, spam score, spam tags
- **Messaging Apps**: WhatsApp/Telegram presence detection
- **Social Media**: Instagram, Twitter, Facebook profile discovery
- **Breach Data**: Email breaches and leak information
- **Spam Reports**: Community reports and sentiment analysis
- **Domain/WHOIS**: Linked domains and registration data
- **Profile Images**: Profile pictures from various platforms
- **Number Reassignment**: Carrier change detection
- **Online Mentions**: Timeline and mention tracking

### 🛡️ Robust Fallback System
Each feature implements multiple fallback methods:
1. **Primary**: Free API calls (Numverify, AbstractAPI, etc.)
2. **Secondary**: Web scraping with requests + BeautifulSoup4
3. **Tertiary**: Browser automation with Selenium/Playwright

### 💾 Data Management
- Raw JSON storage per feature
- Consolidated results export (JSON, CSV, PDF)
- Profile image downloads
- Comprehensive error logging
- Browser localStorage persistence

### 🎨 Matrix-Style UI
- Animated matrix background
- Blue/black cyberpunk theme
- Real-time progress tracking
- Collapsible result sections
- Responsive design

## Installation & Setup

### Backend (Python 3.11.9)

1. **Clone and setup backend**:
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

2. **Configure environment variables**:
\`\`\`bash
cp .env.example .env
# Edit .env with your API keys
\`\`\`

3. **Create output directories**:
\`\`\`bash
mkdir -p output/raw output/images
\`\`\`

4. **Run the FastAPI server**:
\`\`\`bash
python main.py
# Server runs on http://localhost:8000
\`\`\`

### Frontend (Next.js 15)

1. **Install dependencies**:
\`\`\`bash
npm install
\`\`\`

2. **Run development server**:
\`\`\`bash
npm run dev
# Frontend runs on http://localhost:3000
\`\`\`

## API Keys Required

Add these to your `backend/.env` file:

\`\`\`env
# Primary APIs (Free tiers available)
NUMVERIFY_API_KEY=your_numverify_key_here
ABSTRACTAPI_KEY=your_abstractapi_key_here
WHOISXML_API_KEY=your_whoisxml_key_here
HLRLOOKUP_API_KEY=your_hlrlookup_key_here
BREACH_DIRECTORY_API_KEY=your_breach_directory_key_here
\`\`\`

### API Providers & Limits:
- **Numverify**: 250 requests/month (free)
- **AbstractAPI**: 1,000 requests/month (free)
- **WhoisXML**: 500 requests/month (free)
- **HLRLookup**: 100 requests/month (free)
- **BreachDirectory**: Varies by plan

## Usage

### Web Interface
1. Open http://localhost:3000
2. Enter phone number (e.g., +1 555 123 4567)
3. Click "Start Scan"
4. Monitor real-time progress
5. View detailed results
6. Download reports (JSON/CSV/PDF)

### API Endpoints
\`\`\`bash
# Start scan
POST /api/scan
{
  "phone_number": "+1 555 123 4567"
}

# Check status
GET /api/scan/{scan_id}/status

# Get results
GET /api/scan/{scan_id}/results

# Download files
GET /api/download/{phone_number}/{json|csv|pdf}
\`\`\`

## Architecture

### Backend Structure
\`\`\`
backend/
├── main.py                 # FastAPI application
├── models/
│   └── phone_data.py      # Pydantic models
├── services/
│   └── phone_intel.py     # Core intelligence service
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── output/               # Results storage
    ├── raw/              # Raw JSON per feature
    ├── images/           # Profile pictures
    └── *.{json,csv,pdf}  # Final reports
\`\`\`

### Frontend Structure
\`\`\`
├── app/
│   ├── page.tsx          # Main application
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── components/
│   ├── phone-scanner.tsx     # Main scanner interface
│   ├── scan-progress.tsx     # Progress tracking
│   ├── scan-results.tsx      # Results display
│   ├── scan-history.tsx      # History management
│   ├── matrix-background.tsx # Animated background
│   └── ui/               # Reusable UI components
└── package.json
\`\`\`

## Error Handling

- All API failures gracefully fallback to scraping
- Scraping failures logged with timestamps
- Partial results saved even if some features fail
- Comprehensive error reporting in results
- Rate limiting and retry mechanisms

## Security & Ethics

⚠️ **Important**: This tool is for educational and legitimate OSINT purposes only.

- Respect rate limits and ToS of all services
- Use responsibly and legally
- Consider privacy implications
- Implement proper access controls in production
- Some features may require additional authentication

## Troubleshooting

### Common Issues:

1. **API Rate Limits**: Tool automatically falls back to scraping
2. **Selenium Issues**: Install ChromeDriver: `pip install chromedriver-autoinstaller`
3. **CORS Errors**: Ensure backend runs on port 8000
4. **Missing Dependencies**: Run `pip install -r requirements.txt`

### Performance Tips:

- Use SSD storage for faster file I/O
- Increase timeout values for slow networks
- Consider Redis for production scan status storage
- Implement database for persistent scan history

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## License

This project is for educational purposes. Please use responsibly and in accordance with applicable laws and service terms.

---

**⚡ Ready to analyze phone numbers like a pro? Start your first scan now!**
