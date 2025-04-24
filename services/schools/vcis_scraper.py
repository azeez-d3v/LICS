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

class VCISScraper(BaseScraper):
    """Scraper for Victory Christian International School website"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://vcis.edu.ph"
        self.name = "Victory Christian International School"
        self.short_name = "VCIS"
        self.session_manager = SessionManager()
    
    async def scrape_tuition_fees(self):
        """Scrape tuition fee information from VCIS website"""
        logger.info(f"Scraping tuition fees for {self.name}")
        
        return {
            "status": "skipped",
            "message": "Tuition fees scraping is skipped for this school because it is not available on the website.",
        }
    
    async def scrape_curriculum(self):
        """Scrape curriculum information from VCIS website"""
        logger.info(f"Scraping curriculum for {self.name}")
        
        try:
            url = f"{self.base_url}/index.php/our-programs/"
            
            # Use session manager
            response = await self.session_manager.get(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize curriculum data structure
            curriculum_data = []
            
            # Find program sections - Look for heading elements that contain program names
            program_headings = soup.select("h2.elementor-heading-title")
            
            for heading in program_headings:
                # Get program name from the heading
                program_name = heading.get_text(strip=True)
                
                # Skip if it's not a program heading (some headings might be for other sections)
                if not program_name or len(program_name) < 3:
                    continue
                
                # Find the parent column that contains this heading and its description
                parent_column = heading.find_parent("div", class_="elementor-column")
                if not parent_column:
                    continue
                
                # Find the program description in the same column
                description_element = parent_column.select_one("div.elementor-widget-text-editor p")
                description = ""
                if description_element:
                    description = description_element.get_text(strip=True)
                
                # Create program data structure
                program_data = {
                    "name": program_name,
                    "description": description
                }
                
                # Add additional information like links if available
                links = parent_column.select("a")
                if links:
                    program_links = []
                    for link in links:
                        link_url = link.get('href', '')
                        link_text = link.get_text(strip=True)
                        if link_url and link_text:
                            program_links.append({
                                "text": link_text,
                                "url": link_url
                            })
                    
                    if program_links:
                        program_data["links"] = program_links
                
                # Add the program to the curriculum data
                curriculum_data.append(program_data)
                logger.info(f"Added program: {program_name}")
            
            # Check if we found any programs
            if not curriculum_data:
                # Fallback approach - look for specific program sections we know exist
                # This is based on the HTML structure provided
                online_program = {
                    "name": "VCIS Online",
                    "description": ""
                }
                
                hybrid_program = {
                    "name": "Integrated Hybrid",
                    "description": ""
                }
                
                # Find descriptions using more specific selectors
                online_desc = soup.select_one("div.elementor-element-edc767f p")
                if online_desc:
                    online_program["description"] = online_desc.get_text(strip=True)
                
                hybrid_desc = soup.select_one("div.elementor-element-58b0756 p")
                if hybrid_desc:
                    hybrid_program["description"] = hybrid_desc.get_text(strip=True)
                
                if online_program["description"]:
                    curriculum_data.append(online_program)
                    logger.info(f"Added program using fallback method: {online_program['name']}")
                
                if hybrid_program["description"]:
                    curriculum_data.append(hybrid_program)
                    logger.info(f"Added program using fallback method: {hybrid_program['name']}")
            
            # If we still didn't find any programs, try an even more general approach
            if not curriculum_data:
                # Look for all sections that might contain program information
                sections = soup.select("section.elementor-section")
                
                for i, section in enumerate(sections):
                    heading = section.select_one("h2.elementor-heading-title")
                    if not heading:
                        continue
                    
                    program_name = heading.get_text(strip=True)
                    
                    # Find paragraphs that might contain descriptions
                    paragraphs = section.select("p")
                    description = " ".join([p.get_text(strip=True) for p in paragraphs])
                    
                    if program_name and description:
                        program_data = {
                            "name": program_name,
                            "description": description
                        }
                        
                        curriculum_data.append(program_data)
                        logger.info(f"Added program using general section method: {program_name}")
            
            # Return the results
            if curriculum_data:
                return {
                    "status": "success",
                    "data": curriculum_data
                }
            else:
                return {
                    "status": "warning",
                    "message": "No curriculum information found",
                    "data": []
                }
            
        except Exception as e:
            logger.error(f"Error scraping curriculum for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape_enrollment_process(self):
        """Scrape enrollment process and requirements information from VCIS website"""
        logger.info(f"Scraping enrollment process and requirements for {self.name}")
        
        try:
            # Implement enrollment process scraping logic here
            # ...
            
            return {
                "status": "not_implemented",
                "message": "Enrollment process scraping is not yet implemented for this school."
            }
            
        except Exception as e:
            logger.error(f"Error scraping enrollment process for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape_scholarships(self):
        """Scrape scholarship information from VCIS website"""
        logger.info(f"Scraping scholarship information for {self.name}")
        
        # Implement scholarship scraping logic here
        return {
            "status": "not_implemented",
            "message": "No relevant scholarships information found"
        }
    
    async def scrape_contact_info(self):
        """Scrape contact information from VCIS website"""
        logger.info(f"Scraping contact information for {self.name}")
        
        try:
            url = f"{self.base_url}/index.php/contact-us/"
            
            # Use session manager
            response = await self.session_manager.get(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize contact data structure with only the requested fields
            contact_data = {
                "contact_person": "N/A",
                "phone": "N/A",
                "email": "N/A"
            }
            
            # Find icon boxes that contain contact information
            icon_boxes = soup.select("div.elementor-icon-box-wrapper")
            
            for box in icon_boxes:
                # Get the icon element to determine what type of information this is
                icon = box.select_one("i.fas, i.far")
                description = box.select_one("p.elementor-icon-box-description")
                
                if not icon or not description:
                    continue
                    
                # Get the text content
                info_text = description.get_text(strip=True)
                icon_class = icon.get("class")
                
                # Determine the type of information based on the icon and store only phone and email
                if icon and icon_class:
                    if "fa-phone-alt" in icon_class and info_text:
                        contact_data["phone"] = info_text
                        logger.info(f"Found phone: {info_text}")
                    elif "fa-envelope" in icon_class and info_text:
                        # Handle multiple email addresses separated by pipes
                        emails = [email.strip() for email in info_text.replace("|", ",").split(",")]
                        # Filter out empty strings
                        emails = [email for email in emails if email]
                        
                        if emails:
                            # Use the primary email as the main contact
                            contact_data["email"] = emails[0]
                            logger.info(f"Found primary email: {emails[0]}")
            
            # Check if we found the required contact information
            if contact_data["phone"] != "N/A" or contact_data["email"] != "N/A":
                return {
                    "status": "success",
                    "data": contact_data
                }
            else:
                return {
                    "status": "warning",
                    "message": "Limited contact information found",
                    "data": contact_data
                }
            
        except Exception as e:
            logger.error(f"Error scraping contact information for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape(self, school_data=None):
        """Main method to scrape all data from VCIS website"""
        logger.info(f"Starting scraping process for {self.name}")
        
        try:
            # Get fee information
            tuition_result = await self.scrape_tuition_fees()
            
            # Get curriculum data
            curriculum_result = await self.scrape_curriculum()
            
            # Continue with other scraping methods
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
        scraper = VCISScraper()
        result = await scraper.scrape()
        print(json.dumps(result, indent=4))
    
    asyncio.run(main())