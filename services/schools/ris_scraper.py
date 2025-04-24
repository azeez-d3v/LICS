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

class RISScraper(BaseScraper):
    """Scraper for Reedley International School website"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.reedleyschool.edu.ph"
        self.name = "Reedley International School"
        self.short_name = "RIS"
        self.session_manager = SessionManager()
    
    async def scrape_tuition_fees(self):
        """Scrape tuition fee information from BSM website"""
        logger.info(f"Scraping tuition fees for {self.name}")
        
        return {
            "status": "skipped",
            "message": "Tuition fees scraping is skipped for this school because it is not available on the website.",
        }
    
    async def scrape_curriculum(self):
        """Scrape curriculum information from RIS website"""
        logger.info(f"Scraping curriculum for {self.name}")
        
        try:
            url = f"{self.base_url}/acad-programs/"
            
            # Use session manager to get the page content
            response = await self.session_manager.get(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize curriculum data structure
            curriculum_data = {
                "overview": "",
                "kindergarten": {},
                "basic_education": {},
                "advanced_placement": {},
                "senior_high_school": {}
            }
            
            # Get Kindergarten section information
            kinder_section = soup.select_one("div.kinderGartenRow")
            if kinder_section:
                kinder_title = kinder_section.find('h2')
                kinder_desc = kinder_section.find('p')
                
                if kinder_title and kinder_desc:
                    curriculum_data["kindergarten"] = {
                        "title": kinder_title.get_text(strip=True),
                        "description": kinder_desc.get_text(strip=True)
                    }
                    logger.info(f"Found kindergarten program: {kinder_title.get_text(strip=True)}")
            
            # Get Basic Education Curriculum sections
            basic_edu_section = soup.select_one("div.basicEducationRow")
            if basic_edu_section:
                basic_edu_title = basic_edu_section.find('h2')
                if basic_edu_title:
                    curriculum_data["basic_education"]["title"] = basic_edu_title.get_text(strip=True)
                    logger.info(f"Found basic education program: {basic_edu_title.get_text(strip=True)}")
                
                # Process each subject accordion
                subject_cards = basic_edu_section.select("#accordion .card")
                subjects = {}
                
                for card in subject_cards:
                    header = card.select_one(".card-header h3 button span")
                    body = card.select_one(".card-body")
                    
                    if header and body:
                        subject_name = header.get_text(strip=True)
                        subject_desc = body.get_text(strip=True)
                        
                        # Clean up description - replace multiple spaces with single space
                        subject_desc = re.sub(r'\s+', ' ', subject_desc).strip()
                        
                        subjects[subject_name] = subject_desc
                        logger.info(f"Found subject: {subject_name}")
                
                curriculum_data["basic_education"]["subjects"] = subjects
            
            # Get AP Program information
            ap_section = soup.select_one("div.juniorProgramDiv")
            if ap_section:
                ap_title = ap_section.find('h2')
                ap_desc = ap_section.find('p')
                
                if ap_title and ap_desc:
                    curriculum_data["advanced_placement"] = {
                        "title": ap_title.get_text(strip=True),
                        "description": ap_desc.get_text(strip=True)
                    }
                    logger.info(f"Found AP program: {ap_title.get_text(strip=True)}")
            
            # Get Senior High School Curriculum
            shs_section = soup.select_one("div.seniorHsCurriculum")
            if shs_section:
                shs_title = shs_section.find('h2')
                if shs_title:
                    curriculum_data["senior_high_school"]["title"] = shs_title.get_text(strip=True)
                    logger.info(f"Found senior high school program: {shs_title.get_text(strip=True)}")
                
                # Process each strand accordion
                strand_cards = shs_section.select("#accordion2 .card")
                strands = {}
                
                for card in strand_cards:
                    header = card.select_one(".card-header h3 button span")
                    body = card.select_one(".card-body")
                    
                    if header and body:
                        strand_name = header.get_text(strip=True)
                        strand_desc = body.get_text(strip=True)
                        
                        # Clean up whitespace
                        strand_desc = re.sub(r'\s+', ' ', strand_desc).strip()
                        
                        # Check if there's a list in the description
                        list_items = []
                        list_ol = card.select_one(".card-body ol")
                        
                        if list_ol:
                            li_items = list_ol.select("li")
                            for li in li_items:
                                list_items.append(li.get_text(strip=True))
                            
                            # Remove the list from the description to avoid duplication
                            strand_desc = strand_desc.split('1.')[0].strip()
                        
                        strand_data = {
                            "description": strand_desc
                        }
                        
                        if list_items:
                            strand_data["courses"] = list_items
                        
                        strands[strand_name] = strand_data
                        logger.info(f"Found strand: {strand_name}")
                
                curriculum_data["senior_high_school"]["strands"] = strands
            
            # Extract grade levels from sidebar
            sidebar = soup.select_one("div.acadProgramSidebar")
            if sidebar:
                grade_levels = []
                grade_items = sidebar.select("ul li")
                
                for item in grade_items:
                    grade_name = item.get_text(strip=True)
                    grade_levels.append(grade_name)
                
                curriculum_data["grade_levels"] = grade_levels
                logger.info(f"Found {len(grade_levels)} grade levels")
            
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
        """Scrape enrollment process and requirements information from RIS website"""
        logger.info(f"Scraping enrollment process and requirements for {self.name}")
        
        try:
            url = f"{self.base_url}/apply/#procedureId"
            
            # Use session manager
            response = await self.session_manager.get(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize enrollment data structure
            enrollment_data = {
                "overview": "",
                "steps": [],
                "requirements": [],
                "contact_info": {}
            }
            
            # Extract the steps of the admissions procedure
            step_sections = soup.select("div.admissionRequirements_Left")
            
            for i, section in enumerate(step_sections):
                step_number = section.select_one("h3")
                step_title = section.select_one("h2")
                
                if step_number and step_title:
                    step_num = re.search(r'Step\s+(\d+)', step_number.get_text(strip=True))
                    step_num = int(step_num.group(1)) if step_num else i + 1
                    
                    step_data = {
                        "step": step_num,
                        "title": step_title.get_text(strip=True)
                    }
                    
                    # For Steps 2 and 3, look for span elements with descriptions
                    if step_num in [2, 3]:
                        step_description = section.select_one("span")
                        if step_description:
                            # Get the text and clean any nested tags
                            desc_text = step_description.get_text(strip=True)
                            step_data["description"] = desc_text
                            logger.info(f"Found description for Step {step_num}: {desc_text}")
                    
                    # Extract links for Step 1 (forms to download)
                    if step_num == 1:
                        form_links = section.select("ul li a")
                        if form_links:
                            forms = []
                            for link in form_links:
                                form_data = {
                                    "name": link.get_text(strip=True),
                                    "url": link.get('href', '')
                                }
                                forms.append(form_data)
                            
                            if forms:
                                step_data["forms"] = forms
                        
                        # Get description from paragraph for Step 1
                        step1_desc = section.select_one("p.border-bott-p")
                        if step1_desc:
                            step_data["description"] = step1_desc.get_text(strip=True)
                    
                    enrollment_data["steps"].append(step_data)
                    logger.info(f"Added step {step_num}: {step_title.get_text(strip=True)}")
            
            # Extract the requirements
            requirements_list = soup.select_one("div.admissionRequirements_Right ul")
            if requirements_list:
                requirements = []
                for item in requirements_list.select("li"):
                    req_title = item.select_one("h3")
                    req_desc = item.select_one("p")
                    
                    if req_title:
                        req_data = {
                            "title": req_title.get_text(strip=True),
                            "description": req_desc.get_text(strip=True) if req_desc else ""
                        }
                        
                        # Clean up the title to remove the numbering prefix
                        if "—" in req_data["title"]:
                            req_data["title"] = req_data["title"].split("—", 1)[1].strip()
                        
                        requirements.append(req_data)
                        logger.info(f"Added requirement: {req_data['title']}")
                
                enrollment_data["requirements"] = requirements
            
            # Extract contact information
            contact_section = soup.select_one("div.admissionProcessingCtaLeft")
            contact_links = soup.select("div.admissionProcessingCtaRight a")
            
            if contact_section:
                contact_text = contact_section.get_text(strip=True)
                enrollment_data["contact_info"]["message"] = contact_text
            
            if contact_links:
                for link in contact_links:
                    link_text = link.get_text(strip=True).lower()
                    link_href = link.get('href', '')
                    
                    if "call" in link_text and "tel:" in link_href:
                        enrollment_data["contact_info"]["phone"] = link_href.replace("tel:", "")
                    
                    if "email" in link_text and "mailto:" in link_href:
                        enrollment_data["contact_info"]["email"] = link_href.replace("mailto:", "")
            
            # Add overall process overview
            top_section = soup.select_one("div.admissionRequirements_Left h4")
            if top_section:
                enrollment_data["overview"] = top_section.get_text(strip=True)
            
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
        """Scrape scholarship information from RIS website"""
        logger.info(f"Scraping scholarship information for {self.name}")
        
        return {
            "status": "skipped",
            "message": "Tuition fees scraping is skipped for this school because it is not available on the website.",
        }
    
    async def scrape_contact_info(self):
        """Scrape essential contact information from RIS website"""
        logger.info(f"Scraping contact information for {self.name}")
        
        try:
            url = f"{self.base_url}/contact/"
            
            # Use session manager
            response = await self.session_manager.get(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize contact data structure
            contact_data = {
                "general_inquiries": {},
                "departments": {}
            }
            
            # Extract general inquiries info
            gen_inquiries = soup.select_one("div.genInquiries")
            if gen_inquiries:
                inquiries_items = gen_inquiries.select("ul li")
                
                if len(inquiries_items) >= 3:
                    # First item is the title
                    contact_data["general_inquiries"]["title"] = inquiries_items[0].get_text(strip=True)
                    
                    # Second item contains phone numbers
                    phone_links = inquiries_items[1].select("a")
                    if phone_links:
                        phone_numbers = [link.get_text(strip=True) for link in phone_links]
                        contact_data["general_inquiries"]["phone"] = phone_numbers
                    
                    # Third item is email
                    email_link = inquiries_items[2].select_one("a")
                    if email_link:
                        contact_data["general_inquiries"]["email"] = email_link.get_text(strip=True)
            
            # Extract department-specific contact details
            department_cards = soup.select("div.directoryCard")
            
            for card in department_cards:
                # Get department name
                dept_name = card.select_one("h3")
                
                if dept_name:
                    dept_name = dept_name.get_text(strip=True)
                    
                    # Initialize department data
                    if dept_name not in contact_data["departments"]:
                        contact_data["departments"][dept_name] = {
                            "phone": [],
                            "email": []
                        }
                    
                    # Extract phone numbers and emails
                    links = card.select("a")
                    for link in links:
                        link_text = link.get_text(strip=True)
                        link_href = link.get('href', '')
                        
                        if link_href.startswith("tel:"):
                            contact_data["departments"][dept_name]["phone"].append(link_text)
                        elif link_href.startswith("mailto:"):
                            contact_data["departments"][dept_name]["email"].append(link_text)
                else:
                    # Handle department cards without h3 headers (like Grade School)
                    emails = []
                    phones = []
                    
                    links = card.select("a")
                    for link in links:
                        link_text = link.get_text(strip=True)
                        link_href = link.get('href', '')
                        
                        if link_href.startswith("tel:"):
                            phones.append(link_text)
                        elif link_href.startswith("mailto:"):
                            emails.append(link_text)
                    
                    # Determine department name from emails or content
                    dept_name = "Other"
                    
                    # Try to extract dept name from the first phone entry
                    if phones and ":" in phones[0]:
                        parts = phones[0].split(":", 1)
                        dept_name = parts[0].strip()
                        phones[0] = parts[1].strip()
                    
                    # Add to departments
                    if dept_name not in contact_data["departments"]:
                        contact_data["departments"][dept_name] = {
                            "phone": phones,
                            "email": emails
                        }
                    else:
                        # Append to existing department
                        contact_data["departments"][dept_name]["phone"].extend(phones)
                        contact_data["departments"][dept_name]["email"].extend(emails)
            
            # Special handling for the IT department which has a paragraph
            it_dept_card = soup.select_one("div.directoryCard p")
            if it_dept_card:
                note = it_dept_card.get_text(strip=True)
                if "IT Dept." in contact_data["departments"]:
                    contact_data["departments"]["IT Dept."]["note"] = note
            
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
        """Main method to scrape all data from RIS website"""
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
                "tuition_fees": tuition_result["data"] if tuition_result["status"] == "success" else tuition_result,
                "curriculum": curriculum_result["data"] if curriculum_result["status"] == "success" else curriculum_result,
                "enrollment_process": enrollment_result["data"] if enrollment_result["status"] == "success" else enrollment_result,
                "scholarships": scholarship_result["data"] if scholarship_result["status"] == "success" else scholarship_result,
                "contact_info": contact_result["data"] if contact_result["status"] == "success" else contact_result
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
        scraper = RISScraper()
        result = await scraper.scrape()
        print(json.dumps(result, indent=4))
    
    asyncio.run(main())