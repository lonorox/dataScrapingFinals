"""
Simple database manager for converting combined.csv to SQLite.
"""

import sqlite3
import csv
import os
from datetime import datetime
from typing import List, Dict, Any


class Database:
    """Converts combined.csv to SQLite database."""
    
    def __init__(self, csv_path: str = "data_output/raw/combined.csv", db_path: str = "data_output/raw/scraped_articles.db"):
        """Initialize converter with CSV and database paths."""
        self.csv_path = csv_path
        self.db_path = db_path
        self.connection = None
    
    def _get_connection(self):
        """Get database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
        except Exception as e:
            # Handle threading-related errors gracefully
            # This can happen when the connection was created in a different thread
            print(f"Warning: Could not close database connection: {e}")
            self.connection = None
    
    def create_table(self):
        """Create the articles table based on CSV structure."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    url TEXT UNIQUE,
                    author TEXT,
                    publication_date_datetime TEXT,
                    publication_date_readable TEXT,
                    summary TEXT,
                    tags TEXT,
                    source_type TEXT,
                    source TEXT,
                    scraped_at TEXT,
                    metadata TEXT,
                    worker_id INTEGER,
                    task_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source_type ON articles(source_type)')
            
            conn.commit()
            print(f"Table 'articles' created successfully in {self.db_path}")
    
    def convert_csv_to_sqlite(self) -> int:
        """Convert combined.csv to SQLite database."""
        if not os.path.exists(self.csv_path):
            print(f"Error: CSV file not found at {self.csv_path}")
            return 0
        
        # Create table first
        self.create_table()
        
        converted_count = 0
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    for row in reader:
                        try:
                            # Insert row into database
                            cursor.execute('''
                                INSERT OR IGNORE INTO articles (
                                    title, url, author, publication_date_datetime,
                                    publication_date_readable, summary, tags,
                                    source_type, source, scraped_at, metadata,
                                    worker_id, task_id
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                row.get('title'),
                                row.get('url'),
                                row.get('author'),
                                row.get('publication_date_datetime'),
                                row.get('publication_date_readable'),
                                row.get('summary'),
                                row.get('tags'),
                                row.get('source_type'),
                                row.get('source'),
                                row.get('scraped_at'),
                                row.get('metadata'),
                                int(float(row.get('worker_id', 0))) if row.get('worker_id') else 0,
                                int(float(row.get('task_id', 0))) if row.get('task_id') else 0
                            ))
                            
                            converted_count += 1
                            
                        except Exception as e:
                            print(f"Error converting row: {e}")
                            print(f"Problematic row: {row}")
                            continue
                    
                    conn.commit()
            
            print(f"Successfully converted {converted_count} rows from CSV to SQLite")
            return converted_count
            
        except Exception as e:
            print(f"Error during CSV conversion: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the converted data."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total articles
                cursor.execute('SELECT COUNT(*) FROM articles')
                total_articles = cursor.fetchone()[0]
                
                # Articles by source type
                cursor.execute('''
                    SELECT source_type, COUNT(*) as count 
                    FROM articles 
                    GROUP BY source_type
                ''')
                source_type_stats = dict(cursor.fetchall())
                
                # Articles by source
                cursor.execute('''
                    SELECT source, COUNT(*) as count 
                    FROM articles 
                    GROUP BY source 
                    ORDER BY count DESC 
                    LIMIT 10
                ''')
                source_stats = dict(cursor.fetchall())
                
                return {
                    'total_articles': total_articles,
                    'source_type_stats': source_type_stats,
                    'source_stats': source_stats
                }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def export_back_to_csv(self, output_path: str = "data_output/exported_from_sqlite.csv") -> bool:
        """Export data from SQLite back to CSV for verification."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM articles')
                rows = cursor.fetchall()
                
                if not rows:
                    print("No data to export")
                    return False
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(columns)
                    writer.writerows(rows)
                
                print(f"Data exported to {output_path}")
                return True
                
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False


def main():
    """Main function to run the CSV to SQLite conversion."""
    converter = Database()
    
    print("Starting CSV to SQLite conversion...")
    converted_count = converter.convert_csv_to_sqlite()
    
    if converted_count > 0:
        print("\nConversion completed successfully!")
        
        # Show statistics
        stats = converter.get_stats()
        print(f"\nDatabase Statistics:")
        print(f"Total articles: {stats.get('total_articles', 0)}")
        print(f"Source types: {stats.get('source_type_stats', {})}")
        print(f"Top sources: {stats.get('source_stats', {})}")
        
        # Optionally export back to CSV for verification
        converter.export_back_to_csv()
    
    converter.close()


if __name__ == "__main__":
    main() 