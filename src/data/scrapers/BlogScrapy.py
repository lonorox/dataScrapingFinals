import subprocess
import json
import os
from src.utils.logger import log
from src.scrapers.ScraperFactory import Scraper
from src.data.models import Article
from typing import List, Dict, Any
from datetime import datetime

class BlogScrapy(Scraper):
    def __init__(self):
        self.name = "techcrunch"
        
    def scrape(self, url):
        # Get the current working directory
        current_dir = os.getcwd()
        
        # Change to the Scrapy project directory
        scrapy_project_dir = os.path.join(current_dir, "src", "scrapers", "scrapy_crawler")
        
        # Use a fixed output file name
        output_file = "temp_output.json"
        
        cmd = [
            "scrapy", "crawl", "techcrunch",
            "-o", output_file
        ]

        try:
            # Run scrapy command from the correct directory
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                cwd=scrapy_project_dir
            )

            if result.returncode != 0:
                log.error(f"Scrapy spider failed: {result.stderr}")
                raise RuntimeError(f"Scrapy spider error: {result.stderr}")

            # Read the output file
            output_path = os.path.join(scrapy_project_dir, output_file)
            if os.path.exists(output_path):
                raw_data = self._parse_scrapy_output(output_path)
                
                # Clean up the output file
                os.remove(output_path)
                
                # Preprocess the data and convert to Article objects
                articles = self.preprocess_data(raw_data)
                
                # Add source type metadata
                for article in articles:
                    article.source_type = 'blog'
                    if not article.scraped_at:
                        article.scraped_at = datetime.now()
                
                log.info(f"Successfully scraped {len(articles)} blog articles")
                return articles
            else:
                log.warning("Scrapy output file not found")
                return []
                
        except Exception as e:
            log.error(f"Unexpected error running Scrapy: {str(e)}")
            raise

    def _parse_scrapy_output(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse the Scrapy output file, handling malformed JSON with multiple arrays."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Handle the case where multiple JSON arrays are concatenated with ][
            if '][' in content:
                # Split by ][ and fix the JSON structure
                parts = content.split('][')
                all_data = []
                
                for i, part in enumerate(parts):
                    # Remove leading [ and trailing ] if they exist
                    if part.startswith('['):
                        part = part[1:]
                    if part.endswith(']'):
                        part = part[:-1]
                    
                    # Skip empty parts
                    if not part.strip():
                        continue
                    
                    try:
                        # Parse each part as JSON
                        if part.strip():
                            data = json.loads(f"[{part}]")
                            all_data.extend(data)
                    except json.JSONDecodeError as e:
                        log.warning(f"Failed to parse JSON part {i}: {e}")
                        continue
                
                return all_data
            else:
                # Normal JSON parsing
                return json.loads(content)
                
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON from Scrapy output: {str(e)}")
            # Try to recover by reading line by line
            return self._parse_json_line_by_line(file_path)
        except Exception as e:
            log.error(f"Error reading Scrapy output file: {e}")
            return []

    def _parse_json_line_by_line(self, file_path: str) -> List[Dict[str, Any]]:
        """Fallback method to parse JSON line by line."""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line not in ['[', ']']:
                        # Remove trailing comma if present
                        if line.endswith(','):
                            line = line[:-1]
                        try:
                            item = json.loads(line)
                            data.append(item)
                        except json.JSONDecodeError:
                            continue
            return data
        except Exception as e:
            log.error(f"Error in line-by-line parsing: {e}")
            return []

    def preprocess_data(self, raw_data: List[Dict[str, Any]]) -> List[Article]:
        """Convert raw data to Article objects."""
        articles = []
        #             'title': title,
        #             'url': article_url,
        #             'author': author,
        #             'publication_date_datetime': date_datetime,
        #             'publication_date_readable': date_readable,
        #             'summary': summary,
        #             'tags': tags

        #                 article = Article(
        #                     source=self.get_site_name(),
        #                     title=self._cleaner(headline),
        #                     summary=self._cleaner(summary.get_text()),
        #                     url=link,
        #                     tags=tags,
        #                     scraped_at=datetime.now(),
        #                     metadata={
        #                         'scraper': 'NewsScraper',
        #                         'framework': 'basicScraper/bs4'
        #                     }
        #                 )
        for item in raw_data:
            try:
                # Create Article object from raw data
                article = Article(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    author=item.get('author'),
                    publication_date_datetime=item.get('publication_date_datetime'),
                    publication_date_readable=item.get('publication_date_readable'),
                    summary=item.get('summary'),
                    tags=item.get('tags', []),
                    source_type='blog',
                    source='TechCrunch',
                    scraped_at=datetime.now(),
                    metadata={
                        'scraper': 'BlogScrapy',
                        'spider': 'techcrunch'
                    }
                )
                articles.append(article)
            except Exception as e:
                log.error(f"Error creating Article object: {e}")
                continue
        
        return articles