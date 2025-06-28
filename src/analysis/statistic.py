"""
Statistical analysis module for scraped data.
Provides data quality checks, statistical summaries, and distributions.
"""

import pandas as pd
import numpy as np
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re


class DataStatistics:
    """Statistical analysis for scraped data."""
    
    def __init__(self, data_path: str = "data_output/combined.csv", 
                 db_path: str = "data_output/scraped_articles.db"):
        """Initialize with data paths."""
        self.data_path = data_path
        self.db_path = db_path
        self.df = None
        self.connection = None
        
    def load_data(self) -> bool:
        """Load data from CSV or database."""
        try:
            if os.path.exists(self.data_path):
                self.df = pd.read_csv(self.data_path)
                print(f"Loaded {len(self.df)} records from CSV")
                return True
            elif os.path.exists(self.db_path):
                self.connection = sqlite3.connect(self.db_path)
                self.df = pd.read_sql_query("SELECT * FROM articles", self.connection)
                print(f"Loaded {len(self.df)} records from database")
                return True
            else:
                print("No data files found")
                return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def close_connection(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def data_quality_check(self) -> Dict[str, Any]:
        """Perform comprehensive data quality checks."""
        if self.df is None:
            return {"error": "No data loaded"}
        
        quality_report = {
            "total_records": len(self.df),
            "missing_values": {},
            "duplicates": {},
            "data_types": {},
            "value_ranges": {},
            "anomalies": {}
        }
        
        # Check missing values
        missing_counts = self.df.isnull().sum()
        quality_report["missing_values"] = {
            col: {"count": int(count), "percentage": float(count/len(self.df)*100)}
            for col, count in missing_counts.items() if count > 0
        }
        
        # Check duplicates
        duplicate_counts = self.df.duplicated().sum()
        quality_report["duplicates"]["total"] = int(duplicate_counts)
        quality_report["duplicates"]["percentage"] = float(duplicate_counts/len(self.df)*100)
        
        # Check URL duplicates specifically
        if 'url' in self.df.columns:
            url_duplicates = self.df['url'].duplicated().sum()
            quality_report["duplicates"]["url_duplicates"] = int(url_duplicates)
        
        # Data types
        quality_report["data_types"] = self.df.dtypes.astype(str).to_dict()
        
        # Value ranges for numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            quality_report["value_ranges"][col] = {
                "min": float(self.df[col].min()),
                "max": float(self.df[col].max()),
                "mean": float(self.df[col].mean()),
                "std": float(self.df[col].std())
            }
        
        # Check for anomalies in text lengths
        if 'title' in self.df.columns:
            title_lengths = self.df['title'].str.len()
            quality_report["anomalies"]["title_length"] = {
                "min": int(title_lengths.min()),
                "max": int(title_lengths.max()),
                "mean": float(title_lengths.mean()),
                "std": float(title_lengths.std())
            }
        
        if 'summary' in self.df.columns:
            summary_lengths = self.df['summary'].str.len()
            quality_report["anomalies"]["summary_length"] = {
                "min": int(summary_lengths.min()),
                "max": int(summary_lengths.max()),
                "mean": float(summary_lengths.mean()),
                "std": float(summary_lengths.std())
            }
        
        return quality_report
    
    def statistical_summary(self) -> Dict[str, Any]:
        """Generate comprehensive statistical summary."""
        if self.df is None:
            return {"error": "No data loaded"}
        
        summary = {
            "basic_stats": {},
            "source_analysis": {},
            "temporal_analysis": {},
            "content_analysis": {},
            "author_analysis": {}
        }
        
        # Basic statistics
        summary["basic_stats"]["total_articles"] = len(self.df)
        summary["basic_stats"]["unique_sources"] = self.df['source'].nunique()
        if 'author' in self.df.columns:
            summary["basic_stats"]["unique_authors"] = self.df['author'].nunique()
        
        # Source analysis
        source_counts = self.df['source'].value_counts()
        summary["source_analysis"]["top_sources"] = source_counts.head(10).to_dict()
        summary["source_analysis"]["source_type_distribution"] = self.df['source_type'].value_counts().to_dict()
        
        # Temporal analysis
        if 'publication_date_datetime' in self.df.columns:
            try:
                self.df['pub_date'] = pd.to_datetime(self.df['publication_date_datetime'], errors='coerce')
                date_stats = self.df['pub_date'].describe()
                summary["temporal_analysis"]["date_range"] = {
                    "earliest": str(date_stats['min']),
                    "latest": str(date_stats['max']),
                    "total_days": (date_stats['max'] - date_stats['min']).days
                }
                
                # Articles per day
                daily_counts = self.df['pub_date'].dt.date.value_counts()
                summary["temporal_analysis"]["daily_stats"] = {
                    "avg_articles_per_day": float(daily_counts.mean()),
                    "max_articles_per_day": int(daily_counts.max()),
                    "min_articles_per_day": int(daily_counts.min())
                }
            except Exception as e:
                summary["temporal_analysis"]["error"] = str(e)
        
        # Content analysis
        if 'title' in self.df.columns:
            title_lengths = self.df['title'].str.len()
            summary["content_analysis"]["title_stats"] = {
                "avg_length": float(title_lengths.mean()),
                "median_length": float(title_lengths.median()),
                "std_length": float(title_lengths.std())
            }
        
        if 'summary' in self.df.columns:
            summary_lengths = self.df['summary'].str.len()
            summary["content_analysis"]["summary_stats"] = {
                "avg_length": float(summary_lengths.mean()),
                "median_length": float(summary_lengths.median()),
                "std_length": float(summary_lengths.std())
            }
        
        # Author analysis
        if 'author' in self.df.columns:
            author_counts = self.df['author'].value_counts()
            summary["author_analysis"]["top_authors"] = author_counts.head(10).to_dict()
            summary["author_analysis"]["total_authors"] = len(author_counts)
            summary["author_analysis"]["avg_articles_per_author"] = float(len(self.df) / len(author_counts))
        
        return summary
    
    def distribution_analysis(self) -> Dict[str, Any]:
        """Analyze distributions of various data fields."""
        if self.df is None:
            return {"error": "No data loaded"}
        
        distributions = {
            "source_distribution": {},
            "author_distribution": {},
            "content_length_distribution": {},
            "temporal_distribution": {}
        }
        
        # Source distribution
        source_dist = self.df['source'].value_counts()
        distributions["source_distribution"] = {
            "total_sources": len(source_dist),
            "concentration": float(source_dist.head(10).sum() / len(self.df) * 100)
        }
        
        # Author distribution
        if 'author' in self.df.columns:
            author_dist = self.df['author'].value_counts()
            distributions["author_distribution"] = {
                "total_authors": len(author_dist),
                "concentration": float(author_dist.head(10).sum() / len(self.df) * 100)
            }
        
        # Content length distribution
        if 'title' in self.df.columns:
            title_lengths = self.df['title'].str.len()
            distributions["content_length_distribution"]["title"] = {
                "percentiles": {
                    "25%": float(title_lengths.quantile(0.25)),
                    "50%": float(title_lengths.quantile(0.50)),
                    "75%": float(title_lengths.quantile(0.75)),
                    "90%": float(title_lengths.quantile(0.90)),
                    "95%": float(title_lengths.quantile(0.95))
                },
                "bins": {
                    "short": int((title_lengths <= 50).sum()),
                    "medium": int(((title_lengths > 50) & (title_lengths <= 100)).sum()),
                    "long": int((title_lengths > 100).sum())
                }
            }
        
        if 'summary' in self.df.columns:
            summary_lengths = self.df['summary'].str.len()
            distributions["content_length_distribution"]["summary"] = {
                "percentiles": {
                    "25%": float(summary_lengths.quantile(0.25)),
                    "50%": float(summary_lengths.quantile(0.50)),
                    "75%": float(summary_lengths.quantile(0.75)),
                    "90%": float(summary_lengths.quantile(0.90)),
                    "95%": float(summary_lengths.quantile(0.95))
                },
                "bins": {
                    "short": int((summary_lengths <= 200).sum()),
                    "medium": int(((summary_lengths > 200) & (summary_lengths <= 500)).sum()),
                    "long": int((summary_lengths > 500).sum())
                }
            }
        
        # Temporal distribution
        if 'publication_date_datetime' in self.df.columns and 'pub_date' in self.df.columns:
            try:
                daily_counts = self.df['pub_date'].dt.date.value_counts()
                distributions["temporal_distribution"] = {
                    "daily_variance": float(daily_counts.var()),
                    "peak_day": str(daily_counts.idxmax()),
                    "peak_count": int(daily_counts.max()),
                    "quiet_day": str(daily_counts.idxmin()),
                    "quiet_count": int(daily_counts.min())
                }
            except Exception as e:
                distributions["temporal_distribution"]["error"] = str(e)
        
        return distributions
    
    def generate_visualizations(self, output_dir: str = "data_output/reports"):
        """Generate statistical visualizations."""
        if self.df is None:
            print("No data loaded for visualization")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Source distribution
        plt.figure(figsize=(12, 8))
        source_counts = self.df['source'].value_counts().head(15)
        plt.barh(range(len(source_counts)), source_counts.values)
        plt.yticks(range(len(source_counts)), source_counts.index)
        plt.xlabel('Number of Articles')
        plt.title('Top 15 Sources by Article Count')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/source_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Source type distribution
        plt.figure(figsize=(10, 6))
        source_type_counts = self.df['source_type'].value_counts()
        plt.pie(source_type_counts.values, labels=source_type_counts.index, autopct='%1.1f%%')
        plt.title('Distribution by Source Type')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/source_type_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Title length distribution
        if 'title' in self.df.columns:
            plt.figure(figsize=(10, 6))
            title_lengths = self.df['title'].str.len()
            plt.hist(title_lengths, bins=50, alpha=0.7, edgecolor='black')
            plt.xlabel('Title Length (characters)')
            plt.ylabel('Frequency')
            plt.title('Distribution of Title Lengths')
            plt.axvline(title_lengths.mean(), color='red', linestyle='--', label=f'Mean: {title_lengths.mean():.1f}')
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"{output_dir}/title_length_distribution.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Temporal distribution (if dates available)
        if 'publication_date_datetime' in self.df.columns and 'pub_date' in self.df.columns:
            try:
                plt.figure(figsize=(15, 6))
                daily_counts = self.df['pub_date'].dt.date.value_counts().sort_index()
                plt.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=4)
                plt.xlabel('Date')
                plt.ylabel('Number of Articles')
                plt.title('Articles Published Over Time')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(f"{output_dir}/temporal_distribution.png", dpi=300, bbox_inches='tight')
                plt.close()
            except Exception as e:
                print(f"Error creating temporal visualization: {e}")
        
        # 5. Author distribution (top 20)
        if 'author' in self.df.columns:
            plt.figure(figsize=(12, 8))
            author_counts = self.df['author'].value_counts().head(20)
            plt.barh(range(len(author_counts)), author_counts.values)
            plt.yticks(range(len(author_counts)), author_counts.index)
            plt.xlabel('Number of Articles')
            plt.title('Top 20 Authors by Article Count')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/author_distribution.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"Visualizations saved to {output_dir}")
    
    def export_statistics(self, output_dir: str = "data_output/reports") -> Dict[str, str]:
        """Export all statistics to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {}
        
        # Generate all statistics
        quality_report = self.data_quality_check()
        statistical_summary = self.statistical_summary()
        distributions = self.distribution_analysis()
        
        # Combine all statistics
        all_stats = {
            "generated_at": datetime.now().isoformat(),
            "data_quality": quality_report,
            "statistical_summary": statistical_summary,
            "distributions": distributions
        }
        
        # Export to JSON
        json_path = f"{output_dir}/statistics_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(all_stats, f, indent=2, default=str)
        exported_files["json"] = json_path
        
        # Export to CSV (summary statistics)
        csv_data = []
        for source, count in statistical_summary.get("source_analysis", {}).get("top_sources", {}).items():
            csv_data.append({
                "source": source,
                "article_count": count,
                "percentage": count / statistical_summary["basic_stats"]["total_articles"] * 100
            })
        
        if csv_data:
            df_summary = pd.DataFrame(csv_data)
            csv_path = f"{output_dir}/source_statistics_{timestamp}.csv"
            df_summary.to_csv(csv_path, index=False)
            exported_files["csv"] = csv_path
        
        # Generate visualizations
        self.generate_visualizations(output_dir)
        
        return exported_files


def main():
    """Main function for running statistics analysis."""
    stats = DataStatistics()
    
    if stats.load_data():
        print("Running statistical analysis...")
        
        # Generate and export statistics
        exported_files = stats.export_statistics()
        
        print("Statistics analysis completed!")
        print("Exported files:")
        for file_type, path in exported_files.items():
            print(f"  {file_type.upper()}: {path}")
        
        stats.close_connection()
    else:
        print("Failed to load data for analysis")


if __name__ == "__main__":
    main() 