import asyncio
import streamlit as st
import pandas as pd
from utils.school_data import SchoolData
from services.schools.ism_scraper import ISMScraper
import importlib
import os
import sys
import inspect
import traceback
from typing import Dict, Any, List, Tuple, Optional

# Set page configuration
st.set_page_config(
    page_title="LICS - International School Data Scraper",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cache school scrapers to avoid reloading
@st.cache_resource
def load_scrapers():
    """Load all available school-specific scrapers"""
    scrapers = {}
    schools_module_path = os.path.join(os.path.dirname(__file__), "services", "schools")
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Get list of scraper modules
    scraper_files = [f[:-3] for f in os.listdir(schools_module_path) 
                   if f.endswith("_scraper.py") and not f.startswith("__")]
    
    for scraper_module in scraper_files:
        try:
            # Import the module
            module_name = f"services.schools.{scraper_module}"
            module = importlib.import_module(module_name)
            
            # Find the scraper class
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and name.endswith("Scraper") and name != "Scraper":
                    # Create an instance of the scraper
                    school_name = name.replace("Scraper", "")
                    scrapers[school_name] = obj
                    break
        except Exception as e:
            st.error(f"Failed to load scraper {scraper_module}: {str(e)}")
            continue
    
    return scrapers

# Function to run the scraper asynchronously
async def run_scraper(scraper_class, school_data):
    """Run a scraper on the given school data"""
    try:
        scraper = scraper_class()
        return await scraper.scrape(school_data)
    except Exception as e:
        st.error(f"Error scraping {school_data['name']}: {str(e)}")
        traceback.print_exc()
        return None

# Function to run multiple scrapers in parallel
async def run_scrapers(selected_schools, school_data_list, scrapers):
    """Run scrapers for multiple schools in parallel"""
    tasks = []
    for school in selected_schools:
        # Find the matching school data
        school_data = next((s for s in school_data_list if s["name"] == school), None)
        if not school_data:
            continue
            
        # Find the appropriate scraper
        school_name_no_spaces = school.replace(" ", "")
        scraper_found = False
        
        # Try exact class name match first (e.g., ISMScraper for "International School Manila")
        for scraper_key, scraper_class in scrapers.items():
            # Get the class name without "Scraper" and check if it matches part of the school name
            class_name = scraper_key
            
            # Try direct name match
            if class_name.lower() in school_name_no_spaces.lower():
                st.info(f"Using {class_name}Scraper for {school}")
                tasks.append(run_scraper(scraper_class, school_data))
                scraper_found = True
                break
                
        # If no match found, try matching against initials or acronyms
        if not scraper_found:
            # Get initials from school name (e.g., "International School Manila" -> "ISM")
            words = school.split()
            initials = "".join(word[0] for word in words if len(word) > 1)
            
            for scraper_key, scraper_class in scrapers.items():
                if scraper_key.lower() == initials.lower():
                    st.info(f"Using {scraper_key}Scraper for {school} based on initials match")
                    tasks.append(run_scraper(scraper_class, school_data))
                    scraper_found = True
                    break
                    
        # If still no match found, try a more aggressive match
        if not scraper_found:
            school_parts = school.lower().split()
            for scraper_key, scraper_class in scrapers.items():
                class_name = scraper_key.lower()
                
                # Check if any significant word in the school name appears in the class name
                for part in school_parts:
                    if len(part) > 2 and part in class_name:
                        st.info(f"Using {scraper_key}Scraper for {school} based on partial match")
                        tasks.append(run_scraper(scraper_class, school_data))
                        scraper_found = True
                        break
                
                if scraper_found:
                    break
        
        # If still no match found, use the default ISMScraper
        if not scraper_found:
            st.warning(f"No specific scraper found for {school}. Using default ISMScraper")
            tasks.append(run_scraper(ISMScraper, school_data))
    
    return await asyncio.gather(*tasks)

# Function to display school data in a formatted way
def display_school_data(school_info: Dict[str, Any]):
    """Display formatted school information"""
    if not school_info:
        st.warning("No data available for this school")
        return
    
    # Display school name
    st.header(school_info['name'])
    
    # Check if 'link' key exists in school_info before accessing it
    if 'link' in school_info and school_info['link']:
        st.markdown(f"**Website:** [{school_info['link']}]({school_info['link']})")
    else:
        st.markdown("**Website:** Not available")
    
    # Create tabs for different sections
    tabs = st.tabs(["Programs & Curriculum", "School Fees", "Enrollment Process", 
                   "Scholarships & Discounts", "Contact Information"])
    
    # Helper function to recursively display dictionary content
    def display_dict_data(data, level=0):
        if not data:
            return ""
            
        if isinstance(data, str):
            return data
            
        if isinstance(data, dict):
            result = ""
            for key, value in data.items():
                # Format key as a header based on nesting level
                if level == 0:
                    result += f"### {key}\n\n"
                elif level == 1:
                    result += f"#### {key}\n\n"
                else:
                    result += f"**{key}**\n\n"
                
                # Recursively process value
                result += display_dict_data(value, level + 1)
                result += "\n"
            return result
            
        if isinstance(data, list):
            result = ""
            for item in data:
                result += display_dict_data(item, level) + "\n"
            return result
            
        return str(data)
    
    # Programs & Curriculum tab
    with tabs[0]:
        program_data = None
        # Check different possible keys for program data
        for key in ['program', 'curriculum', 'academic_program', 'academics']:
            if key in school_info and school_info[key] != "No data available":
                program_data = school_info[key]
                break
                
        if program_data:
            if isinstance(program_data, str):
                st.markdown(program_data)
            else:
                st.markdown(display_dict_data(program_data))
        else:
            st.info("No program information available")
    
    # School Fees tab
    with tabs[1]:
        fee_data = None
        # Check different possible keys for fee data
        for key in ['school_fee', 'tuition_fees', 'fees', 'tuition', 'costs']:
            if key in school_info and school_info[key] != "No data available":
                fee_data = school_info[key]
                break
                
        if fee_data:
            if isinstance(fee_data, str):
                st.markdown(fee_data)
            else:
                st.markdown(display_dict_data(fee_data))
        else:
            st.info("No fee information available")
    
    # Enrollment Process tab
    with tabs[2]:
        enrollment_data = None
        # Check different possible keys for enrollment data
        for key in ['enrollment_process', 'admission', 'admissions', 'enrollment', 'application_process']:
            if key in school_info and school_info[key] != "No data available":
                enrollment_data = school_info[key]
                break
                
        if enrollment_data:
            if isinstance(enrollment_data, str):
                st.markdown(enrollment_data)
            else:
                st.markdown(display_dict_data(enrollment_data))
        else:
            st.info("No enrollment information available")
    
    # Scholarships & Discounts tab
    with tabs[3]:
        scholarship_data = None
        # Check different possible keys for scholarship data
        for key in ['discounts_scholarships', 'scholarships', 'financial_aid', 'discounts']:
            if key in school_info and school_info[key] != "No data available":
                scholarship_data = school_info[key]
                break
                
        if scholarship_data:
            if isinstance(scholarship_data, str):
                st.markdown(scholarship_data)
            else:
                st.markdown(display_dict_data(scholarship_data))
        else:
            st.info("No scholarship information available")
    
    # Contact Information tab
    with tabs[4]:
        contact_data = None
        # Check different possible keys for contact data
        for key in ['contact_info', 'contact', 'contacts', 'address']:
            if key in school_info and school_info[key] != "No data available":
                contact_data = school_info[key]
                break
                
        if contact_data:
            if isinstance(contact_data, str):
                st.markdown(contact_data)
            else:
                st.markdown(display_dict_data(contact_data))
        else:
            st.info("No contact information available")
    
    # Display notes and scraping timestamp
    if 'notes' in school_info and school_info['notes']:
        st.caption(school_info['notes'])
    if 'timestamp' in school_info and school_info['timestamp']:
        st.caption(f"Last updated: {school_info['timestamp']}")

# Main function
def main():
    # Load school data and scrapers
    school_data_list = SchoolData.get_schools_list()
    school_names = [school["name"] for school in school_data_list]
    scrapers = load_scrapers()
    
    # School selection
    selected_schools = st.multiselect(
        "Select Schools to Scrape",
        options=school_names,
        default=[school_names[0]]  # Default to first school (ISM)
    )
    
    # Data to Scrape section
    st.subheader("Data to Scrape")
    checkbox_cols = st.columns(5)
    
    with checkbox_cols[0]:
        scrape_program = st.checkbox("Programs & Curriculum", value=True)
    with checkbox_cols[1]:
        scrape_fees = st.checkbox("School Fees", value=True)
    with checkbox_cols[2]:
        scrape_enrollment = st.checkbox("Enrollment Process", value=True)
    with checkbox_cols[3]:
        scrape_scholarships = st.checkbox("Scholarships & Discounts", value=True)
    with checkbox_cols[4]:
        scrape_contact = st.checkbox("Contact Information", value=True)
    
    # Button to start scraping
    scrape_button = st.button("Scrape Selected Schools")
    
    # Results section
    results_container = st.container()
    
    # Handle scraping action
    if scrape_button:
        if not selected_schools:
            st.warning("Please select at least one school to scrape.")
        else:
            with results_container:
                # Show progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("Preparing to scrape schools...")
                
                # Create scraping options dictionary based on checkboxes
                scrape_options = {
                    "program": scrape_program,
                    "school_fee": scrape_fees,
                    "enrollment_process": scrape_enrollment,
                    "discounts_scholarships": scrape_scholarships,
                    "contact_info": scrape_contact
                }
                
                # Run scrapers asynchronously
                results = []
                
                # Create a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Run the scrapers
                    status_text.text("Scraping schools... This may take a minute.")
                    # Pass scrape options to run_scrapers function
                    results = loop.run_until_complete(run_scrapers(selected_schools, school_data_list, scrapers))
                    
                    # Progress updates (assuming each school takes roughly equal time)
                    total_schools = len(selected_schools)
                    progress_bar.progress(50)  # Mark halfway point
                    status_text.text(f"Processing data for {total_schools} schools...")
                finally:
                    loop.close()
                
                # Update progress
                progress_bar.progress(100)
                status_text.text("Scraping complete!")
                
                # Filter out None results
                results = [r for r in results if r is not None]
                
                if not results:
                    st.error("No data was successfully scraped. Please try again.")
                else:
                    # Display results
                    st.header("School Data Comparison")
                    
                    # Optional: Add a download button for the results
                    if results:
                        # Convert results to a simplified format for CSV
                        simplified_results = []
                        for school in results:
                            row = {"Name": school.get("name", "Unknown")}
                            
                            # Add website
                            if "link" in school:
                                row["Website"] = school["link"]
                                
                            # Add program info
                            if scrape_program and any(k in school for k in ["program", "curriculum"]):
                                row["Program Available"] = "Yes"
                            else:
                                row["Program Available"] = "No"
                                
                            # Add fees info
                            if scrape_fees and any(k in school for k in ["school_fee", "tuition_fees", "fees"]):
                                row["Fees Available"] = "Yes"
                            else:
                                row["Fees Available"] = "No"
                            
                            # Add other fields
                            if scrape_enrollment and any(k in school for k in ["enrollment_process", "admissions"]):
                                row["Enrollment Info Available"] = "Yes"
                            else:
                                row["Enrollment Info Available"] = "No"
                                
                            simplified_results.append(row)
                            
                        # Create a DataFrame for download
                        if simplified_results:
                            df = pd.DataFrame(simplified_results)
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "Download Results Summary (CSV)",
                                csv,
                                f"school_comparison_{len(results)}_schools.csv",
                                "text/csv",
                                key='download-csv'
                            )
                    
                    # Display each school's data
                    for school_data in results:
                        st.divider()
                        display_school_data(school_data)
    else:
        # If no action yet, show some info
        with results_container:
            st.info("Select schools above and click 'Scrape Selected Schools' to begin.")

# Run the main function
if __name__ == "__main__":
    main()