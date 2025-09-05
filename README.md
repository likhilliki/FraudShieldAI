# FraudShield AI

**AI-Powered Fraud Detection for Retail Investors**

FraudShield AI is a comprehensive Progressive Web App designed to protect retail investors from market frauds using advanced AI analysis, live SEBI registry verification, and real-time market data analysis.

## 🚀 Features

### Core Functionality
- **SEBI Registry Verification**: Live verification against official SEBI intermediary registry
- **Corporate Announcement Validation**: Verify announcements against official NSE/BSE filings
- **Social Media Fraud Detection**: AI-powered detection of investment scams on social platforms
- **Pump & Dump Detection**: Market anomaly analysis to identify manipulation schemes
- **AI Credibility Scoring**: GPT-4o-mini powered risk assessment with plain English explanations
- **One-Click SEBI Reporting**: Auto-generate fraud reports with evidence

### Technical Features
- **Progressive Web App**: Works offline and can be installed on mobile devices
- **Real-time Data**: Live scraping of SEBI, NSE, and BSE data sources
- **SQLite Database**: Local evidence logging and historical analysis
- **RESTful API**: Clean backend architecture with comprehensive endpoints
- **Responsive Design**: Optimized for mobile and desktop experiences

## 🛠 Tech Stack

**Frontend:**
- React 18 with TypeScript
- Tailwind CSS for styling
- Lucide React for icons
- Vite for development and building

**Backend:**
- Flask (Python 3.9+)
- SQLite database
- Beautiful Soup for web scraping
- Pandas for data processing
- OpenAI API for AI analysis
- YFinance for stock data

## 📦 Installation

### Prerequisites
- Node.js 16+ and npm
- Python 3.9+
- OpenAI API key

### Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_openai_api_key_here"
export FLASK_ENV=development

# Initialize database
python database.py

# Start Flask server
python app.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
DATABASE_URL=sqlite:///fraudshield.db
```

### OpenAI API Setup

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the `OPENAI_API_KEY` environment variable
3. The app uses GPT-4o-mini for cost-effective AI analysis

## 🗄 Database Schema

The application uses SQLite with the following tables:

- **intermediaries**: SEBI registered advisors and intermediaries
- **announcements**: Corporate filings from NSE/BSE
- **history**: All verification requests and AI analysis results
- **market_data**: Stock price and volume data for anomaly detection

## 📊 API Endpoints

### Verification Endpoints
- `POST /verify/advisor` - Verify SEBI registration
- `POST /verify/announcement` - Validate corporate announcements
- `POST /verify/social` - Detect social media fraud
- `POST /verify/anomaly` - Identify market manipulation

### Data Management
- `POST /refresh/sebi` - Update SEBI registry data
- `POST /refresh/market` - Update market data
- `GET /history` - Get verification history
- `GET /health` - Health check

## 🔄 Data Refresh

### SEBI Registry Update
```bash
curl -X POST http://localhost:5000/refresh/sebi
```

The scraper automatically:
1. Downloads Excel files from SEBI website
2. Parses intermediary data using pandas
3. Updates SQLite database
4. Handles duplicates and data validation

### Market Data Update
```bash
curl -X POST http://localhost:5000/refresh/market
```

Updates:
- NSE/BSE corporate announcements
- Stock price and volume data
- Market anomaly indicators

## 🤖 AI Analysis

The AI scoring system uses OpenAI's GPT-4o-mini to:

1. **Analyze Content**: Process advisor names, announcements, or social media posts
2. **Risk Scoring**: Generate 0-100 risk scores with reasoning
3. **Pattern Detection**: Identify fraud indicators and manipulation tactics
4. **Plain English**: Provide explanations accessible to retail investors

### Sample AI Analysis Flow

```python
from ai_scoring import ai_credibility_analysis

result = ai_credibility_analysis(
    content="Guaranteed 300% returns in 30 days!",
    context="social"
)

print(result)
# {
#   "risk_score": 95,
#   "risk_level": "High", 
#   "ai_explanation": "This content shows classic fraud indicators..."
# }
```

## 🔍 Usage Examples

### Verify an Advisor
```bash
curl -X POST http://localhost:5000/verify/advisor \
  -H "Content-Type: application/json" \
  -d '{"advisor_name": "ABC Investment Advisors"}'
```

### Check Corporate Announcement
```bash
curl -X POST http://localhost:5000/verify/announcement \
  -H "Content-Type: application/json" \
  -d '{"announcement": "XYZ Corp announces 50% dividend", "ticker": "XYZ"}'
```

### Social Media Fraud Check
```bash
curl -X POST http://localhost:5000/verify/social \
  -H "Content-Type: application/json" \
  -d '{"content": "Buy ABC stock for guaranteed 500% returns!"}'
```

## 🚀 Deployment

### Frontend (Netlify)
```bash
npm run build
# Deploy dist/ folder to Netlify
```

### Backend (Render/Railway)
1. Push code to GitHub
2. Connect to Render/Railway
3. Set environment variables
4. Deploy with auto-scaling

### Environment Variables for Production
```env
OPENAI_API_KEY=your_production_key
FLASK_ENV=production  
DATABASE_URL=your_production_db_url
```

## 🔒 Security & Compliance

- **Data Privacy**: No personal data stored beyond verification history
- **API Security**: Rate limiting and input validation
- **SEBI Compliance**: Data sourced from official registries only
- **Fraud Reporting**: Direct integration with SEBI complaint system

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Run Frontend Tests  
```bash
npm test
```

### Test AI Scoring
```bash
cd backend
python ai_scoring.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

FraudShield AI is for informational purposes only. Always conduct your own research and consult qualified financial advisors before making investment decisions. The AI analysis should be used as one of many factors in your due diligence process.

## 📞 Support

For support, email support@fraudshield.ai or create an issue in the GitHub repository.

## 🙏 Acknowledgments

- SEBI for providing public registry data
- NSE & BSE for corporate announcement access  
- OpenAI for GPT-4o-mini API
- Yahoo Finance for stock data API

---

**Built with ❤️ for Indian retail investors**