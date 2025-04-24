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

class FaithScraper(BaseScraper):
    """Scraper for Faith Academy website"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://faith.edu.ph"
        self.name = "Faith Academy"
        self.short_name = "Faith"
        self.session_manager = SessionManager()
    
    async def scrape_tuition_fees(self):
        """Scrape tuition fee information from Faith Academy website"""
        logger.info(f"Scraping tuition fees for {self.name}")
        
        try:
            url = f"{self.base_url}/admissions/finances/"
            
            # Use session manager
            response = await self.session_manager.get(url)
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize tuition data structure
            tuition_data = {
                "application_fees": {
                    "new_students": [],
                    "returning_students": []
                },
                "regular_tuition": {},
                "boarding_fees": {
                    "registration": {
                        "new_students": [],
                        "returning_students": []
                    },
                    "room_and_board": {}
                }
            }
            
            # 1. Parse Application Fee table
            application_fee_table = soup.select_one("div[data-id='a6b5222'] table.jet-table")
            if application_fee_table:
                rows = application_fee_table.select("tbody tr")
                for row in rows:
                    cells = row.select("td")
                    if len(cells) >= 4:
                        # New student data (first two cells)
                        new_time_period = cells[0].get_text(strip=True)
                        new_fee = cells[1].get_text(strip=True)
                        tuition_data["application_fees"]["new_students"].append({
                            "time_period": new_time_period,
                            "fee": new_fee
                        })
                        
                        # Returning student data (last two cells)
                        returning_time_period = cells[2].get_text(strip=True)
                        returning_fee = cells[3].get_text(strip=True)
                        tuition_data["application_fees"]["returning_students"].append({
                            "time_period": returning_time_period,
                            "fee": returning_fee
                        })
            
            # 2. Parse Regular Tuition table
            regular_tuition_table = soup.select_one("div[data-id='04facf5'] table.jet-table")
            if regular_tuition_table:
                rows = regular_tuition_table.select("tbody tr")
                # Skip the first row which has column labels for semester/annual
                for row in rows[1:]:
                    cells = row.select("td")
                    if len(cells) >= 5:
                        division = cells[0].get_text(strip=True)
                        if division:  # Sometimes there are empty cells
                            tuition_data["regular_tuition"][division] = {
                                "tuition": {
                                    "semester": cells[1].get_text(strip=True),
                                    "annual": cells[2].get_text(strip=True)
                                },
                                "facility_technology_fee": {
                                    "semester": cells[3].get_text(strip=True),
                                    "annual": cells[4].get_text(strip=True)
                                }
                            }
            
            # 3. Parse Boarding Registration Fee table
            boarding_reg_table = soup.select_one("div[data-id='df4d2f3'] table.jet-table")
            if boarding_reg_table:
                rows = boarding_reg_table.select("tbody tr")
                for row in rows:
                    cells = row.select("td")
                    if len(cells) >= 4:
                        # New student data (first two cells)
                        new_time_period = cells[0].get_text(strip=True)
                        if new_time_period.strip():  # Check if not empty
                            new_fee = cells[1].get_text(strip=True)
                            tuition_data["boarding_fees"]["registration"]["new_students"].append({
                                "time_period": new_time_period,
                                "fee": new_fee
                            })
                        
                        # Returning student data (last two cells)
                        returning_time_period = cells[2].get_text(strip=True)
                        if returning_time_period.strip():  # Check if not empty
                            returning_fee = cells[3].get_text(strip=True)
                            tuition_data["boarding_fees"]["registration"]["returning_students"].append({
                                "time_period": returning_time_period,
                                "fee": returning_fee
                            })
            
            # 4. Parse Room & Board table
            room_board_table = soup.select_one("div[data-id='dfc91b0'] table.jet-table")
            if room_board_table:
                rows = room_board_table.select("tbody tr")
                if rows:
                    cells = rows[0].select("td")
                    if len(cells) >= 2:
                        tuition_data["boarding_fees"]["room_and_board"] = {
                            "7_day_rate": cells[0].get_text(strip=True),
                            "5_day_rate": cells[1].get_text(strip=True)
                        }
            
            # 5. Try to extract additional information
            discounted_rates_section = soup.select_one("div[data-id='b5ebeb7']")
            discount_info = ""
            if discounted_rates_section:
                discount_info = discounted_rates_section.get_text(strip=True)
                # Add this to the tuition data
                tuition_data["discounted_rates_info"] = discount_info
            
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
        """Scrape curriculum information from Faith Academy website"""
        logger.info(f"Scraping curriculum for {self.name}")
        
        try:
            # Since the website doesn't provide clear structured information,
            # we'll hardcode the curriculum data based on the available information
            
            curriculum_data = [
                {
                    "name": "Elementary School",
                    "age_range": "Kindergarten - Grade 5",
                    "description": "Our ultimate hope is that each and every Elementary student gains a sense of who they are, believes that they have been created in God’s image, and that He made them to be learners - which means they can succeed in any area they choose..",
                    "link": f"{self.base_url}/school-life/"
                },
                {
                    "name": "Middle School",
                    "age_range": "Grades 6-8",
                    "description": "Middle School students at Faith Academy are exposed to active, purposeful engagement in the classroom, elective courses, extracurricular activities, and clubs. Our desire is for each student to experience deep academic, spiritual, and social development during their middle years with us.",
                    "link": f"{self.base_url}/school-life/"
                },
                {
                    "name": "High School",
                    "age_range": "Grades 9-12",
                    "description": "High School is the final stretch for students at Faith Academy - it is a time when the skills they have been collecting throughout their schooling are cultivated, challenged, and strengthened. We seek to prepare all students to move into the next stage of their lives knowing they are equipped and capable of success.",
                    "link": f"{self.base_url}/school-life/"
                },
                {
                    "name": "Athletics",
                    "description": "Over the years the Vanguards have cultivated a strong tradition of athletic excellence, because we believe that a well-rounded education extends outside the classroom to include the physical, mental and overall well-being of students.",
                    "link": f"{self.base_url}/school-life/"
                },
                {
                    "name": "Clubs & Student Life",
                    "description": "Clubs and student organizations allow students to lead their fellow students, plan fundraisers, coordinate volunteers, manage time, work with vendors or professionals outside of Faith Academy, travel together, and more. Clubs are guided by staff members who share their expertise and encourage students to grow in their interests, confidence, and friendships.",
                    "link": f"{self.base_url}/school-life/"
                },
                {
                    "name": "Fine Arts",
                    "description": "Fine arts are a strong part of our school’s identity and are celebrated throughout the year with on-campus performances and art shows. A range of courses and extracurricular opportunities invite students to explore and deepen talents in visual arts, instrumental music, theater, music theory and vocal music. Arts training begins during Elementary School and continues through High School.",
                    "link": f"{self.base_url}/school-life/"
                },
                {
                    "name": "Korean Studies",
                    "description": "FOur Korean Studies Program is led by Korean instructors and has been offered since 2004. This program was created to allow interested students the opportunity to study Korean language, history, and civics. As a large portion of our students are from Korea, this program allows young students to increase their Korean and English language proficiency, and helps older students who plan to return to Korea after high school with university entrance and transition.",
                    "link": f"{self.base_url}/school-life/"
                }
            ]
            
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
        """Scrape enrollment process and requirements information from Faith Academy website"""
        logger.info(f"Scraping enrollment process and requirements for {self.name}")
        
        try:
            url_apply = f"{self.base_url}/admissions/apply/"
            url_checklist = f"{self.base_url}/admissions/admissions-checklist/"
            
            # Get the application process page
            process_response = await self.session_manager.get(url_apply)
            process_soup = BeautifulSoup(process_response.text, 'html.parser')
            
            # Get the checklist page
            checklist_response = await self.session_manager.get(url_checklist)
            checklist_soup = BeautifulSoup(checklist_response.text, 'html.parser')
            
            # Initialize data structure
            enrollment_data = {
                "policy": [],
                "requirements": {
                    "general": [],
                    "homeschool": []
                },
                "contact_email": "registrar@faith.edu.ph"
            }
            
            # Extract the enrollment process steps
            timeline_items = process_soup.select(".pp-timeline-item")
            for item in timeline_items:
                # Get the step number
                step_number = item.select_one(".pp-timeline-marker").text.strip() if item.select_one(".pp-timeline-marker") else ""
                
                # Get the step title
                title_elem = item.select_one(".pp-timeline-card-title")
                title = title_elem.text.strip() if title_elem else ""
                
                # Get the step description
                content_elem = item.select_one(".pp-timeline-card-content")
                description = content_elem.text.strip() if content_elem else ""
                
                # Get links in the description
                links = []
                if content_elem:
                    link_elements = content_elem.select("a")
                    for link in link_elements:
                        link_url = link.get('href', '')
                        link_text = link.text.strip()
                        if link_url and link_text:
                            links.append({
                                "text": link_text,
                                "url": link_url
                            })
                
                # Add the step to the policy list
                enrollment_data["policy"].append({
                    "step": step_number,
                    "title": title,
                    "description": description,
                    "links": links
                })
            
            # Extract application requirements - general checklist
            general_checklist = checklist_soup.select("#input_16_1 .gchoice")
            for item in general_checklist:
                label_elem = item.select_one("label")
                if label_elem:
                    requirement_text = label_elem.get_text(strip=True)
                    
                    # Check if there's a link in the requirement
                    link_info = None
                    link_elem = label_elem.select_one("a")
                    if link_elem:
                        link_info = {
                            "text": link_elem.text.strip(),
                            "url": link_elem.get('href', '')
                        }
                    
                    # Add the requirement to the general requirements list
                    requirement_item = {
                        "text": requirement_text
                    }
                    
                    if link_info:
                        requirement_item["link"] = link_info
                    
                    enrollment_data["requirements"]["general"].append(requirement_item)
            
            # Extract homeschool-specific requirements
            homeschool_checklist = checklist_soup.select("#input_16_3 .gchoice")
            for item in homeschool_checklist:
                label_elem = item.select_one("label")
                if label_elem:
                    requirement_text = label_elem.get_text(strip=True)
                    enrollment_data["requirements"]["homeschool"].append({
                        "text": requirement_text
                    })
            
            # Flatten the requirements as per the expected structure
            flattened_requirements = []
            for req in enrollment_data["requirements"]["general"]:
                flattened_requirements.append(req)
            flattened_requirements.append({"category": "Homeschool Additional Requirements"})
            for req in enrollment_data["requirements"]["homeschool"]:
                flattened_requirements.append(req)
            
            return {
                "status": "success",
                "data": {
                    "policy": enrollment_data["policy"],
                    "requirements": flattened_requirements,
                    "contact_email": enrollment_data["contact_email"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error scraping enrollment process for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape_scholarships(self):
        """Scrape scholarship information from Faith Academy website"""
        logger.info(f"Scraping scholarship information for {self.name}")
        
        try:
            # Implementation will go here
            return {
                "status": "success",
                "introduction": "",
                "data": []
            }
            
        except Exception as e:
            logger.error(f"Error scraping scholarship information for {self.name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def scrape_contact_info(self):
        """Scrape contact information from Faith Academy website"""
        logger.info(f"Scraping contact information for {self.name}")
        
        try:
            url = f"{self.base_url}/contact/"
            
            # Get the contact page
            response = await self.session_manager.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize contact data structure
            contact_data = {
                "email": "N/A",
                "phone_numbers": [],
                "contact_person": "N/A"
            }
            
            # Extract email addresses
            email_section = soup.select_one("div[data-id='535fadb']")
            if email_section:
                email_items = email_section.select("li.elementor-icon-list-item a")
                emails = []
                for item in email_items:
                    email_text = item.select_one(".elementor-icon-list-text")
                    if email_text:
                        email = email_text.text.strip()
                        if email and "@" in email:
                            # Make sure to get the full email (some emails in the HTML are truncated)
                            href = item.get('href', '')
                            if href.startswith('mailto:'):
                                full_email = href[7:]  # Remove 'mailto:' prefix
                                emails.append(full_email)
                            else:
                                # If no mailto href, use the text content
                                emails.append(email + ".ph")  # Add .ph since emails in text are truncated
                
                if emails:
                    contact_data["email"] = emails
            
            # Extract phone numbers
            phone_section = soup.select_one("div[data-id='12322ac']")
            if phone_section:
                phone_text = phone_section.get_text(strip=True)
                # Use regex to extract phone numbers
                import re
                phone_numbers = re.findall(r'[\+\d][\d\s\-\(\)]{10,}', phone_text)
                if phone_numbers:
                    contact_data["phone_numbers"] = [phone.strip() for phone in phone_numbers]
            
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
        """Main method to scrape all data from Faith Academy website"""
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
        scraper = FaithScraper()
        result = await scraper.scrape()
        print(json.dumps(result, indent=4))
    
    asyncio.run(main())