import os
import sys
from openai import OpenAI
import yfinance as yf
import pandas as pd
from web_scraper import get_website_text_content
import json
import re
from typing import List, Dict, Any

class PEResearchEngine:
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
    def extract_company_name(self, query: str) -> str:
        """Extract company name from user query using AI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract the company name from the user query. Return only the company name, nothing else. If multiple companies are mentioned, return the primary one being asked about."
                    },
                    {"role": "user", "content": query}
                ],
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fallback: simple regex extraction
            company_patterns = [
                r"about\s+([A-Za-z0-9\s&.-]+?)(?:\s|$|\?)",
                r"([A-Za-z0-9\s&.-]+)'s\s+",
                r"analyze\s+([A-Za-z0-9\s&.-]+?)(?:\s|$|\?)",
            ]
            
            for pattern in company_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            
            return "Unknown Company"
    
    def get_financial_data(self, company_name: str) -> Dict[str, Any]:
        """Get basic financial data using yfinance"""
        try:
            # Try to find ticker symbol
            ticker_search = yf.search(company_name)
            if not ticker_search.empty:
                ticker = ticker_search.iloc[0]['symbol']
            else:
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
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst specializing in competitive analysis. Provide a comprehensive competitor analysis including direct competitors, market positioning, and competitive advantages."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze the competitive landscape for {company_name} in the {sector} sector, specifically in {industry}. Include direct competitors, market share considerations, and competitive positioning."
                    }
                ],
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Could not generate competitor analysis: {str(e)}"
    
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
            
            # Generate comprehensive analysis
            system_prompt = """You are a Private Equity research analyst providing comprehensive company analysis. 
            Your responses should be professional, detailed, and focused on PE investment considerations.
            
            Structure your response with clear sections:
            - Company Overview
            - Financial Highlights  
            - Key Competitors
            - Investment Considerations (Strengths, Challenges, Opportunities)
            - PE Relevance
            
            Use the provided data to give accurate, specific insights. If data is limited, acknowledge this clearly.
            Format your response in markdown with clear headings and bullet points for readability."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                max_tokens=1500
            )
            
            ai_analysis = response.choices[0].message.content
            
            # Format the final response
            if 'error' not in financial_data:
                final_response = f"# {financial_data.get('company_name', company_name)} - PE Research Analysis\n\n{ai_analysis}"
            else:
                final_response = f"# {company_name} - PE Research Analysis\n\n{ai_analysis}"
            
            return final_response
            
        except Exception as e:
            return f"""**Analysis Error**

I encountered an issue while researching {company_name if 'company_name' in locals() else 'the requested company'}:

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
