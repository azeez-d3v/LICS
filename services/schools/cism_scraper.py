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

class CISMScraper(BaseScraper):
    """Scraper for Chinese International School Manila website"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://cismanila.org"
        self.name = "Chinese International School Manila"
        self.short_name = "CISM"
        self.session_manager = SessionManager()
    
    async def scrape_tuition_fees(self):
        """Scrape tuition fee information from CISM website"""
        logger.info(f"Scraping tuition fees for {self.name}")
        
        try:
            url = f"{self.base_url}/admissions/fee-structure"
            
            # Use Playwright to handle JavaScript loading
            html_content = await get_with_playwright(
                url, 
                wait_for_selector="div.table_content table, table", 
                wait_time=10000
            )
            
            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try to find the table with specific selectors based on the actual structure
            table = soup.select_one("div.accordion_container div.item_content div.table_content table")
            
            # If not found, try more general selectors
            if not table:
                table = soup.select_one("div.table_content table")
            
            if not table:
                table = soup.find('table')
            
            if not table:
                logger.warning(f"Tuition fee table not found on {url}")
                return {"status": "error", "message": "Tuition fee table not found"}
            
            tuition_data = {}
            
            # Extract data from table rows
            rows = table.find_all('tr')
            
            # Skip header row
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:  # Make sure we have enough cells
                    grade_level = cells[0].text.strip()
                    annual = cells[1].text.strip()
                    semestral = cells[2].text.strip()
                    quarterly = cells[3].text.strip()
                    
                    if grade_level:  # Only add if grade level is not empty
                        tuition_data[grade_level] = {
                            "Annual": annual,
                            "Semestral": semestral,
                            "Quarterly": quarterly
                        }
            
            return {
                "status": "success",
                "data": tuition_data
            }
            
        except Exception as e:
            logger.error(f"Error scraping tuition fees for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape_curriculum(self):
        """Scrape curriculum information from CISM website"""
        logger.info(f"Scraping curriculum for {self.name}")
        
        try:
            url = f"{self.base_url}/learning/curriculum/"
            
            # Use Playwright to handle JavaScript loading
            html_content = await get_with_playwright(
                url, 
                wait_for_selector="div.curriculum_container, div.__uRxj8vJrdWNc", 
                wait_time=10000
            )
            
            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try multiple selectors based on the provided HTML
            curriculum_containers = soup.select("div.curriculum_container div.__uRxj8vJrdWNc")
            
            # If not found with specific selector, try more general approaches
            if not curriculum_containers:
                curriculum_containers = soup.select("div.container.curriculum_container div.__uRxj8vJrdWNc")
            
            if not curriculum_containers:
                curriculum_containers = soup.select("div.__HVzJCy6CJGoG > div.__uRxj8vJrdWNc")
            
            if not curriculum_containers:
                # Try to find any curriculum blocks with a more general approach
                curriculum_containers = soup.select("div.curriculum_container > div > div")
            
            if not curriculum_containers:
                logger.warning(f"Curriculum containers not found on {url}")
                return {"status": "error", "message": "Curriculum information not found"}
            
            curriculum_data = []
            
            for container in curriculum_containers:
                # Try multiple selector patterns for the curriculum name
                name_elem = (container.select_one("p.__sqJM8jSflkpR") or 
                            container.select_one("div.__QY\\+N\\+pXIYT1I > p:first-child") or
                            container.select_one("div p:first-child"))
                
                # Try multiple selector patterns for the age range
                age_elem = (container.select_one("p.__1TExyx75Kbxq > p") or 
                           container.select_one("p.__1TExyx75Kbxq") or 
                           container.select_one("div > p:nth-child(2) > p"))
                
                # Try to find the link
                link_elem = container.select_one("a")
                
                if name_elem:
                    name = name_elem.text.strip()
                    
                    # Handle age range
                    age_range = ""
                    if age_elem:
                        age_range = age_elem.text.strip()
                    
                    # Handle link
                    link = ""
                    if link_elem:
                        link = link_elem.get('href', '')
                        if link.startswith('/'):
                            link = self.base_url + link
                    
                    curriculum_data.append({
                        "name": name,
                        "age_range": age_range,
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
        """Scrape enrollment process and requirements information from CISM website"""
        logger.info(f"Scraping enrollment process and requirements for {self.name}")
        
        try:
            url = f"{self.base_url}/admissions/admissions-policy"
            
            # Use Playwright to handle JavaScript loading
            html_content = await get_with_playwright(
                url, 
                wait_for_selector="div.accordion_container", 
                wait_time=10000
            )
            
            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the accordion containers for admissions policy and requirements
            accordion_containers = soup.select("div.accordion_container div.item")
            
            if not accordion_containers:
                logger.warning(f"Enrollment process containers not found on {url}")
                return {"status": "error", "message": "Enrollment process information not found"}
            
            enrollment_data = {
                "policy": [],
                "requirements": [],
                "contact_email": ""
            }
            
            for container in accordion_containers:
                # Get the title of each accordion section
                title_elem = container.select_one("div.item_header p.title")
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                
                # Get the content of each accordion section
                content = container.select_one("div.item_content")
                if not content:
                    continue
                
                # Extract policy points (for Admissions Policy section)
                if "Policy" in title:
                    policy_items = content.select("ul li")
                    for item in policy_items:
                        enrollment_data["policy"].append(item.text.strip())
                
                # Extract requirements (for Admissions Requirements section)
                elif "Requirements" in title:
                    # Look for contact email in the requirements section
                    email_match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', content.text)
                    if email_match:
                        enrollment_data["contact_email"] = email_match.group(0)
                    
                    # Extract list items
                    requirement_items = content.select("ul li")
                    for item in requirement_items:
                        enrollment_data["requirements"].append(item.text.strip())
            
            return {
                "status": "success",
                "data": enrollment_data
            }
            
        except Exception as e:
            logger.error(f"Error scraping enrollment process for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape_scholarships(self):
        """Scrape scholarship information from CISM website"""
        logger.info(f"Scraping scholarship information for {self.name}")
        
        try:
            url = f"{self.base_url}/scholarships"
            
            # Use Playwright to handle JavaScript loading
            html_content = await get_with_playwright(
                url, 
                wait_for_selector="div.explore_cism_container, div.__xTj7CWA-ABoj", 
                wait_time=10000
            )
            
            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get the introduction text if available
            intro_heading = soup.select_one("div.explore_cism_container h3.heading_text")
            intro_text = soup.select_one("div.explore_cism_container p.subheading_text")
            
            introduction = ""
            if intro_heading and intro_text:
                introduction = f"{intro_heading.text.strip()}: {intro_text.text.strip()}"
            
            # Find scholarship containers
            scholarship_containers = soup.select("div.__xTj7CWA-ABoj")
            
            if not scholarship_containers:
                logger.warning(f"Scholarship containers not found on {url}")
                return {"status": "error", "message": "Scholarship information not found"}
            
            scholarship_data = []
            
            for container in scholarship_containers:
                # Get scholarship title
                title_elem = container.select_one("h2.__s6AZ0GO3Zktp")
                
                # Get scholarship description
                desc_elem = container.select_one("div.__hc4Qy2\\+wXZ2b")
                
                # Get link to more information
                link_elem = container.select_one("a")
                
                if title_elem:
                    title = title_elem.text.strip()
                    
                    # Handle description
                    description = ""
                    if desc_elem:
                        description = desc_elem.text.strip()
                    
                    # Handle link
                    link = ""
                    if link_elem:
                        link = link_elem.get('href', '')
                        if link.startswith('/'):
                            link = self.base_url + link
                    
                    scholarship_data.append({
                        "name": title,
                        "description": description,
                        "link": link
                    })
            
            return {
                "status": "success",
                "introduction": introduction,
                "data": scholarship_data
            }
            
        except Exception as e:
            logger.error(f"Error scraping scholarship information for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape_contact_info(self):
        """Scrape contact information from CISM website"""
        logger.info(f"Scraping contact information for {self.name}")
        
        try:
            url = f"{self.base_url}/contact-us"
            
            # Use Playwright to handle JavaScript loading
            html_content = await get_with_playwright(
                url, 
                wait_for_selector="div.address_phone_container", 
                wait_time=10000
            )
            
            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            contact_data = {
                "email": "N/A",
                "phone_numbers": [],
                "contact_person": "N/A"
            }
            
            # Try to find email addresses on the page
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            email_matches = re.findall(email_pattern, html_content)
            
            if email_matches:
                # Use the first email found
                contact_data["email"] = email_matches[0]
            
            # Find phone numbers in the container
            phone_containers = soup.select("div.address_phone_container div.text_container")
            
            for container in phone_containers:
                # Check if this is a phone container (has SMS link or phone icon)
                if container.select_one("a[href^='sms:']") or container.select_one("img[src*='message_logo']"):
                    phone_text = container.select_one("span.text")
                    if phone_text:
                        contact_data["phone_numbers"].append(phone_text.text.strip())
            
            return {
                "status": "success",
                "data": contact_data
            }
            
        except Exception as e:
            logger.error(f"Error scraping contact information for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape(self, school_data=None):
        """Main method to scrape all data from CISM website"""
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
        scraper = CISMScraper()
        result = await scraper.scrape()
        print(json.dumps(result, indent=4))
    
    asyncio.run(main())