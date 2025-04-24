# School Data Scraper

This project is designed to scrape data from international schools in the Philippines, providing a unified structure for easy comparison and analysis.

## Features

- Universal data scraping architecture to handle different school websites
- Standardized data structure across all schools
- Asynchronous scraping for improved performance
- Streamlit UI for easy data visualization and export
- Error handling and detailed logging

## Data Structure

All school data is standardized into the following fields:

- **Name**: School name
- **Link**: School website URL
- **School Fee**: Extracted tuition and fee information
- **Program/Curriculum**: Academic programs offered
- **Enrollment Process**: Application requirements and procedures
- **Events**: Upcoming school events
- **Discounts and Scholarships**: Financial aid opportunities
- **Contact Info**: How to get in touch with the school
- **Notes**: Additional information or scraping errors

## Setup and Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit application:

```bash
streamlit run app.py
```

## Architecture

The project is organized as follows:

- `app.py`: Streamlit UI and main application entry point
- `utils/school_data.py`: Utility for providing school website information
- `services/models.py`: Data models for consistent structure
- `services/scraper.py`: Universal web scraper implementation
- `services/session_manager.py`: Asynchronous HTTP request manager

## How It Works

1. The application loads the list of schools from `SchoolData`
2. User selects schools to analyze
3. The app concurrently scrapes data from all selected schools
4. Data is presented in a standardized format for comparison
5. Results can be downloaded as CSV

## Technical Implementation

- Uses `curl-cffi` for browser emulation and efficient HTTP requests
- Employs `BeautifulSoup` for HTML parsing
- Implements intelligent content extraction based on field type
- Handles various website structures through heuristic content identification 