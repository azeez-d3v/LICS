import asyncio
import importlib
import os
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from datetime import datetime
from services.session_manager import SessionManager
from services.models import SchoolInfo
import re

class BaseScraper:
    """Base class for all school-specific scrapers"""
    
    def __init__(self):
        """Initialize the base scraper"""
        self.base_url = ""
        self.name = ""
        self.short_name = ""
        
    async def scrape(self, school_data=None):
        """
        Abstract method to be implemented by subclasses
        
        Args:
            school_data: Optional school data dictionary
            
        Returns:
            Dictionary with scraped school information
        """
        raise NotImplementedError("Subclasses must implement scrape method")

class SchoolScraper:
    """Universal scraper for school data with a consistent architecture"""
    
    def __init__(self):
        """Initialize the scraper with default headers"""
        self.session_manager = SessionManager(default_headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'DNT': '1',
        })
    
    async def scrape_school(self, school: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scrape comprehensive data for a school using a universal structure
        
        Args:
            school: School data dictionary from SchoolData utility
            
        Returns:
            Dictionary with standardized school information
        """
        # Try to use a school-specific scraper if available
        try:
            school_name_short = school["name"].lower().split()[0]
            if school_name_short == "the":
                school_name_short = school["name"].lower().split()[1]
            
            # Convert to abbreviation if possible
            if len(school["name"].split()) > 1:
                abbreviation = ''.join([word[0].lower() for word in school["name"].split() 
                                       if word.lower() not in ['the', 'and', 'of']])
            else:
                abbreviation = school_name_short
            
            # Try to load school-specific scraper
            module_path = f"services.schools.{abbreviation}_scraper"
            try:
                module = importlib.import_module(module_path)
                # Find the class - it should be the capitalized abbreviation + "Scraper"
                class_name = abbreviation.upper() + "Scraper"
                scraper_class = getattr(module, class_name)
                scraper = scraper_class()
                return await scraper.scrape(school)
            except (ImportError, AttributeError):
                # If specific scraper doesn't exist, continue with universal scraper
                pass
        except Exception as e:
            print(f"Error loading school-specific scraper: {str(e)}")
        
        # Create a school info object with the universal structure
        school_info = SchoolInfo(
            name=school["name"],
            link=school["link"]
        )
        
        try:
            # Parse school fees
            fee_data = await self._scrape_field(school, "school_fee")
            school_info.school_fee = fee_data
            
            # Parse program/curriculum
            program_data = await self._scrape_field(school, "program")
            school_info.program = program_data
            
            # Parse enrollment process
            enrollment_data = await self._scrape_field(school, "Enrollment Process and Requirements")
            school_info.enrollment_process = enrollment_data
            
            # Parse events
            events_data = await self._scrape_field(school, "Upcoming Events")
            school_info.events = events_data
            
            # Parse discounts and scholarships
            discount_data = await self._scrape_field(school, "Discounts and Scholarship")
            school_info.discounts_scholarships = discount_data
            
            # Parse contact information
            contact_data = await self._scrape_field(school, "Contact Information ")
            school_info.contact_info = contact_data
            
        except Exception as e:
            school_info.notes = f"Error during scraping: {str(e)} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return school_info.to_dict()
    
    async def _scrape_field(self, school: Dict[str, Any], field_name: str) -> str:
        """
        Scrape specific field data from URLs
        
        Args:
            school: School data dictionary
            field_name: Name of the field to scrape
            
        Returns:
            Formatted string with scraped information
        """
        field_data = school.get(field_name, [])
        
        # Handle empty fields
        if not field_data:
            return "No data available"
        
        # Handle string URLs (convert to list)
        if isinstance(field_data, str):
            field_data = [field_data]
        
        # Scrape data from each URL
        results = []
        for url in field_data:
            try:
                # Skip empty URLs
                if not url:
                    continue
                    
                # Get HTML content
                response = await self.session_manager.get(url)
                html = response.text
                
                # Parse HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract main content
                content = self._extract_content(soup, field_name)
                if content:
                    results.append(f"From {url}:\n{content}")
            except Exception as e:
                results.append(f"Error scraping {url}: {str(e)}")
        
        # Join results with separators
        if not results:
            return "No data available"
        
        return "\n\n---\n\n".join(results)
    
    def _extract_content(self, soup: BeautifulSoup, field_name: str) -> str:
        """
        Extract relevant content based on field name
        
        Args:
            soup: BeautifulSoup object
            field_name: Name of the field being scraped
            
        Returns:
            Formatted string with extracted content
        """
        # Remove script and style elements
        for script in soup(["script", "style", "iframe", "noscript"]):
            script.extract()
        
        content = ""
        
        # Try to find main content container
        main_content = self._find_main_content(soup)
        
        if not main_content:
            # Fallback to extracting relevant sections
            if field_name == "school_fee":
                content = self._extract_fees(soup)
            elif field_name == "program":
                content = self._extract_program(soup)
            elif "Enrollment" in field_name:
                content = self._extract_enrollment(soup)
            elif "Events" in field_name:
                content = self._extract_events(soup)
            elif "Discounts" in field_name:
                content = self._extract_scholarships(soup)
            elif "Contact" in field_name:
                content = self._extract_contact(soup)
            else:
                # Generic content extraction
                paragraphs = soup.find_all('p')
                content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        else:
            # Extract text from main content
            paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content).strip()
        content = re.sub(r'\n+', '\n', content).strip()
        
        return content[:5000] if content else "No structured data found"
    
    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Any]:
        """Find the main content container in a webpage"""
        # Try common content container selectors
        selectors = [
            'main', '#main', '.main', 
            'article', '.article', '#article',
            '.content', '#content', '.page-content', 
            '.entry-content', '.post-content',
            '.container', '.inner-container'
        ]
        
        for selector in selectors:
            content = soup.select_one(selector)
            if content and len(content.get_text(strip=True)) > 100:
                return content
                
        # Try to find largest text container
        containers = soup.find_all(['div', 'section'], class_=True)
        if containers:
            # Sort by amount of text content
            containers = sorted(containers, key=lambda x: len(x.get_text(strip=True)), reverse=True)
            if containers and len(containers[0].get_text(strip=True)) > 100:
                return containers[0]
        
        return None
    
    def _extract_fees(self, soup: BeautifulSoup) -> str:
        """Extract school fee information"""
        # Look for tables that might contain fee information
        tables = soup.find_all('table')
        if tables:
            return "\n".join([table.get_text(strip=True, separator="\n") for table in tables])
        
        # Look for fee-related content
        fee_related = soup.find_all(
            lambda tag: tag.name in ['div', 'section', 'p'] and 
            any(keyword in tag.get_text().lower() for keyword in ['fee', 'tuition', 'cost', 'payment', 'financial'])
        )
        
        if fee_related:
            return "\n".join([elem.get_text(strip=True) for elem in fee_related])
        
        return ""
    
    def _extract_program(self, soup: BeautifulSoup) -> str:
        """Extract program/curriculum information"""
        # Look for curriculum-related content
        program_related = soup.find_all(
            lambda tag: tag.name in ['div', 'section', 'p', 'li'] and 
            any(keyword in tag.get_text().lower() for keyword in ['program', 'curriculum', 'academic', 'course', 'study'])
        )
        
        if program_related:
            return "\n".join([elem.get_text(strip=True) for elem in program_related])
        
        return ""
    
    def _extract_enrollment(self, soup: BeautifulSoup) -> str:
        """Extract enrollment process information"""
        # Look for enrollment-related content
        enrollment_related = soup.find_all(
            lambda tag: tag.name in ['div', 'section', 'p', 'li'] and 
            any(keyword in tag.get_text().lower() for keyword in ['enroll', 'admission', 'application', 'apply', 'requirement'])
        )
        
        if enrollment_related:
            return "\n".join([elem.get_text(strip=True) for elem in enrollment_related])
        
        return ""
    
    def _extract_events(self, soup: BeautifulSoup) -> str:
        """Extract upcoming events information"""
        # Look for event-related content
        event_related = soup.find_all(
            lambda tag: tag.name in ['div', 'section', 'p', 'li'] and 
            any(keyword in tag.get_text().lower() for keyword in ['event', 'calendar', 'upcoming', 'schedule'])
        )
        
        if event_related:
            return "\n".join([elem.get_text(strip=True) for elem in event_related])
        
        return ""
    
    def _extract_scholarships(self, soup: BeautifulSoup) -> str:
        """Extract scholarship information"""
        # Look for scholarship-related content
        scholarship_related = soup.find_all(
            lambda tag: tag.name in ['div', 'section', 'p', 'li'] and 
            any(keyword in tag.get_text().lower() for keyword in ['scholarship', 'financial aid', 'discount', 'grant', 'assistance'])
        )
        
        if scholarship_related:
            return "\n".join([elem.get_text(strip=True) for elem in scholarship_related])
        
        return ""
    
    def _extract_contact(self, soup: BeautifulSoup) -> str:
        """Extract contact information"""
        # Look for contact-related content
        contact_related = soup.find_all(
            lambda tag: tag.name in ['div', 'section', 'p', 'li', 'address'] and 
            any(keyword in tag.get_text().lower() for keyword in ['contact', 'email', 'phone', 'address', 'location'])
        )
        
        if contact_related:
            return "\n".join([elem.get_text(strip=True) for elem in contact_related])
        
        return ""