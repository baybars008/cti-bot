"""
Simple API utilities for dashboard data
Works without Flask context
"""

import sqlite3
from typing import Dict, List, Any
from collections import Counter

def get_all_posts() -> List[Dict]:
    """Get all posts from database"""
    conn = sqlite3.connect('instance/data.db')
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM posts")
    rows = cur.fetchall()
    
    # Get column names
    cur.execute("PRAGMA table_info(posts)")
    columns = [col[1] for col in cur.fetchall()]
    
    conn.close()
    
    posts = []
    for row in rows:
        post_dict = dict(zip(columns, row))
        posts.append(post_dict)
    
    return posts

def get_dashboard_data() -> Dict:
    """Get comprehensive dashboard data"""
    posts = get_all_posts()
    
    if not posts:
        return {
            'overview': {
                'total_attacks': 0,
                'total_companies': 0,
                'total_countries': 0,
                'total_sectors': 0,
                'total_threat_actors': 0
            },
            'risk_distribution': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'top_countries': {},
            'top_threat_actors': {},
            'real_sectors': {},
            'activities': {}
        }
    
    # Basic stats
    total_attacks = len(posts)
    total_companies = len(set([p.get('name') for p in posts if p.get('name')]))
    total_countries = len(set([p.get('country') for p in posts if p.get('country')]))
    total_sectors = len(set([p.get('activity') for p in posts if p.get('activity')]))
    
    # Risk distribution
    risk_levels = Counter([p.get('activity') for p in posts if p.get('activity')])
    critical_attacks = risk_levels.get('Critical', 0) + risk_levels.get('Kritik', 0)
    high_attacks = risk_levels.get('High', 0) + risk_levels.get('Yüksek', 0)
    medium_attacks = risk_levels.get('Medium', 0) + risk_levels.get('Orta', 0)
    low_attacks = risk_levels.get('Low', 0) + risk_levels.get('Düşük', 0)
    
    # Geographic analysis
    country_counts = Counter([p.get('country') for p in posts if p.get('country')])
    top_countries = dict(country_counts.most_common(10))
    
    # Threat actors
    threat_actor_counts = Counter([p.get('name') for p in posts if p.get('name')])
    top_threat_actors = dict(threat_actor_counts.most_common(10))
    
    # Sectors
    sector_counts = Counter([p.get('activity') for p in posts if p.get('activity')])
    real_sectors = dict(sector_counts.most_common(10))
    
    # Activities
    activities = dict(Counter([p.get('activity') for p in posts if p.get('activity')]))
    
    return {
        'overview': {
            'total_attacks': total_attacks,
            'total_companies': total_companies,
            'total_countries': total_countries,
            'total_sectors': total_sectors,
            'total_threat_actors': len(top_threat_actors)
        },
        'risk_distribution': {
            'critical': critical_attacks,
            'high': high_attacks,
            'medium': medium_attacks,
            'low': low_attacks
        },
        'top_countries': top_countries,
        'top_threat_actors': top_threat_actors,
        'real_sectors': real_sectors,
        'activities': activities
    }

def get_filtered_attacks(start_date=None, end_date=None, country=None, risk_level=None) -> List[Dict]:
    """Get filtered attacks"""
    posts = get_all_posts()
    
    # Apply filters
    filtered_posts = []
    for post in posts:
        if not post.get('name'):
            continue
            
        # Date filter
        if start_date and post.get('discovered', '') < start_date:
            continue
        if end_date and post.get('discovered', '') > end_date:
            continue
            
        # Country filter
        if country and post.get('country') != country:
            continue
            
        # Risk level filter
        if risk_level and post.get('activity') != risk_level:
            continue
            
        filtered_posts.append(post)
    
    # Convert to API format
    attacks = []
    for post in filtered_posts:
        attacks.append({
            'company': post.get('name') or 'Unknown',
            'sector': post.get('sector') or 'Unknown',
            'country': post.get('country') or 'Unknown',
            'threat_actor': post.get('name') or 'Unknown',
            'risk_level': post.get('activity') or 'Medium',
            'date': post.get('discovered') or 'Unknown'
        })
    
    return attacks

def get_recent_attacks(page=1, per_page=10, start_date=None, end_date=None) -> Dict:
    """Get recent attacks with pagination"""
    posts = get_all_posts()
    
    # Apply date filters
    filtered_posts = []
    for post in posts:
        if not post.get('name'):
            continue
            
        if start_date and post.get('discovered', '') < start_date:
            continue
        if end_date and post.get('discovered', '') > end_date:
            continue
            
        filtered_posts.append(post)
    
    # Sort by date
    filtered_posts.sort(key=lambda x: x.get('discovered', ''), reverse=True)
    
    # Pagination
    total = len(filtered_posts)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_posts = filtered_posts[start_idx:end_idx]
    
    # Convert to API format
    attacks = []
    for post in page_posts:
        attacks.append({
            'company': post.get('name') or 'Unknown',
            'sector': post.get('sector') or 'Unknown',
            'country': post.get('country') or 'Unknown',
            'threat_actor': post.get('name') or 'Unknown',
            'risk_level': post.get('activity') or 'Medium',
            'date': post.get('discovered') or 'Unknown',
            'is_threat_actor': False
        })
    
    return {
        'attacks': attacks,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }
