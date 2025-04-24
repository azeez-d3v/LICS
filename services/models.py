from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class SchoolInfo:
    """Data class for standardized school information"""
    name: str
    link: str
    school_fee: str = field(default="No data available")
    program: str = field(default="No data available")
    enrollment_process: str = field(default="No data available")
    events: str = field(default="No data available") 
    discounts_scholarships: str = field(default="No data available")
    contact_info: str = field(default="No data available")
    notes: str = field(default_factory=lambda: f"Scraped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def to_dict(self):
        """Convert to dictionary for easier serialization"""
        return {
            "name": self.name,
            "link": self.link,
            "school_fee": self.school_fee,
            "program": self.program,
            "enrollment_process": self.enrollment_process,
            "events": self.events,
            "discounts_scholarships": self.discounts_scholarships,
            "contact_info": self.contact_info,
            "notes": self.notes
        } 