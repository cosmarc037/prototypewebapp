import trafilatura
import requests
from typing import Optional

def get_website_text_content(url: str) -> Optional[str]:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results is not directly readable, better to be summarized by LLM before consume
    by the user.

    Some common website to crawl information from:
    Company websites, Wikipedia pages, financial news sites
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text
        return None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def search_company_info(company_name: str) -> str:
    """
    Search for company information from multiple sources
    """
    sources = []
    
    # Try Wikipedia
    wiki_url = f"https://en.wikipedia.org/wiki/{company_name.replace(' ', '_')}"
    wiki_content = get_website_text_content(wiki_url)
    if wiki_content and len(wiki_content) > 200:
        sources.append(f"**Wikipedia Summary:**\n{wiki_content[:1500]}...\n")
    
    # Combine all sources
    if sources:
        return "\n".join(sources)
    else:
        return f"Limited web information available for {company_name}."

def get_financial_news(company_name: str) -> str:
    """
    Attempt to get recent financial news about the company
    """
    try:
        # This is a simplified approach - in production you might use news APIs
        search_terms = company_name.replace(' ', '+')
        # Note: This is a basic implementation - you might want to integrate with news APIs
        return f"For the latest financial news about {company_name}, please check financial news websites or use news APIs."
    except Exception as e:
        return f"Could not retrieve financial news: {str(e)}"
