import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

class DataManager:
    """Manages storage and retrieval of scraped school data"""
    
    def __init__(self, data_dir: str = "data_outputs"):
        """
        Initialize the data manager
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_results(self, results: List[Dict[str, Any]], prefix: str = "school_data") -> str:
        """
        Save scraped results to CSV and JSON
        
        Args:
            results: List of school data dictionaries
            prefix: Filename prefix
            
        Returns:
            Path to the saved CSV file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_base = f"{prefix}_{timestamp}"
        
        # Save as CSV
        csv_path = os.path.join(self.data_dir, f"{file_base}.csv")
        pd.DataFrame(results).to_csv(csv_path, index=False)
        
        # Save as JSON with pretty formatting
        json_path = os.path.join(self.data_dir, f"{file_base}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return csv_path
    
    def load_latest_results(self, prefix: str = "school_data") -> Optional[List[Dict[str, Any]]]:
        """
        Load the most recent scraped results
        
        Args:
            prefix: Filename prefix to search for
            
        Returns:
            List of school data dictionaries or None if no data found
        """
        # Find all JSON files with the prefix
        json_files = [
            f for f in os.listdir(self.data_dir) 
            if f.startswith(prefix) and f.endswith('.json')
        ]
        
        if not json_files:
            return None
        
        # Sort by timestamp (descending)
        json_files.sort(reverse=True)
        latest_file = os.path.join(self.data_dir, json_files[0])
        
        # Load the data
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_available_datasets(self, prefix: str = "school_data") -> List[str]:
        """
        Get list of available datasets
        
        Args:
            prefix: Filename prefix to search for
            
        Returns:
            List of dataset timestamps
        """
        json_files = [
            f for f in os.listdir(self.data_dir) 
            if f.startswith(prefix) and f.endswith('.json')
        ]
        
        # Extract timestamps from filenames
        timestamps = [
            f.replace(f"{prefix}_", "").replace(".json", "") 
            for f in json_files
        ]
        
        return sorted(timestamps, reverse=True) 