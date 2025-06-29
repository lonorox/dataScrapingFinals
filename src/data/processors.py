"""
Data processing utilities for handling data output operations.
"""

import os
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.utils.logger import log

class DataOutputManager:
    """Manages data output operations with append functionality."""
    
    def __init__(self, output_dir: str = "data_output/raw"):
        """Initialize the data output manager."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def append_to_json(self, filename: str, data: List[Dict[str, Any]]) -> bool:
        """Append data to a JSON file, creating it if it doesn't exist."""
        try:
            filepath = self.output_dir / filename
            
            # Load existing data if file exists
            existing_data = []
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_data = []
            
            # Append new data
            if isinstance(existing_data, list):
                existing_data.extend(data)
            else:
                existing_data = [existing_data] + data
            
            # Write back to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            log.info(f"Error appending to JSON {filename}: {e}")
            return False
    
    def append_to_csv(self, filename: str, data: List[Dict[str, Any]]) -> bool:
        """Append data to a CSV file, creating it if it doesn't exist."""
        try:
            filepath = self.output_dir / filename
            
            # Check if file exists to determine if we need to write headers
            file_exists = filepath.exists()
            
            # Get fieldnames from data
            if data:
                fieldnames = list(data[0].keys())
            else:
                return True  # No data to append
            
            # Append data to CSV
            mode = 'a' if file_exists else 'w'
            with open(filepath, mode, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # Write header only if file is new
                if not file_exists:
                    writer.writeheader()
                
                # Write data
                for row in data:
                    writer.writerow(row)
            
            return True
        except Exception as e:
            log.info(f"Error appending to CSV {filename}: {e}")
            return False
    
    def save_combined_csv(self, data_by_type: Dict[str, List[Dict[str, Any]]], filename: str = "combined.csv") -> bool:
        """Save combined data from multiple sources to CSV with append functionality."""
        try:
            # Prepare all items with source type
            all_items = []
            for source_type, items in data_by_type.items():
                for item in items:
                    item_copy = item.copy()
                    item_copy['source_type'] = source_type
                    all_items.append(item_copy)
            
            if not all_items:
                return True
            
            # Use pandas for better CSV handling
            try:
                df_new = pd.DataFrame(all_items)
                filepath = self.output_dir / filename
                
                if filepath.exists():
                    # Read existing data and append
                    df_existing = pd.read_csv(filepath)
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    # Remove duplicates based on URL if it exists
                    if 'url' in df_combined.columns:
                        df_combined = df_combined.drop_duplicates(subset=['url'], keep='last')
                else:
                    df_combined = df_new
                
                df_combined.to_csv(filepath, index=False)
                return True
                
            except ImportError:
                # Fallback to CSV writer if pandas is not available
                return self.append_to_csv(filename, all_items)
                
        except Exception as e:
            log.info(f"Error saving combined CSV: {e}")
            return False
    
    def save_summary_csv(self, results: List[Any], filename: str = "summary.csv") -> bool:
        """Save summary data to CSV with append functionality."""
        try:
            filepath = self.output_dir/  filename
            
            # Prepare summary data
            summary_data = []
            for result in results:
                summary_data.append({
                    'task_id': result.task_id,
                    'worker_name': result.worker_name,
                    'source_type': result.source_type,
                    'success': result.success,
                    'processing_time': round(result.processing_time, 2),
                    'data_count': len(result.data) if result.data else 0,
                    'error_message': result.error_message if hasattr(result, 'error_message') else None,
                    'timestamp': datetime.now().isoformat()
                })
            
            return self.append_to_csv(filename, summary_data)
            
        except Exception as e:
            log.info(f"Error saving summary CSV: {e}")
            return False
    
    def save_worker_result(self, worker_name: str, data: List[Dict[str, Any]]) -> bool:
        """Save individual worker results with timestamp."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"worker_{worker_name}_{timestamp}.json"
            return self.append_to_json(filename, data)
        except Exception as e:
            log.info(f"Error saving worker result: {e}")
            return False
    
    def cleanup_old_files(self, max_age_hours: int = 24, pattern: str = "worker_*.json") -> None:
        """Clean up old files in the output directory."""
        try:
            import glob
            
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            # Get all files matching pattern
            file_pattern = self.output_dir / pattern
            files = glob.glob(str(file_pattern))
            
            for file_path in files:
                try:
                    # Get file modification time
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mtime < cutoff_time:
                        os.remove(file_path)
                        log.info(f"Cleaned up old file: {file_path}")
                except Exception as e:
                    log.info(f"Failed to clean up file {file_path}: {e}")
                    
        except Exception as e:
            log.info(f"Error during cleanup: {e}")
    
    def save_articles_json(self, filename: str, data: List[Dict[str, Any]]) -> bool:
        """Save articles to a JSON file (wrapper for append_to_json)."""
        return self.append_to_json(filename, data)

# Global instance for easy access
data_output_manager = DataOutputManager()

def consolidate_worker_data(output_dir: str = "data_output/raw") -> Dict[str, List[Dict[str, Any]]]:
    """
    Consolidate all worker JSON files by source type.
    
    Returns:
        Dict with keys 'blog', 'news', 'rss' containing consolidated data
    """
    import glob
    from pathlib import Path
    
    output_path = Path(output_dir)
    consolidated_data = {
        'blog': [],
        'news': [],
        'rss': []
    }
    
    # Find all worker JSON files
    worker_files = glob.glob(str(output_path / "worker_*.json"))
    
    for file_path in worker_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                data = [data]
            
            # Group data by source_type
            for item in data:
                source_type = item.get('source_type', '').lower()
                if source_type in consolidated_data:
                    consolidated_data[source_type].append(item)
                else:
                    # If source_type is not recognized, try to infer from URL or other fields
                    url = item.get('url', '').lower()
                    if any(keyword in url for keyword in ['blog', 'medium', 'wordpress']):
                        consolidated_data['blog'].append(item)
                    elif any(keyword in url for keyword in ['news', 'cnn', 'bbc', 'reuters']):
                        consolidated_data['news'].append(item)
                    elif any(keyword in url for keyword in ['rss', 'feed', 'xml']):
                        consolidated_data['rss'].append(item)
                    else:
                        # Default to news if can't determine
                        consolidated_data['news'].append(item)
                        
        except Exception as e:
            log.error(f"Error processing file {file_path}: {e}")
            continue
    
    return consolidated_data

def save_consolidated_data(consolidated_data: Dict[str, List[Dict[str, Any]]], 
                          output_dir: str = "data_output/raw") -> bool:
    """
    Save consolidated data to type-specific JSON files and combined CSV.
    
    Args:
        consolidated_data: Dictionary with 'blog', 'news', 'rss' keys containing data
        output_dir: Output directory path
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save type-specific JSON files with append functionality
        for data_type, data in consolidated_data.items():
            if data:
                filename = f"{data_type}_data.json"
                # Use the existing append_to_json method to append data instead of overwriting
                success = data_output_manager.append_to_json(filename, data)
                if success:
                    log.info(f"Appended {len(data)} items to {filename}")
                else:
                    log.error(f"Failed to append data to {filename}")
        
        # Save combined CSV
        success = data_output_manager.save_combined_csv(consolidated_data, "combined.csv")
        
        if success:
            log.info("Successfully saved combined CSV file")
        else:
            log.error("Failed to save combined CSV file")
        
        return success
        
    except Exception as e:
        log.error(f"Error saving consolidated data: {e}")
        return False

def cleanup_worker_files(output_dir: str = "data_output/raw") -> bool:
    """
    Delete worker files after consolidation.
    
    Args:
        output_dir: Directory containing worker files
    
    Returns:
        bool: True if successful, False otherwise
    """
    import glob
    from pathlib import Path
    
    try:
        output_path = Path(output_dir)
        
        # Find all worker JSON files
        worker_files = glob.glob(str(output_path / "worker_*.json"))
        
        deleted_count = 0
        for file_path in worker_files:
            try:
                # Delete file directly
                os.remove(file_path)
                deleted_count += 1
                
            except Exception as e:
                log.info(f"Error deleting file {file_path}: {e}")
                continue
        
        log.info(f"Deleted {deleted_count} worker files")
        return True
        
    except Exception as e:
        log.error(f"Error during cleanup: {e}")
        return False 