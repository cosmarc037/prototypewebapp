import os
import sys
import yfinance as yf
import pandas as pd
from web_scraper import get_website_text_content
import json
import re
from typing import List, Dict, Any
import requests

class PEResearchEngine:
    def __init__(self):
        # Using Hugging Face Inference API with GPT-NeoX-20B
        self.hf_api_url = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neox-20b"
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")  # Optional, can work without it
        
    def query_hf_model(self, prompt: str, max_tokens: int = 200) -> str:
        """Query Hugging Face model with fallback to pattern matching"""
        try:
            headers = {}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.hf_api_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
            return ""
        except Exception:
            return ""

    def extract_company_name(self, query: str) -> str:
        """Extract company name from user query using AI or pattern matching"""
        # Try AI extraction first
        ai_prompt = f"Extract only the company name from this query: '{query}'\nCompany name:"
        ai_result = self.query_hf_model(ai_prompt, max_tokens=20)
        
        if ai_result and len(ai_result) < 50:
            return ai_result.strip()
        
        # Fallback: regex pattern extraction
        company_patterns = [
            r"about\s+([A-Za-z0-9\s&.-]+?)(?:\s|$|\?)",
            r"([A-Za-z0-9\s&.-]+)'s\s+",
            r"analyze\s+([A-Za-z0-9\s&.-]+?)(?:\s|$|\?)",
            r"tell me about\s+([A-Za-z0-9\s&.-]+?)(?:\s|$|\?)",
            r"research\s+([A-Za-z0-9\s&.-]+?)(?:\s|$|\?)",
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                # Clean up common words
                company = re.sub(r'\b(company|corp|corporation|inc|ltd|llc)\b', '', company, flags=re.IGNORECASE).strip()
                return company
        
        return "Unknown Company"
    
    def get_financial_data(self, company_name: str) -> Dict[str, Any]:
        """Get basic financial data using yfinance"""
        try:
            # Common ticker mappings
            ticker_map = {
                'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL',
                'amazon': 'AMZN', 'tesla': 'TSLA', 'meta': 'META',
                'netflix': 'NFLX', 'nvidia': 'NVDA', 'facebook': 'META',
                'alphabet': 'GOOGL', 'ford': 'F', 'general motors': 'GM'
            }
            ticker = ticker_map.get(company_name.lower(), company_name.upper())
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            financial_data = {
                'ticker': ticker,
                'company_name': info.get('longName', company_name),
                'market_cap': info.get('marketCap'),
                'revenue': info.get('totalRevenue'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'employees': info.get('fullTimeEmployees'),
                'website': info.get('website'),
                'business_summary': info.get('longBusinessSummary'),
                'current_price': info.get('currentPrice'),
                'pe_ratio': info.get('trailingPE'),
                'profit_margin': info.get('profitMargins'),
                'revenue_growth': info.get('revenueGrowth'),
                'headquarters': f"{info.get('city', '')}, {info.get('state', '')} {info.get('country', '')}".strip(', ')
            }
            
            return financial_data
            
        except Exception as e:
            return {'error': f"Could not retrieve financial data: {str(e)}"}
    
    def scrape_company_info(self, company_name: str) -> str:
        """Scrape additional company information from the web"""
        try:
            # Try to get company information from their website or news
            search_urls = [
                f"https://en.wikipedia.org/wiki/{company_name.replace(' ', '_')}",
            ]
            
            scraped_content = ""
            for url in search_urls:
                try:
                    content = get_website_text_content(url)
                    if content and len(content) > 100:
                        scraped_content += f"\n\nSource: {url}\n{content[:2000]}..."
                        break
                except:
                    continue
            
            return scraped_content if scraped_content else "No additional web content found."
            
        except Exception as e:
            return f"Web scraping error: {str(e)}"
    
    def generate_competitor_analysis(self, company_data: Dict[str, Any]) -> str:
        """Generate competitor analysis using AI"""
        try:
            sector = company_data.get('sector', 'Unknown')
            industry = company_data.get('industry', 'Unknown')
            company_name = company_data.get('company_name', 'Unknown')
            
            prompt = f"""Analyze the competitive landscape for {company_name} in the {sector} sector, specifically in {industry}.

Company: {company_name}
Sector: {sector}
Industry: {industry}

Provide a comprehensive competitor analysis including:
1. Direct competitors
2. Market positioning
3. Competitive advantages
4. Market share considerations

Analysis:"""
            
            ai_result = self.query_hf_model(prompt, max_tokens=600)
            
            if ai_result:
                return ai_result
            else:
                # Fallback analysis based on sector/industry
                return self.generate_basic_competitor_analysis(company_name, sector, industry)
            
        except Exception as e:
            return f"Could not generate competitor analysis: {str(e)}"
    
    def generate_basic_competitor_analysis(self, company_name: str, sector: str, industry: str) -> str:
        """Generate basic competitor analysis without AI"""
        competitors_db = {
            'Technology': ['Apple', 'Microsoft', 'Google', 'Amazon', 'Meta'],
            'Automotive': ['Tesla', 'Ford', 'General Motors', 'Toyota', 'Volkswagen'],
            'Financial Services': ['JPMorgan Chase', 'Bank of America', 'Wells Fargo', 'Goldman Sachs'],
            'Healthcare': ['Johnson & Johnson', 'Pfizer', 'UnitedHealth', 'Merck'],
            'Consumer Discretionary': ['Amazon', 'Nike', 'Home Depot', 'McDonald\'s'],
            'Energy': ['ExxonMobil', 'Chevron', 'ConocoPhillips', 'BP'],
        }
        
        potential_competitors = competitors_db.get(sector, [])
        competitors_text = ', '.join([c for c in potential_competitors if c.lower() != company_name.lower()][:5])
        
        return f"""**Competitive Analysis for {company_name}**

**Sector:** {sector}
**Industry:** {industry}

**Key Competitors:** {competitors_text if competitors_text else 'Analysis requires additional research'}

**Market Position:** {company_name} operates in the {sector} sector within the {industry} industry. Competitive positioning depends on market share, innovation capabilities, and operational efficiency.

**Competitive Factors:**
- Brand recognition and customer loyalty
- Product/service differentiation
- Pricing strategy and cost structure
- Distribution channels and market reach
- Technology and innovation capabilities

*Note: Detailed competitive analysis requires current market data and industry reports.*"""
    
    def format_financial_data(self, data: Dict[str, Any]) -> str:
        """Format financial data for display"""
        if 'error' in data:
            return f"**Financial Data:** {data['error']}"
        
        formatted = "**Financial Highlights:**\n"
        
        if data.get('market_cap'):
            market_cap_b = data['market_cap'] / 1e9
            formatted += f"- Market Cap: ${market_cap_b:.1f}B\n"
        
        if data.get('revenue'):
            revenue_b = data['revenue'] / 1e9
            formatted += f"- Annual Revenue: ${revenue_b:.1f}B\n"
        
        if data.get('current_price'):
            formatted += f"- Stock Price: ${data['current_price']:.2f}\n"
        
        if data.get('pe_ratio'):
            formatted += f"- P/E Ratio: {data['pe_ratio']:.1f}\n"
        
        if data.get('profit_margin'):
            margin_pct = data['profit_margin'] * 100
            formatted += f"- Profit Margin: {margin_pct:.1f}%\n"
        
        if data.get('employees'):
            formatted += f"- Employees: {data['employees']:,}\n"
        
        if data.get('headquarters'):
            formatted += f"- Headquarters: {data['headquarters']}\n"
        
        return formatted
    
    def analyze_company(self, query: str, chat_history: List[Dict[str, str]]) -> str:
        """Main function to analyze a company based on user query"""
        try:
            # Extract company name from query
            company_name = self.extract_company_name(query)
            
            # Check if this is a follow-up question
            is_followup = len(chat_history) > 0 and any(
                keyword in query.lower() 
                for keyword in ['more', 'tell me more', 'continue', 'what about', 'also', 'additionally']
            )
            
            # Get financial data
            financial_data = self.get_financial_data(company_name)
            
            # Get additional web content
            web_content = self.scrape_company_info(company_name)
            
            # Generate competitor analysis
            competitor_analysis = self.generate_competitor_analysis(financial_data)
            
            # Build context for AI analysis
            context = f"""
            Company: {company_name}
            Financial Data: {json.dumps(financial_data, indent=2)}
            Web Content: {web_content[:1000]}...
            Competitor Analysis: {competitor_analysis}
            
            User Query: {query}
            Chat History: {json.dumps(chat_history[-5:], indent=2) if chat_history else 'None'}
            """
            
            # Generate comprehensive analysis using AI
            analysis_prompt = f"""As a Private Equity research analyst, provide comprehensive company analysis for investment considerations.

{context}

Structure your response with clear sections:
- Company Overview
- Financial Highlights  
- Key Competitors
- Investment Considerations (Strengths, Challenges, Opportunities)
- PE Relevance

Provide professional, detailed analysis focused on PE investment considerations. Use markdown formatting with clear headings and bullet points.

Analysis:"""
            
            ai_analysis = self.query_hf_model(analysis_prompt, max_tokens=1200)
            
            if not ai_analysis:
                # Fallback to structured analysis without AI
                ai_analysis = self.generate_structured_analysis(company_name, financial_data, competitor_analysis, web_content)
            
            # Format the final response
            if 'error' not in financial_data:
                final_response = f"# {financial_data.get('company_name', company_name)} - PE Research Analysis\n\n{ai_analysis}"
            else:
                final_response = f"# {company_name} - PE Research Analysis\n\n{ai_analysis}"
            
            return final_response
            
        except Exception as e:
            extracted_name = "the requested company"
            try:
                extracted_name = self.extract_company_name(query)
            except:
                pass
                
            return f"""**Analysis Error**

I encountered an issue while researching {extracted_name}:

**Error Details:** {str(e)}

**Possible Solutions:**
- Check if the company name is spelled correctly
- Try using the full company name or stock ticker
- Ensure the company is publicly traded or well-known
- Rephrase your question

**Example Queries:**
- "Tell me about Apple"
- "Analyze Tesla's market position" 
- "Who are Microsoft's competitors?"

Please try again with a different approach."""
    
    def generate_structured_analysis(self, company_name: str, financial_data: Dict[str, Any], competitor_analysis: str, web_content: str) -> str:
        """Generate structured analysis without AI"""
        formatted_financials = self.format_financial_data(financial_data)
        
        return f"""## Company Overview
{company_name} is a company operating in the {financial_data.get('sector', 'various')} sector, specifically in the {financial_data.get('industry', 'multiple industries')} space.

{formatted_financials}

## Key Competitors
{competitor_analysis}

## Investment Considerations

### Strengths
- Established market presence in {financial_data.get('sector', 'their sector')}
- {f"Market capitalization of ${financial_data.get('market_cap', 0)/1e9:.1f}B" if financial_data.get('market_cap') else "Significant market position"}
- {f"Revenue of ${financial_data.get('revenue', 0)/1e9:.1f}B annually" if financial_data.get('revenue') else "Established revenue streams"}

### Challenges
- Competitive market environment
- Industry-specific regulatory considerations
- Market volatility and economic factors

### Opportunities
- Sector growth potential
- Strategic expansion possibilities
- Operational efficiency improvements

## PE Relevance
This analysis provides foundational data for Private Equity evaluation. Key considerations include:
- Financial performance metrics
- Market position and competitive landscape
- Growth potential and scalability
- Operational improvement opportunities

*Note: This analysis is based on available public data. Detailed due diligence would require additional proprietary information and market research.*"""

    def get_chat_context(self, chat_history: List[Dict[str, str]]) -> str:
        """Extract relevant context from chat history"""
        if not chat_history:
            return ""
        
        # Get last few messages for context
        recent_messages = chat_history[-4:]
        context = "Recent conversation context:\n"
        for msg in recent_messages:
            context += f"{msg['role']}: {msg['content'][:200]}...\n"
        
        return context
