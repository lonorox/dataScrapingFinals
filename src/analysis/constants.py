"""
Constants and templates for the analysis module.
Contains HTML templates and other configuration constants.
"""

# HTML template for comprehensive reports
HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Scraping Analysis Report</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f8f9fa; 
            line-height: 1.6;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background-color: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
        }
        h1 { 
            color: #2c3e50; 
            text-align: center; 
            border-bottom: 4px solid #3498db; 
            padding-bottom: 15px; 
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        h2 { 
            color: #34495e; 
            margin-top: 40px; 
            margin-bottom: 20px;
            font-size: 1.8em;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        h3 { 
            color: #7f8c8d; 
            margin-top: 25px;
            font-size: 1.3em;
        }
        .metric { 
            background-color: #ecf0f1; 
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 8px; 
            border-left: 5px solid #3498db; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .insight { 
            background-color: #e8f5e8; 
            padding: 15px; 
            margin: 8px 0; 
            border-radius: 8px; 
            border-left: 5px solid #27ae60; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .recommendation { 
            background-color: #fff3cd; 
            padding: 15px; 
            margin: 8px 0; 
            border-radius: 8px; 
            border-left: 5px solid #ffc107; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 25px; 
            margin: 25px 0; 
        }
        .stat-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px; 
            border-radius: 12px; 
            text-align: center; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-number { 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #ffffff; 
            margin-bottom: 5px;
        }
        .stat-label { 
            color: #e8f4f8; 
            font-size: 1.1em;
            font-weight: 500;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin: 25px 0; 
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        th, td { 
            padding: 15px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }
        th { 
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white; 
            font-weight: 600;
        }
        tr:nth-child(even) { 
            background-color: #f8f9fa; 
        }
        tr:hover {
            background-color: #e3f2fd;
        }
        .timestamp { 
            text-align: center; 
            color: #6c757d; 
            font-style: italic; 
            margin-top: 40px; 
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        .visualization-section {
            margin: 40px 0;
            padding: 30px;
            background-color: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }
        .visualization-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }
        .visualization-item {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        .visualization-item img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .visualization-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .section-divider {
            height: 2px;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            margin: 40px 0;
            border-radius: 1px;
        }
        .alert {
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 5px solid #e74c3c;
            background-color: #fdf2f2;
            color: #c53030;
        }
        .success {
            border-left-color: #27ae60;
            background-color: #f0fff4;
            color: #22543d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Data Scraping Analysis Report</h1>
        <p class="timestamp">Generated on: {{ timestamp }}</p>
        
        <h2>📈 Executive Summary</h2>
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
        
        <h3>🔍 Key Insights</h3>
        {% for insight in key_insights %}
        <div class="insight">💡 {{ insight }}</div>
        {% endfor %}
        
        <h3>💡 Recommendations</h3>
        {% for rec in recommendations %}
        <div class="recommendation">📋 {{ rec }}</div>
        {% endfor %}
        
        <div class="section-divider"></div>
        
        <h2>📊 Data Visualizations</h2>
        <div class="visualization-section">
            <div class="visualization-grid">
                {% if temporal_distribution %}
                <div class="visualization-item">
                    <div class="visualization-title">📅 Temporal Distribution</div>
                    <img src="data:image/png;base64,{{ temporal_distribution }}" alt="Temporal Distribution of Articles">
                </div>
                {% endif %}
                
                {% if source_distribution %}
                <div class="visualization-item">
                    <div class="visualization-title">📰 Source Distribution</div>
                    <img src="data:image/png;base64,{{ source_distribution }}" alt="Source Distribution">
                </div>
                {% endif %}
                
                {% if source_type_distribution %}
                <div class="visualization-item">
                    <div class="visualization-title">🏷️ Source Type Distribution</div>
                    <img src="data:image/png;base64,{{ source_type_distribution }}" alt="Source Type Distribution">
                </div>
                {% endif %}
                
                {% if author_distribution %}
                <div class="visualization-item">
                    <div class="visualization-title">👤 Author Distribution</div>
                    <img src="data:image/png;base64,{{ author_distribution }}" alt="Author Distribution">
                </div>
                {% endif %}
                
                {% if title_length_distribution %}
                <div class="visualization-item">
                    <div class="visualization-title">📏 Title Length Distribution</div>
                    <img src="data:image/png;base64,{{ title_length_distribution }}" alt="Title Length Distribution">
                </div>
                {% endif %}
            </div>
        </div>
        
        <div class="section-divider"></div>
        
        <h2>📋 Detailed Analysis</h2>
        
        <h3>📰 Source Distribution</h3>
        <table>
            <tr>
                <th>Source Type</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
            {% for source_type, count in source_types.items() %}
            <tr>
                <td>{{ source_type }}</td>
                <td>{{ count }}</td>
                <td>{{ "%.1f"|format((count / overview.total_articles) * 100) }}%</td>
            </tr>
            {% endfor %}
        </table>
        
        <h3>🏆 Top Sources</h3>
        <table>
            <tr>
                <th>Rank</th>
                <th>Source</th>
                <th>Article Count</th>
                <th>Source Type</th>
                <th>Percentage</th>
            </tr>
            {% for source, data in top_sources.items() %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ source }}</td>
                <td>{{ data.article_count }}</td>
                <td>{{ data.source_type }}</td>
                <td>{{ "%.1f"|format((data.article_count / overview.total_articles) * 100) }}%</td>
            </tr>
            {% endfor %}
        </table>
        
        <h3>📊 Performance Metrics</h3>
        <div class="metric">
            <strong>📈 Data Completeness:</strong><br>
            <div style="margin: 10px 0;">
                <span style="display: inline-block; width: 120px;">Titles:</span>
                <span style="color: {{ 'green' if performance_metrics.data_completeness.titles >= 90 else 'orange' if performance_metrics.data_completeness.titles >= 70 else 'red' }}">
                    {{ "%.1f"|format(performance_metrics.data_completeness.titles) }}%
                </span>
            </div>
            <div style="margin: 10px 0;">
                <span style="display: inline-block; width: 120px;">Summaries:</span>
                <span style="color: {{ 'green' if performance_metrics.data_completeness.summaries >= 90 else 'orange' if performance_metrics.data_completeness.summaries >= 70 else 'red' }}">
                    {{ "%.1f"|format(performance_metrics.data_completeness.summaries) }}%
                </span>
            </div>
            <div style="margin: 10px 0;">
                <span style="display: inline-block; width: 120px;">Authors:</span>
                <span style="color: {{ 'green' if performance_metrics.data_completeness.authors >= 90 else 'orange' if performance_metrics.data_completeness.authors >= 70 else 'red' }}">
                    {{ "%.1f"|format(performance_metrics.data_completeness.authors) }}%
                </span>
            </div>
        </div>
        
        <div class="metric">
            <strong>⚡ Source Efficiency:</strong><br>
            <div style="margin: 10px 0;">
                <span style="display: inline-block; width: 150px;">Articles per Source:</span>
                <span>{{ "%.2f"|format(performance_metrics.source_efficiency.articles_per_source) }}</span>
            </div>
            <div style="margin: 10px 0;">
                <span style="display: inline-block; width: 150px;">Top Source Contribution:</span>
                <span>{{ "%.1f"|format(performance_metrics.source_efficiency.top_source_contribution) }}%</span>
            </div>
        </div>
        
        {% if data_quality_issues %}
        <h3>⚠️ Data Quality Issues</h3>
        <div class="alert">
            <strong>Issues Found:</strong><br>
            {% for issue in data_quality_issues %}
            • {{ issue }}<br>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="section-divider"></div>
        
        <div class="timestamp">
            <strong>Report generated by Data Scraping Analysis System</strong><br>
            For questions or support, please contact the development team.
        </div>
    </div>
</body>
</html>
"""

# Image file patterns to look for in reports directory
VISUALIZATION_IMAGES = {
    'temporal_distribution': 'temporal_distribution.png',
    'source_distribution': 'source_distribution.png', 
    'source_type_distribution': 'source_type_distribution.png',
    'author_distribution': 'author_distribution.png',
    'title_length_distribution': 'title_length_distribution.png'
}

# CSS styles for different alert types
ALERT_STYLES = {
    'success': 'border-left-color: #27ae60; background-color: #f0fff4; color: #22543d;',
    'warning': 'border-left-color: #ffc107; background-color: #fff3cd; color: #856404;',
    'error': 'border-left-color: #e74c3c; background-color: #fdf2f2; color: #c53030;',
    'info': 'border-left-color: #3498db; background-color: #e3f2fd; color: #1e3a8a;'
}

# Report generation settings
REPORT_SETTINGS = {
    'max_top_sources': 10,
    'chart_width': 800,
    'chart_height': 600,
    'dpi': 100,
    'style': 'seaborn-v0_8'
} 