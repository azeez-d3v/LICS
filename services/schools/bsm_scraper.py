import sys
import os
from bs4 import BeautifulSoup
import re
import json
import logging
import asyncio

# Add parent directory to path to allow imports when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.scraper import BaseScraper
from services.session_manager import SessionManager
from services.playwright_manager import get_with_playwright, close_playwright

logger = logging.getLogger(__name__)

class BSMScraper(BaseScraper):
    """Scraper for British School Manila website"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.britishschoolmanila.org"
        self.name = "British School Manila"
        self.short_name = "BSM"
        self.session_manager = SessionManager()
    
    async def scrape_tuition_fees(self):
        """Scrape tuition fee information from BSM website"""
        logger.info(f"Scraping tuition fees for {self.name}")
        
        return {
            "status": "skipped",
            "message": "Tuition fees scraping is skipped for this school because it is not available on the website.",
        }
    
    async def scrape_curriculum(self):
        """Scrape curriculum information from BSM website"""
        logger.info(f"Scraping curriculum for {self.name}")
        
        try:
            url = f"{self.base_url}/academics/the-key-stages"
            
            # Use sessuion manager
            response = await self.session_manager.get(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the tabs navigation to get all key stages
            curriculum_data = []
            
            # Find the accordion container that holds all the key stages
            accordion_container = soup.select_one("div.fsElement.fsPanelGroup.fsAccordion")
            
            if not accordion_container:
                logger.warning(f"Curriculum accordion container not found on {url}")
                return {"status": "error", "message": "Curriculum information not found"}
            
            # Get all the key stage panels
            panels = accordion_container.select("section.fsElement.fsPanel")
            
            for panel in panels:
                # Get the key stage title
                title_elem = panel.select_one("h2.fsElementTitle a")
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                
                # Get the panel content
                content_elem = panel.select_one("div.fsElementContent div.fsElementContent")
                if not content_elem:
                    continue
                
                # Extract structured data
                paragraphs = content_elem.find_all('p')
                
                # First paragraph often contains age range information
                age_range = ""
                description = ""
                
                if paragraphs:
                    # Try to extract age range from first paragraph
                    first_p = paragraphs[0].text.strip()
                    age_match = re.search(r'for ages (\d+ to \d+)', first_p)
                    if age_match:
                        age_range = age_match.group(1)
                    
                    # Combine the rest of the paragraphs for description
                    # Skip image paragraphs (those with only <br> or empty)
                    description_paragraphs = []
                    for p in paragraphs:
                        p_text = p.text.strip()
                        if p_text and p_text != "<br>":
                            # Remove the "KS#" anchors that might appear in the text
                            p_text = re.sub(r'<a\s+id="[^"]+"\s+name="[^"]+"></a>', '', p_text)
                            description_paragraphs.append(p_text)
                    
                    if description_paragraphs:
                        description = " ".join(description_paragraphs)
                
                # Extract panel ID to create a direct link
                panel_id = panel.get('id', '')
                link = f"{url}#{panel_id}" if panel_id else url
                
                curriculum_data.append({
                    "name": title,
                    "age_range": age_range,
                    "description": description,
                    "link": link
                })
            
            return {
                "status": "success",
                "data": curriculum_data
            }
            
        except Exception as e:
            logger.error(f"Error scraping curriculum for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape_enrollment_process(self):
        """Scrape enrollment process and requirements information from BSM website"""
        logger.info(f"Scraping enrollment process and requirements for {self.name}")
        
        try:
            url = f"{self.base_url}/admissions/how-to-apply"
            
            # Use Playwright to handle JavaScript loading
            response = await self.session_manager.get(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the tabs navigation to get all application steps
            tabs_nav = soup.select_one("ul.fsTabsNav")
            
            if not tabs_nav:
                logger.warning(f"Application steps tabs not found on {url}")
                return {"status": "error", "message": "Enrollment process information not found"}
            
            # Extract application process steps
            application_steps = []
            
            # Extract application requirements
            application_requirements = []
            
            # Extract contact information
            contact_email = ""
            
            # Process tabs and panels
            panels = soup.select("section.fsElement.fsPanel")
            
            for i, panel in enumerate(panels):
                # Get the step title
                title_elem = panel.select_one("h2.fsElementTitle a")
                if not title_elem:
                    continue
                
                # Extract the step number from the title or use the loop index
                step_number = i + 1  # Default to index
                number_span = panel.select_one("h2.fsElementTitle span.accordion-number")
                if number_span:
                    try:
                        step_number = int(number_span.text.strip())
                    except ValueError:
                        pass  # Use the default index number
                
                # Get the title text without the number
                title = title_elem.text.strip()
                
                # Get the panel content
                content_div = panel.select_one("div.fsElementContent")
                if not content_div:
                    continue
                
                # Get the inner content section if it exists
                inner_section = content_div.select_one("section.fsElement.fsContent")
                
                description = ""
                
                # If inner section exists, get the content
                if inner_section:
                    inner_content = inner_section.select_one("div.fsElementContent")
                    if inner_content:
                        # Extract the description text from paragraphs
                        paragraphs = inner_content.select("p")
                        description_parts = []
                        
                        for p in paragraphs:
                            p_text = p.text.strip()
                            if p_text and not p_text.startswith("ENQUIRE TODAY"):
                                description_parts.append(p_text)
                        
                        if description_parts:
                            description = " ".join(description_parts)
                
                # Look for any email in the content
                if not contact_email:
                    email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', description)
                    if email_matches:
                        contact_email = email_matches[0]
                
                # Check if this panel contains admission requirements
                if "Requirements" in title or "Requirements" in description:
                    requirement_list = content_div.select("ul li")
                    for item in requirement_list:
                        requirement_text = item.text.strip()
                        if requirement_text:
                            application_requirements.append(requirement_text)
                
                # Add this step to the application steps
                application_steps.append({
                    "step_number": step_number,
                    "title": title,
                    "description": description
                })
            
            # Sort application steps by step number
            application_steps.sort(key=lambda x: x["step_number"])
            
            return {
                "status": "success",
                "data": {
                    "application_process": application_steps,
                    "requirements": application_requirements,
                    "contact_email": contact_email
                }
            }
            
        except Exception as e:
            logger.error(f"Error scraping enrollment process for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape_scholarships(self):
        """Scrape scholarship information from BSM website"""
        logger.info(f"Scraping scholarship information for {self.name}")
        
        # Placeholder for implementation
        return {
            "status": "not_implemented",
            "message": "No relevant scholarships information found"
        }
    
    async def scrape_contact_info(self):
        """Scrape contact information from BSM website"""
        logger.info(f"Scraping contact information for {self.name}")
        
        try:
            url = f"{self.base_url}/contact"
            
            # Use session manager to get the page
            response = await self.session_manager.get(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize contact information
            contact_person = "N/A"
            contact_number = ""
            contact_email = "N/A"
            
            # Find the contact information section
            contact_section = soup.select_one("div.fsElementHeaderContent")
            
            if contact_section:
                # Extract all text content
                all_text = contact_section.get_text()
                
                # Use regex to find phone number
                phone_match = re.search(r'\+\d+\s*\(\d+\)\s*[\d\s]+', all_text)
                if phone_match:
                    contact_number = phone_match.group(0).strip()
                
                # Look for email in the entire content
                email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', all_text)
                if email_matches:
                    contact_email = email_matches[0]
            
            return {
                "status": "success",
                "data": {
                    "contact_person": contact_person,
                    "phone": contact_number,
                    "email": contact_email,
                }
            }
            
        except Exception as e:
            logger.error(f"Error scraping contact information for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape(self, school_data=None):
        """Main method to scrape all data from BSM website"""
        logger.info(f"Starting scraping process for {self.name}")
        
        try:
            tuition_result = await self.scrape_tuition_fees()
            curriculum_result = await self.scrape_curriculum()
            enrollment_result = await self.scrape_enrollment_process()
            scholarship_result = await self.scrape_scholarships()
            contact_result = await self.scrape_contact_info()
            
            results = {
                "name": self.name,
                "tuition_fees": tuition_result,
                "curriculum": curriculum_result,
                "enrollment_process": enrollment_result,
                "scholarships": scholarship_result,
                "contact_info": contact_result
            }
            
            # Close the Playwright browser when done
            await close_playwright()
            
            return results
        except Exception as e:
            logger.error(f"Error in main scrape method: {str(e)}")
            # Make sure to close Playwright even on errors
            await close_playwright()
            raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # For testing purposes
    async def main():
        scraper = BSMScraper()
        result = await scraper.scrape()
        print(json.dumps(result, indent=4))
    
    asyncio.run(main())