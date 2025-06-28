"""
Trend analysis module for scraped data.
Provides time-based trend analysis and comparative analysis across sources.
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
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


class TrendAnalysis:
    """Trend analysis for scraped data."""
    
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
            elif os.path.exists(self.db_path):
                self.connection = sqlite3.connect(self.db_path)
                self.df = pd.read_sql_query("SELECT * FROM articles", self.connection)
                print(f"Loaded {len(self.df)} records from database")
            else:
                print("No data files found")
                return False
            
            # Preprocess dates
            if 'publication_date_datetime' in self.df.columns:
                self.df['pub_date'] = pd.to_datetime(self.df['publication_date_datetime'], errors='coerce')
                self.df = self.df.dropna(subset=['pub_date'])
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def close_connection(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def temporal_trend_analysis(self) -> Dict[str, Any]:
        """Analyze temporal trends in the data."""
        if self.df is None or 'pub_date' not in self.df.columns:
            return {"error": "No temporal data available"}
        
        trends = {
            "daily_trends": {},
            "weekly_trends": {},
            "monthly_trends": {},
            "seasonal_patterns": {},
            "growth_rates": {}
        }
        
        # Daily trends
        daily_counts = self.df.groupby(self.df['pub_date'].dt.date).size()
        trends["daily_trends"] = {
            "total_days": len(daily_counts),
            "avg_articles_per_day": float(daily_counts.mean()),
            "peak_day": str(daily_counts.idxmax()),
            "peak_count": int(daily_counts.max()),
            "quiet_day": str(daily_counts.idxmin()),
            "quiet_count": int(daily_counts.min()),
            "variance": float(daily_counts.var()),
            "trend_direction": "increasing" if daily_counts.iloc[-1] > daily_counts.iloc[0] else "decreasing"
        }
        
        # Weekly trends
        self.df['week'] = self.df['pub_date'].dt.isocalendar().week
        self.df['year'] = self.df['pub_date'].dt.year
        weekly_counts = self.df.groupby(['year', 'week']).size()
        
        trends["weekly_trends"] = {
            "total_weeks": len(weekly_counts),
            "avg_articles_per_week": float(weekly_counts.mean()),
            "peak_week": f"{weekly_counts.idxmax()[0]}-W{weekly_counts.idxmax()[1]:02d}",
            "peak_count": int(weekly_counts.max()),
            "variance": float(weekly_counts.var())
        }
        
        # Monthly trends
        self.df['month'] = self.df['pub_date'].dt.to_period('M')
        monthly_counts = self.df.groupby('month').size()
        
        trends["monthly_trends"] = {
            "total_months": len(monthly_counts),
            "avg_articles_per_month": float(monthly_counts.mean()),
            "peak_month": str(monthly_counts.idxmax()),
            "peak_count": int(monthly_counts.max()),
            "growth_rate": float((monthly_counts.iloc[-1] - monthly_counts.iloc[0]) / monthly_counts.iloc[0] * 100)
        }
        
        # Seasonal patterns
        self.df['season'] = self.df['pub_date'].dt.month.map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })
        
        seasonal_counts = self.df.groupby('season').size()
        trends["seasonal_patterns"] = seasonal_counts.to_dict()
        
        # Growth rates
        if len(monthly_counts) > 1:
            monthly_growth = monthly_counts.pct_change().dropna()
            trends["growth_rates"] = {
                "avg_monthly_growth": float(monthly_growth.mean() * 100),
                "max_growth": float(monthly_growth.max() * 100),
                "max_decline": float(monthly_growth.min() * 100),
                "growth_volatility": float(monthly_growth.std() * 100)
            }
        
        return trends
    
    def source_comparative_analysis(self) -> Dict[str, Any]:
        """Compare trends across different sources."""
        if self.df is None:
            return {"error": "No data loaded"}
        
        comparison = {
            "source_performance": {},
            "content_comparison": {},
            "temporal_comparison": {},
            "correlation_analysis": {}
        }
        
        # Source performance metrics
        source_stats = self.df.groupby('source').agg({
            'title': 'count',
            'pub_date': ['min', 'max']
        }).round(2)
        
        source_stats.columns = ['article_count', 'first_article', 'last_article']
        source_stats['date_range_days'] = (source_stats['last_article'] - source_stats['first_article']).dt.days
        source_stats['articles_per_day'] = source_stats['article_count'] / source_stats['date_range_days']
        
        # Top performing sources
        top_sources = source_stats.nlargest(10, 'article_count')
        comparison["source_performance"]["top_sources"] = top_sources.to_dict('index')
        
        # Content comparison
        if 'title' in self.df.columns:
            title_lengths_by_source = self.df.groupby('source')['title'].apply(lambda x: x.str.len().mean())
            comparison["content_comparison"]["avg_title_length"] = title_lengths_by_source.to_dict()
        
        if 'summary' in self.df.columns:
            summary_lengths_by_source = self.df.groupby('source')['summary'].apply(lambda x: x.str.len().mean())
            comparison["content_comparison"]["avg_summary_length"] = summary_lengths_by_source.to_dict()
        
        # Temporal comparison by source
        if 'pub_date' in self.df.columns:
            source_temporal = {}
            for source in self.df['source'].unique():
                source_data = self.df[self.df['source'] == source]
                if len(source_data) > 10:  # Only analyze sources with sufficient data
                    daily_counts = source_data.groupby(source_data['pub_date'].dt.date).size()
                    source_temporal[source] = {
                        "avg_daily_articles": float(daily_counts.mean()),
                        "peak_day": str(daily_counts.idxmax()) if len(daily_counts) > 0 else None,
                        "total_days_active": len(daily_counts),
                        "consistency_score": float(1 - daily_counts.std() / daily_counts.mean()) if daily_counts.mean() > 0 else 0
                    }
            
            comparison["temporal_comparison"] = source_temporal
        
        # Correlation analysis between sources
        if 'pub_date' in self.df.columns:
            # Create daily time series for each source
            source_correlations = {}
            top_sources_list = top_sources.head(5).index.tolist()
            
            for i, source1 in enumerate(top_sources_list):
                for source2 in top_sources_list[i+1:]:
                    source1_data = self.df[self.df['source'] == source1]
                    source2_data = self.df[self.df['source'] == source2]
                    
                    if len(source1_data) > 5 and len(source2_data) > 5:
                        source1_daily = source1_data.groupby(source1_data['pub_date'].dt.date).size()
                        source2_daily = source2_data.groupby(source2_data['pub_date'].dt.date).size()
                        
                        # Align the series
                        common_dates = source1_daily.index.intersection(source2_daily.index)
                        if len(common_dates) > 5:
                            corr = source1_daily[common_dates].corr(source2_daily[common_dates])
                            source_correlations[f"{source1}_vs_{source2}"] = float(corr)
            
            comparison["correlation_analysis"] = source_correlations
        
        return comparison
    
    def keyword_trend_analysis(self, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze trends in keyword usage over time."""
        if self.df is None or 'title' not in self.df.columns:
            return {"error": "No title data available"}
        
        if keywords is None:
            # Extract common keywords from titles
            all_titles = ' '.join(self.df['title'].dropna().astype(str))
            words = re.findall(r'\b\w+\b', all_titles.lower())
            word_counts = Counter(words)
            # Filter out common stop words and short words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
            keywords = [word for word, count in word_counts.most_common(20) 
                       if word not in stop_words and len(word) > 3]
        
        keyword_trends = {}
        
        for keyword in keywords:
            # Find articles containing the keyword
            keyword_articles = self.df[self.df['title'].str.contains(keyword, case=False, na=False)]
            
            if len(keyword_articles) > 0 and 'pub_date' in keyword_articles.columns:
                # Group by month
                keyword_articles['month'] = keyword_articles['pub_date'].dt.to_period('M')
                monthly_counts = keyword_articles.groupby('month').size()
                
                keyword_trends[keyword] = {
                    "total_mentions": len(keyword_articles),
                    "monthly_trend": monthly_counts.to_dict(),
                    "peak_month": str(monthly_counts.idxmax()) if len(monthly_counts) > 0 else None,
                    "trend_direction": "increasing" if len(monthly_counts) > 1 and monthly_counts.iloc[-1] > monthly_counts.iloc[0] else "stable"
                }
        
        return {
            "analyzed_keywords": keywords,
            "keyword_trends": keyword_trends,
            "top_keywords": sorted(keyword_trends.items(), key=lambda x: x[1]["total_mentions"], reverse=True)[:10]
        }
    
    def source_type_analysis(self) -> Dict[str, Any]:
        """Analyze trends by source type (blog, news, rss)."""
        if self.df is None:
            return {"error": "No data loaded"}
        
        source_type_analysis = {
            "distribution": {},
            "temporal_patterns": {},
            "content_characteristics": {},
            "performance_comparison": {}
        }
        
        # Distribution
        source_type_counts = self.df['source_type'].value_counts()
        source_type_analysis["distribution"] = source_type_counts.to_dict()
        
        # Temporal patterns by source type
        if 'pub_date' in self.df.columns:
            for source_type in self.df['source_type'].unique():
                type_data = self.df[self.df['source_type'] == source_type]
                if len(type_data) > 10:
                    daily_counts = type_data.groupby(type_data['pub_date'].dt.date).size()
                    source_type_analysis["temporal_patterns"][source_type] = {
                        "avg_daily_articles": float(daily_counts.mean()),
                        "peak_day": str(daily_counts.idxmax()) if len(daily_counts) > 0 else None,
                        "consistency": float(1 - daily_counts.std() / daily_counts.mean()) if daily_counts.mean() > 0 else 0
                    }
        
        # Content characteristics by source type
        if 'title' in self.df.columns:
            title_lengths_by_type = self.df.groupby('source_type')['title'].apply(lambda x: x.str.len().mean())
            source_type_analysis["content_characteristics"]["avg_title_length"] = title_lengths_by_type.to_dict()
        
        if 'summary' in self.df.columns:
            summary_lengths_by_type = self.df.groupby('source_type')['summary'].apply(lambda x: x.str.len().mean())
            source_type_analysis["content_characteristics"]["avg_summary_length"] = summary_lengths_by_type.to_dict()
        
        # Performance comparison
        source_type_stats = self.df.groupby('source_type').agg({
            'title': 'count',
            'source': 'nunique'
        }).rename(columns={'title': 'total_articles', 'source': 'unique_sources'})
        
        source_type_stats['avg_articles_per_source'] = source_type_stats['total_articles'] / source_type_stats['unique_sources']
        source_type_analysis["performance_comparison"] = source_type_stats.to_dict('index')
        
        return source_type_analysis
    
    def generate_trend_visualizations(self, output_dir: str = "data_output/reports"):
        """Generate trend visualizations."""
        if self.df is None:
            print("No data loaded for visualization")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Daily trend over time
        if 'pub_date' in self.df.columns:
            plt.figure(figsize=(15, 6))
            daily_counts = self.df.groupby(self.df['pub_date'].dt.date).size()
            plt.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=4)
            plt.xlabel('Date')
            plt.ylabel('Number of Articles')
            plt.title('Daily Article Publication Trend')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/daily_trend.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. Monthly trend
        if 'pub_date' in self.df.columns:
            plt.figure(figsize=(12, 6))
            monthly_counts = self.df.groupby(self.df['pub_date'].dt.to_period('M')).size()
            plt.bar(range(len(monthly_counts)), monthly_counts.values, alpha=0.7)
            plt.xlabel('Month')
            plt.ylabel('Number of Articles')
            plt.title('Monthly Article Publication Trend')
            plt.xticks(range(len(monthly_counts)), [str(x) for x in monthly_counts.index], rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/monthly_trend.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Source type comparison over time
        if 'pub_date' in self.df.columns:
            plt.figure(figsize=(15, 6))
            for source_type in self.df['source_type'].unique():
                type_data = self.df[self.df['source_type'] == source_type]
                monthly_counts = type_data.groupby(type_data['pub_date'].dt.to_period('M')).size()
                plt.plot(range(len(monthly_counts)), monthly_counts.values, marker='o', label=source_type, linewidth=2)
            
            plt.xlabel('Month')
            plt.ylabel('Number of Articles')
            plt.title('Monthly Trend by Source Type')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/source_type_trends.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Seasonal patterns
        if 'pub_date' in self.df.columns:
            plt.figure(figsize=(10, 6))
            self.df['season'] = self.df['pub_date'].dt.month.map({
                12: 'Winter', 1: 'Winter', 2: 'Winter',
                3: 'Spring', 4: 'Spring', 5: 'Spring',
                6: 'Summer', 7: 'Summer', 8: 'Summer',
                9: 'Fall', 10: 'Fall', 11: 'Fall'
            })
            seasonal_counts = self.df.groupby('season').size()
            plt.pie(seasonal_counts.values, labels=seasonal_counts.index, autopct='%1.1f%%')
            plt.title('Seasonal Distribution of Articles')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/seasonal_patterns.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        # 5. Top sources performance comparison
        plt.figure(figsize=(12, 8))
        source_counts = self.df['source'].value_counts().head(15)
        colors = plt.cm.viridis(np.linspace(0, 1, len(source_counts)))
        plt.barh(range(len(source_counts)), source_counts.values, color=colors)
        plt.yticks(range(len(source_counts)), source_counts.index)
        plt.xlabel('Number of Articles')
        plt.title('Top 15 Sources Performance')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/source_performance.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Trend visualizations saved to {output_dir}")
    
    def export_trend_analysis(self, output_dir: str = "data_output/reports") -> Dict[str, str]:
        """Export all trend analysis to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {}
        
        # Generate all trend analyses
        temporal_trends = self.temporal_trend_analysis()
        source_comparison = self.source_comparative_analysis()
        keyword_trends = self.keyword_trend_analysis()
        source_type_analysis = self.source_type_analysis()
        
        # Combine all analyses
        all_trends = {
            "generated_at": datetime.now().isoformat(),
            "temporal_trends": temporal_trends,
            "source_comparison": source_comparison,
            "keyword_trends": keyword_trends,
            "source_type_analysis": source_type_analysis
        }
        
        # Export to JSON
        json_path = f"{output_dir}/trend_analysis_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(all_trends, f, indent=2, default=str)
        exported_files["json"] = json_path
        
        # Export temporal data to CSV
        if 'pub_date' in self.df.columns:
            daily_counts = self.df.groupby(self.df['pub_date'].dt.date).size().reset_index()
            daily_counts.columns = ['date', 'article_count']
            csv_path = f"{output_dir}/daily_trends_{timestamp}.csv"
            daily_counts.to_csv(csv_path, index=False)
            exported_files["csv"] = csv_path
        
        # Generate visualizations
        self.generate_trend_visualizations(output_dir)
        
        return exported_files


def main():
    """Main function for running trend analysis."""
    trends = TrendAnalysis()
    
    if trends.load_data():
        print("Running trend analysis...")
        
        # Generate and export trend analysis
        exported_files = trends.export_trend_analysis()
        
        print("Trend analysis completed!")
        print("Exported files:")
        for file_type, path in exported_files.items():
            print(f"  {file_type.upper()}: {path}")
        
        trends.close_connection()
    else:
        print("Failed to load data for analysis")


if __name__ == "__main__":
    main() 