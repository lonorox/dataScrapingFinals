"""
Reports generation module for scraped data.
Provides automated reports with insights and data export in multiple formats.
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
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import LineChart, BarChart, PieChart, Reference
import jinja2
import webbrowser


class ReportGenerator:
    """Generate comprehensive reports with insights and data export."""
    
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
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def close_connection(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary with key insights."""
        if self.df is None:
            return {"error": "No data loaded"}
        
        summary = {
            "overview": {},
            "key_insights": [],
            "recommendations": [],
            "performance_metrics": {}
        }
        
        # Overview
        summary["overview"] = {
            "total_articles": len(self.df),
            "date_range": {
                "start": str(self.df['pub_date'].min()) if 'pub_date' in self.df.columns else "Unknown",
                "end": str(self.df['pub_date'].max()) if 'pub_date' in self.df.columns else "Unknown"
            },
            "unique_sources": self.df['source'].nunique(),
            "unique_authors": self.df['author'].nunique() if 'author' in self.df.columns else 0,
            "source_types": self.df['source_type'].value_counts().to_dict()
        }
        
        # Key insights
        insights = []
        
        # Insight 1: Top performing source
        top_source = self.df['source'].value_counts().index[0]
        top_source_count = self.df['source'].value_counts().iloc[0]
        insights.append(f"Top performing source: {top_source} with {top_source_count} articles")
        
        # Insight 2: Content volume trend
        if 'pub_date' in self.df.columns:
            daily_counts = self.df.groupby(self.df['pub_date'].dt.date).size()
            avg_daily = daily_counts.mean()
            insights.append(f"Average daily publication rate: {avg_daily:.1f} articles")
            
            if len(daily_counts) > 1:
                trend = "increasing" if daily_counts.iloc[-1] > daily_counts.iloc[0] else "decreasing"
                insights.append(f"Publication trend: {trend}")
        
        # Insight 3: Content quality
        if 'title' in self.df.columns:
            avg_title_length = self.df['title'].str.len().mean()
            insights.append(f"Average title length: {avg_title_length:.1f} characters")
        
        # Insight 4: Source diversity
        source_concentration = (self.df['source'].value_counts().head(5).sum() / len(self.df)) * 100
        insights.append(f"Top 5 sources account for {source_concentration:.1f}% of all content")
        
        summary["key_insights"] = insights
        
        # Recommendations
        recommendations = []
        
        if source_concentration > 80:
            recommendations.append("Consider diversifying sources to reduce dependency on top sources")
        
        if 'pub_date' in self.df.columns and len(daily_counts) > 1:
            if daily_counts.iloc[-1] < daily_counts.iloc[0]:
                recommendations.append("Monitor declining publication rates and investigate causes")
        
        if self.df['title'].isnull().sum() > len(self.df) * 0.1:
            recommendations.append("Improve data quality by ensuring all articles have titles")
        
        summary["recommendations"] = recommendations
        
        # Performance metrics
        summary["performance_metrics"] = {
            "data_completeness": {
                "titles": float((1 - self.df['title'].isnull().sum() / len(self.df)) * 100),
                "summaries": float((1 - self.df['summary'].isnull().sum() / len(self.df)) * 100) if 'summary' in self.df.columns else 0,
                "authors": float((1 - self.df['author'].isnull().sum() / len(self.df)) * 100) if 'author' in self.df.columns else 0
            },
            "source_efficiency": {
                "articles_per_source": float(len(self.df) / self.df['source'].nunique()),
                "top_source_contribution": float((self.df['source'].value_counts().iloc[0] / len(self.df)) * 100)
            }
        }
        
        return summary
    
    def generate_detailed_analysis(self) -> Dict[str, Any]:
        """Generate detailed analysis report."""
        if self.df is None:
            return {"error": "No data loaded"}
        
        analysis = {
            "source_analysis": {},
            "content_analysis": {},
            "temporal_analysis": {},
            "quality_analysis": {}
        }
        
        # Source analysis
        source_stats = self.df.groupby('source').agg({
            'title': 'count',
            'pub_date': ['min', 'max'] if 'pub_date' in self.df.columns else None
        }).round(2)
        
        if 'pub_date' in self.df.columns:
            source_stats.columns = ['article_count', 'first_article', 'last_article']
            source_stats['date_range_days'] = (source_stats['last_article'] - source_stats['first_article']).dt.days
            source_stats['articles_per_day'] = source_stats['article_count'] / source_stats['date_range_days']
        else:
            source_stats.columns = ['article_count']
        
        analysis["source_analysis"] = {
            "top_sources": source_stats.nlargest(10, 'article_count').to_dict('index'),
            "source_type_distribution": self.df['source_type'].value_counts().to_dict(),
            "source_performance_metrics": {
                "avg_articles_per_source": float(len(self.df) / self.df['source'].nunique()),
                "source_concentration_index": float((self.df['source'].value_counts().head(5).sum() / len(self.df)) * 100)
            }
        }
        
        # Content analysis
        content_metrics = {}
        
        if 'title' in self.df.columns:
            title_lengths = self.df['title'].str.len()
            content_metrics["title"] = {
                "avg_length": float(title_lengths.mean()),
                "median_length": float(title_lengths.median()),
                "std_length": float(title_lengths.std()),
                "min_length": int(title_lengths.min()),
                "max_length": int(title_lengths.max())
            }
        
        if 'summary' in self.df.columns:
            summary_lengths = self.df['summary'].str.len()
            content_metrics["summary"] = {
                "avg_length": float(summary_lengths.mean()),
                "median_length": float(summary_lengths.median()),
                "std_length": float(summary_lengths.std()),
                "min_length": int(summary_lengths.min()),
                "max_length": int(summary_lengths.max())
            }
        
        analysis["content_analysis"] = content_metrics
        
        # Temporal analysis
        if 'pub_date' in self.df.columns:
            temporal_metrics = {}
            
            # Daily patterns
            daily_counts = self.df.groupby(self.df['pub_date'].dt.date).size()
            temporal_metrics["daily"] = {
                "avg_articles_per_day": float(daily_counts.mean()),
                "peak_day": str(daily_counts.idxmax()),
                "peak_count": int(daily_counts.max()),
                "variance": float(daily_counts.var())
            }
            
            # Monthly patterns
            monthly_counts = self.df.groupby(self.df['pub_date'].dt.to_period('M')).size()
            temporal_metrics["monthly"] = {
                "avg_articles_per_month": float(monthly_counts.mean()),
                "peak_month": str(monthly_counts.idxmax()),
                "peak_count": int(monthly_counts.max()),
                "trend": "increasing" if len(monthly_counts) > 1 and monthly_counts.iloc[-1] > monthly_counts.iloc[0] else "stable"
            }
            
            analysis["temporal_analysis"] = temporal_metrics
        
        # Quality analysis
        quality_metrics = {
            "missing_data": {
                "titles": int(self.df['title'].isnull().sum()),
                "summaries": int(self.df['summary'].isnull().sum()) if 'summary' in self.df.columns else 0,
                "authors": int(self.df['author'].isnull().sum()) if 'author' in self.df.columns else 0,
                "urls": int(self.df['url'].isnull().sum()) if 'url' in self.df.columns else 0
            },
            "duplicates": {
                "total_duplicates": int(self.df.duplicated().sum()),
                "url_duplicates": int(self.df['url'].duplicated().sum()) if 'url' in self.df.columns else 0
            }
        }
        
        analysis["quality_analysis"] = quality_metrics
        
        return analysis
    
    def export_to_excel(self, output_path: str = "data_output/reports/comprehensive_report.xlsx") -> str:
        """Export comprehensive report to Excel with multiple sheets and charts."""
        if self.df is None:
            return "No data to export"
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            
            # Sheet 1: Executive Summary
            summary_data = self.generate_executive_summary()
            
            # Create summary DataFrame
            summary_rows = []
            for insight in summary_data.get("key_insights", []):
                summary_rows.append({"Insight": insight})
            
            for rec in summary_data.get("recommendations", []):
                summary_rows.append({"Recommendation": rec})
            
            summary_df = pd.DataFrame(summary_rows)
            summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            # Sheet 2: Source Analysis
            source_analysis = self.df.groupby('source').agg({
                'title': 'count',
                'source_type': 'first'
            }).rename(columns={'title': 'Article Count'}).sort_values('Article Count', ascending=False)
            
            source_analysis.to_excel(writer, sheet_name='Source Analysis')
            
            # Sheet 3: Temporal Analysis
            if 'pub_date' in self.df.columns:
                daily_counts = self.df.groupby(self.df['pub_date'].dt.date).size().reset_index()
                daily_counts.columns = ['Date', 'Article Count']
                daily_counts.to_excel(writer, sheet_name='Daily Trends', index=False)
            
            # Sheet 4: Content Analysis
            content_data = []
            if 'title' in self.df.columns:
                title_lengths = self.df['title'].str.len()
                content_data.append({
                    'Metric': 'Title Length',
                    'Average': title_lengths.mean(),
                    'Median': title_lengths.median(),
                    'Min': title_lengths.min(),
                    'Max': title_lengths.max()
                })
            
            if 'summary' in self.df.columns:
                summary_lengths = self.df['summary'].str.len()
                content_data.append({
                    'Metric': 'Summary Length',
                    'Average': summary_lengths.mean(),
                    'Median': summary_lengths.median(),
                    'Min': summary_lengths.min(),
                    'Max': summary_lengths.max()
                })
            
            content_df = pd.DataFrame(content_data)
            content_df.to_excel(writer, sheet_name='Content Analysis', index=False)
            
            # Sheet 5: Quality Metrics
            quality_data = []
            quality_data.append({
                'Metric': 'Total Articles',
                'Value': len(self.df)
            })
            quality_data.append({
                'Metric': 'Unique Sources',
                'Value': self.df['source'].nunique()
            })
            quality_data.append({
                'Metric': 'Missing Titles',
                'Value': self.df['title'].isnull().sum()
            })
            if 'summary' in self.df.columns:
                quality_data.append({
                    'Metric': 'Missing Summaries',
                    'Value': self.df['summary'].isnull().sum()
                })
            
            quality_df = pd.DataFrame(quality_data)
            quality_df.to_excel(writer, sheet_name='Quality Metrics', index=False)
            
            # Add charts to the workbook
            workbook = writer.book
            
            # Chart 1: Top Sources Bar Chart
            if len(source_analysis) > 0:
                chart_sheet = workbook.create_sheet('Charts')
                
                # Source distribution chart
                chart1 = BarChart()
                chart1.title = "Top 10 Sources by Article Count"
                chart1.x_axis.title = "Source"
                chart1.y_axis.title = "Article Count"
                
                data = Reference(writer.sheets['Source Analysis'], min_col=2, min_row=1, max_row=11, max_col=2)
                cats = Reference(writer.sheets['Source Analysis'], min_col=1, min_row=2, max_row=11)
                chart1.add_data(data, titles_from_data=True)
                chart1.set_categories(cats)
                
                chart_sheet.add_chart(chart1, "A1")
        
        return output_path
    
    def export_to_csv(self, output_dir: str = "data_output/reports") -> Dict[str, str]:
        """Export data to multiple CSV files."""
        if self.df is None:
            return {"error": "No data to export"}
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {}
        
        # Main data export
        main_csv = f"{output_dir}/complete_dataset_{timestamp}.csv"
        self.df.to_csv(main_csv, index=False)
        exported_files["complete_dataset"] = main_csv
        
        # Source summary
        source_summary = self.df.groupby('source').agg({
            'title': 'count',
            'source_type': 'first'
        }).rename(columns={'title': 'article_count'}).reset_index()
        source_csv = f"{output_dir}/source_summary_{timestamp}.csv"
        source_summary.to_csv(source_csv, index=False)
        exported_files["source_summary"] = source_csv
        
        # Daily trends
        if 'pub_date' in self.df.columns:
            daily_trends = self.df.groupby(self.df['pub_date'].dt.date).size().reset_index()
            daily_trends.columns = ['date', 'article_count']
            daily_csv = f"{output_dir}/daily_trends_{timestamp}.csv"
            daily_trends.to_csv(daily_csv, index=False)
            exported_files["daily_trends"] = daily_csv
        
        # Content analysis
        content_analysis = []
        if 'title' in self.df.columns:
            title_stats = self.df['title'].str.len().describe()
            content_analysis.append({
                'metric': 'title_length',
                'count': title_stats['count'],
                'mean': title_stats['mean'],
                'std': title_stats['std'],
                'min': title_stats['min'],
                '25%': title_stats['25%'],
                '50%': title_stats['50%'],
                '75%': title_stats['75%'],
                'max': title_stats['max']
            })
        
        if content_analysis:
            content_df = pd.DataFrame(content_analysis)
            content_csv = f"{output_dir}/content_analysis_{timestamp}.csv"
            content_df.to_csv(content_csv, index=False)
            exported_files["content_analysis"] = content_csv
        
        return exported_files
    
    def generate_html_report(self, output_path: str = "data_output/reports/comprehensive_report.html") -> str:
        """Generate comprehensive HTML report."""
        if self.df is None:
            return "No data to generate report"
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate analysis data
        executive_summary = self.generate_executive_summary()
        detailed_analysis = self.generate_detailed_analysis()
        
        # HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Scraping Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        h3 { color: #7f8c8d; }
        .metric { background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
        .insight { background-color: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #27ae60; }
        .recommendation { background-color: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #ffc107; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #dee2e6; }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { color: #6c757d; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .timestamp { text-align: center; color: #6c757d; font-style: italic; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Scraping Analysis Report</h1>
        <p class="timestamp">Generated on: {{ timestamp }}</p>
        
        <h2>Executive Summary</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ overview.total_articles }}</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ overview.unique_sources }}</div>
                <div class="stat-label">Unique Sources</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ overview.unique_authors }}</div>
                <div class="stat-label">Unique Authors</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ overview.date_range.start[:10] if overview.date_range.start != 'Unknown' else 'N/A' }}</div>
                <div class="stat-label">Start Date</div>
            </div>
        </div>
        
        <h3>Key Insights</h3>
        {% for insight in key_insights %}
        <div class="insight">{{ insight }}</div>
        {% endfor %}
        
        <h3>Recommendations</h3>
        {% for rec in recommendations %}
        <div class="recommendation">{{ rec }}</div>
        {% endfor %}
        
        <h2>Detailed Analysis</h2>
        
        <h3>Source Distribution</h3>
        <table>
            <tr>
                <th>Source Type</th>
                <th>Count</th>
            </tr>
            {% for source_type, count in source_types.items() %}
            <tr>
                <td>{{ source_type }}</td>
                <td>{{ count }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h3>Top Sources</h3>
        <table>
            <tr>
                <th>Source</th>
                <th>Article Count</th>
                <th>Source Type</th>
            </tr>
            {% for source, data in top_sources.items() %}
            <tr>
                <td>{{ source }}</td>
                <td>{{ data.article_count }}</td>
                <td>{{ data.source_type }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h3>Performance Metrics</h3>
        <div class="metric">
            <strong>Data Completeness:</strong><br>
            Titles: {{ performance_metrics.data_completeness.titles }}%<br>
            Summaries: {{ performance_metrics.data_completeness.summaries }}%<br>
            Authors: {{ performance_metrics.data_completeness.authors }}%
        </div>
        
        <div class="metric">
            <strong>Source Efficiency:</strong><br>
            Articles per Source: {{ performance_metrics.source_efficiency.articles_per_source }}<br>
            Top Source Contribution: {{ performance_metrics.source_efficiency.top_source_contribution }}%
        </div>
    </div>
</body>
</html>
        """
        
        # Prepare template data
        template_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overview": executive_summary["overview"],
            "key_insights": executive_summary["key_insights"],
            "recommendations": executive_summary["recommendations"],
            "performance_metrics": executive_summary["performance_metrics"],
            "source_types": executive_summary["overview"]["source_types"],
            "top_sources": dict(list(detailed_analysis["source_analysis"]["top_sources"].items())[:10])
        }
        
        # Render template
        template = jinja2.Template(html_template)
        html_content = template.render(**template_data)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_comprehensive_report(self, output_dir: str = "data_output/reports") -> Dict[str, str]:
        """Generate comprehensive report in multiple formats."""
        if self.df is None:
            return {"error": "No data loaded"}
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        generated_files = {}
        
        # Generate all reports
        print("Generating executive summary...")
        executive_summary = self.generate_executive_summary()
        
        print("Generating detailed analysis...")
        detailed_analysis = self.generate_detailed_analysis()
        
        print("Exporting to Excel...")
        excel_path = self.export_to_excel(f"{output_dir}/comprehensive_report_{timestamp}.xlsx")
        generated_files["excel"] = excel_path
        
        print("Exporting to CSV...")
        csv_files = self.export_to_csv(output_dir)
        generated_files["csv"] = csv_files
        
        print("Generating HTML report...")
        html_path = self.generate_html_report(f"{output_dir}/comprehensive_report_{timestamp}.html")
        generated_files["html"] = html_path
        
        # Save JSON report
        json_report = {
            "generated_at": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "detailed_analysis": detailed_analysis
        }
        
        json_path = f"{output_dir}/comprehensive_report_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2, default=str)
        generated_files["json"] = json_path
        
        return generated_files


def main():
    """Main function for running report generation."""
    reporter = ReportGenerator()
    
    if reporter.load_data():
        print("Generating comprehensive reports...")
        
        # Generate all reports
        generated_files = reporter.generate_comprehensive_report()
        
        print("Report generation completed!")
        print("Generated files:")
        for file_type, path in generated_files.items():
            if isinstance(path, dict):
                print(f"  {file_type.upper()}:")
                for sub_type, sub_path in path.items():
                    print(f"    {sub_type}: {sub_path}")
            else:
                print(f"  {file_type.upper()}: {path}")
        
        reporter.close_connection()
    else:
        print("Failed to load data for report generation")


if __name__ == "__main__":
    main() 