# URL bilgilerinin bulunduğu alan
# Buradan çeşitli adreslere routing işlemi yapabilirsiniz

from flask import Blueprint
from controllers.Controller import *
from controllers.ExportController import *
from controllers.PerformanceController import *
from controllers.IntegrationController import *
from controllers.MonitoringController import *

pclist = Blueprint('pclist', __name__)

# Ana sayfa
pclist.route('/', methods=['GET'])(controller_index)
pclist.route('/dashboard', methods=['GET'])(controller_dashboard)

# API endpoints
pclist.route('/api/dashboard-data', methods=['GET'])(controller_dashboard_data)
pclist.route('/api/social-media-stats', methods=['GET'])(controller_social_media_stats)
pclist.route('/api/recent-attacks', methods=['GET'])(controller_recent_attacks)
pclist.route('/api/filtered-attacks', methods=['GET'])(controller_filtered_attacks)
pclist.route('/api/company-detail/<company_name>', methods=['GET'])(controller_company_detail)
pclist.route('/api/sector-analysis/<sector_name>', methods=['GET'])(controller_sector_analysis)
pclist.route('/api/threat-actor-detail/<threat_actor_name>', methods=['GET'])(controller_threat_actor_detail)

# Hafta 5 - Otomasyon ve İleri Görselleştirmeler
pclist.route('/api/advanced-charts', methods=['GET'])(controller_advanced_charts)
pclist.route('/api/realtime-status', methods=['GET'])(controller_realtime_status)
pclist.route('/api/force-update', methods=['POST'])(controller_force_update)
pclist.route('/api/generate-report', methods=['POST'])(controller_report_generate)

# Sayfa routes
from flask import render_template

def page_filters():
    return render_template('filters.html')

def page_company_detail():
    return render_template('company_detail.html')

def page_sector_analysis():
    return render_template('sector_analysis.html')

def page_threat_actor_detail():
    return render_template('threat_actor_detail.html')

def page_realtime():
    return render_template('realtime_dashboard.html')

def page_analytics():
    return render_template('analytics.html')

def page_reports():
    return render_template('reports.html')

pclist.route('/filters', methods=['GET'])(page_filters)
pclist.route('/company-detail', methods=['GET'])(page_company_detail)
pclist.route('/sector-analysis', methods=['GET'])(page_sector_analysis)
pclist.route('/threat-actor-detail', methods=['GET'])(page_threat_actor_detail)
pclist.route('/realtime', methods=['GET'])(page_realtime)
pclist.route('/analytics', methods=['GET'])(page_analytics)
pclist.route('/reports', methods=['GET'])(page_reports)

# Hafta 6 - Export API Routes
pclist.route('/api/export/attacks', methods=['GET'])(controller_export_attacks)
pclist.route('/api/export/companies', methods=['GET'])(controller_export_companies)
pclist.route('/api/export/bulk', methods=['GET'])(controller_bulk_export)
pclist.route('/api/health', methods=['GET'])(controller_api_health)
pclist.route('/api/status', methods=['GET'])(controller_api_status)

# Hafta 6 - Performance Management Routes
pclist.route('/api/cache/stats', methods=['GET'])(controller_cache_stats)
pclist.route('/api/cache/clear', methods=['POST'])(controller_clear_cache)
pclist.route('/api/database/stats', methods=['GET'])(controller_database_stats)
pclist.route('/api/database/optimize', methods=['POST'])(controller_optimize_database)
pclist.route('/api/performance/monitor', methods=['GET'])(controller_performance_monitor)
pclist.route('/api/performance/analyze', methods=['GET'])(controller_query_analyzer)
pclist.route('/api/performance/auto-optimize', methods=['POST'])(controller_auto_optimize)

# Hafta 6 - Integration Management Routes
pclist.route('/api/integrations/test', methods=['GET'])(controller_test_integrations)
pclist.route('/api/integrations/status', methods=['GET'])(controller_integration_status)
pclist.route('/api/integrations/config', methods=['GET'])(controller_integration_config)
pclist.route('/api/integrations/attack-alert', methods=['POST'])(controller_send_attack_alert)
pclist.route('/api/integrations/daily-summary', methods=['POST'])(controller_send_daily_summary)
pclist.route('/api/integrations/weekly-report', methods=['POST'])(controller_send_weekly_report)
pclist.route('/api/integrations/system-alert', methods=['POST'])(controller_send_system_alert)
pclist.route('/api/integrations/custom-message', methods=['POST'])(controller_send_custom_message)
pclist.route('/api/integrations/slack/test', methods=['GET'])(controller_slack_test)
pclist.route('/api/integrations/email/test', methods=['GET'])(controller_email_test)
pclist.route('/api/integrations/teams/test', methods=['GET'])(controller_teams_test)

# Hafta 7 - Monitoring ve Optimizasyon Routes
pclist.route('/monitoring', methods=['GET'])(controller_monitoring_dashboard)
pclist.route('/api/monitoring/performance', methods=['GET'])(controller_performance_summary)
pclist.route('/api/monitoring/errors', methods=['GET'])(controller_error_summary)
pclist.route('/api/monitoring/health', methods=['GET'])(controller_system_health)
pclist.route('/api/monitoring/clear-metrics', methods=['POST'])(controller_clear_metrics)
pclist.route('/api/analytics/patterns', methods=['GET'])(controller_attack_patterns)
pclist.route('/api/analytics/anomalies', methods=['GET'])(controller_detect_anomalies)
pclist.route('/api/analytics/predictions', methods=['GET'])(controller_generate_predictions)
pclist.route('/api/analytics/insights', methods=['GET'])(controller_generate_insights)
pclist.route('/api/ml/train-risk', methods=['POST'])(controller_train_risk_classifier)
pclist.route('/api/ml/train-threat', methods=['POST'])(controller_train_threat_classifier)
pclist.route('/api/ml/train-sector', methods=['POST'])(controller_train_sector_classifier)
pclist.route('/api/ml/predict-risk', methods=['POST'])(controller_predict_risk_level)
pclist.route('/api/ml/predict-threat', methods=['POST'])(controller_predict_threat_actor)
pclist.route('/api/ml/cluster-attacks', methods=['GET'])(controller_cluster_attacks)
pclist.route('/api/ml/model-status', methods=['GET'])(controller_model_status)
pclist.route('/api/ml/predictions', methods=['GET'])(controller_ml_predictions)

# Hafta 7 - Tactical Dashboard API'leri
pclist.route('/api/tactical/threats', methods=['GET'])(controller_tactical_threats)
pclist.route('/api/tactical/attacks', methods=['GET'])(controller_tactical_attacks)
pclist.route('/api/tactical/companies', methods=['GET'])(controller_tactical_companies)

# Analiz API'leri
pclist.route('/api/analytics/trends', methods=['GET'])(controller_analytics_trends)
pclist.route('/api/analytics/anomalies', methods=['GET'])(controller_analytics_anomalies)
pclist.route('/api/analytics/predictions', methods=['GET'])(controller_analytics_predictions)