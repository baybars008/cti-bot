"""
CTI-BOT Export Generator
PDF, Excel, CSV export özellikleri
"""

import pandas as pd
import io
import json
from datetime import datetime, timedelta
from flask import Response, current_app
from models.DBModel import db, Post, HackedCompany
from sqlalchemy import func, desc
import os

class ExportGenerator:
    def __init__(self):
        self.export_dir = 'exports'
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_attacks_to_excel(self, days=30, filters=None):
        """Saldırı verilerini Excel formatında export et"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Veri sorgusu
            query = Post.query.filter(Post.created_at >= start_date)
            
            # Filtreler uygula
            if filters:
                if filters.get('sector'):
                    query = query.filter(Post.sector == filters['sector'])
                if filters.get('country'):
                    query = query.filter(Post.country == filters['country'])
                if filters.get('impact_level'):
                    query = query.filter(Post.impact_level == filters['impact_level'])
            
            attacks = query.all()
            
            # DataFrame oluştur
            data = []
            for attack in attacks:
                data.append({
                    'ID': attack.id,
                    'Başlık': attack.title,
                    'Şirket Adı': attack.company_name,
                    'Sektör': attack.sector,
                    'Ülke': attack.country,
                    'Etki Seviyesi': attack.impact_level,
                    'Tehdit Aktörü': attack.name,
                    'Saldırı Tarihi': attack.hack_date.strftime('%Y-%m-%d') if attack.hack_date else '',
                    'Oluşturulma Tarihi': attack.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Açıklama': attack.description,
                    'Website': attack.website,
                    'Sızıntı URL': attack.post_url
                })
            
            df = pd.DataFrame(data)
            
            # Excel dosyası oluştur
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Saldırılar', index=False)
                
                # İstatistikler sayfası
                stats_data = self._generate_stats_data(attacks)
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='İstatistikler', index=False)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Excel export hatası: {str(e)}")
    
    def export_attacks_to_pdf(self, days=30, filters=None):
        """Saldırı verilerini PDF formatında export et"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Veri sorgusu
            query = Post.query.filter(Post.created_at >= start_date)
            
            # Filtreler uygula
            if filters:
                if filters.get('sector'):
                    query = query.filter(Post.sector == filters['sector'])
                if filters.get('country'):
                    query = query.filter(Post.country == filters['country'])
                if filters.get('impact_level'):
                    query = query.filter(Post.impact_level == filters['impact_level'])
            
            attacks = query.limit(100).all()  # PDF için limit
            
            # PDF oluştur
            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Başlık
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("CTI-BOT Saldırı Raporu", title_style))
            story.append(Spacer(1, 12))
            
            # Tarih aralığı
            date_style = ParagraphStyle(
                'DateRange',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20,
                alignment=1
            )
            story.append(Paragraph(f"Tarih Aralığı: {start_date.strftime('%Y-%m-%d')} - {datetime.utcnow().strftime('%Y-%m-%d')}", date_style))
            story.append(Spacer(1, 20))
            
            # İstatistikler
            stats_data = self._generate_stats_data(attacks)
            story.append(Paragraph("İstatistikler", styles['Heading2']))
            
            stats_table_data = [['Metrik', 'Değer']]
            for stat in stats_data:
                stats_table_data.append([stat['Metrik'], str(stat['Değer'])])
            
            stats_table = Table(stats_table_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 20))
            
            # Saldırı listesi
            story.append(Paragraph("Saldırı Listesi", styles['Heading2']))
            
            # Tablo verileri
            table_data = [['ID', 'Şirket', 'Sektör', 'Ülke', 'Etki', 'Tarih']]
            for attack in attacks:
                table_data.append([
                    str(attack.id),
                    attack.company_name or 'N/A',
                    attack.sector or 'N/A',
                    attack.country or 'N/A',
                    attack.impact_level or 'N/A',
                    attack.hack_date.strftime('%Y-%m-%d') if attack.hack_date else 'N/A'
                ])
            
            # Tablo oluştur
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(table)
            
            # PDF oluştur
            doc.build(story)
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"PDF export hatası: {str(e)}")
    
    def export_attacks_to_csv(self, days=30, filters=None):
        """Saldırı verilerini CSV formatında export et"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Veri sorgusu
            query = Post.query.filter(Post.created_at >= start_date)
            
            # Filtreler uygula
            if filters:
                if filters.get('sector'):
                    query = query.filter(Post.sector == filters['sector'])
                if filters.get('country'):
                    query = query.filter(Post.country == filters['country'])
                if filters.get('impact_level'):
                    query = query.filter(Post.impact_level == filters['impact_level'])
            
            attacks = query.all()
            
            # CSV verisi oluştur
            csv_data = "ID,Başlık,Şirket Adı,Sektör,Ülke,Etki Seviyesi,Tehdit Aktörü,Saldırı Tarihi,Oluşturulma Tarihi,Açıklama,Website,Sızıntı URL\n"
            
            for attack in attacks:
                csv_data += f"{attack.id},{attack.title},{attack.company_name or 'N/A'},{attack.sector or 'N/A'},{attack.country or 'N/A'},{attack.impact_level or 'N/A'},{attack.name or 'N/A'},{attack.hack_date.strftime('%Y-%m-%d') if attack.hack_date else 'N/A'},{attack.created_at.strftime('%Y-%m-%d %H:%M:%S')},{attack.description or 'N/A'},{attack.website or 'N/A'},{attack.post_url or 'N/A'}\n"
            
            return csv_data.encode('utf-8')
            
        except Exception as e:
            raise Exception(f"CSV export hatası: {str(e)}")
    
    def _generate_stats_data(self, attacks):
        """İstatistik verileri oluştur"""
        stats = []
        
        # Toplam saldırı sayısı
        stats.append({'Metrik': 'Toplam Saldırı Sayısı', 'Değer': len(attacks)})
        
        # Benzersiz şirket sayısı
        unique_companies = len(set(attack.company_name for attack in attacks if attack.company_name))
        stats.append({'Metrik': 'Benzersiz Şirket Sayısı', 'Değer': unique_companies})
        
        # Sektör dağılımı
        sectors = {}
        for attack in attacks:
            if attack.sector:
                sectors[attack.sector] = sectors.get(attack.sector, 0) + 1
        
        if sectors:
            top_sector = max(sectors, key=sectors.get)
            stats.append({'Metrik': 'En Çok Hedeflenen Sektör', 'Değer': f"{top_sector} ({sectors[top_sector]} saldırı)"})
        
        # Ülke dağılımı
        countries = {}
        for attack in attacks:
            if attack.country:
                countries[attack.country] = countries.get(attack.country, 0) + 1
        
        if countries:
            top_country = max(countries, key=countries.get)
            stats.append({'Metrik': 'En Çok Hedeflenen Ülke', 'Değer': f"{top_country} ({countries[top_country]} saldırı)"})
        
        # Risk seviyesi dağılımı
        risk_levels = {}
        for attack in attacks:
            if attack.impact_level:
                risk_levels[attack.impact_level] = risk_levels.get(attack.impact_level, 0) + 1
        
        if risk_levels:
            stats.append({'Metrik': 'Risk Seviyesi Dağılımı', 'Değer': str(risk_levels)})
        
        return stats
    
    def export_companies_to_excel(self, days=30, filters=None):
        """Şirket verilerini Excel formatında export et"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Veri sorgusu
            query = HackedCompany.query.filter(HackedCompany.created_at >= start_date)
            
            # Filtreler uygula
            if filters:
                if filters.get('sector'):
                    query = query.filter(HackedCompany.sector == filters['sector'])
                if filters.get('country'):
                    query = query.filter(HackedCompany.country_code == filters['country'])
                if filters.get('company_size'):
                    query = query.filter(HackedCompany.company_size == filters['company_size'])
            
            companies = query.all()
            
            # DataFrame oluştur
            data = []
            for company in companies:
                data.append({
                    'ID': company.id,
                    'Şirket Adı': company.company_name,
                    'Ülke Kodu': company.country_code,
                    'Sektör': company.sector,
                    'Şirket Büyüklüğü': company.company_size,
                    'Saldırı Tarihi': company.hack_date.strftime('%Y-%m-%d') if company.hack_date else '',
                    'Tehdit Aktörü': company.threat_actor,
                    'Sızıntıya Uğrayan Veri': company.data_type_leaked,
                    'Etki Seviyesi': company.impact_level,
                    'Gelir Aralığı': company.revenue_range,
                    'Çalışan Sayısı': company.employee_count,
                    'Website': company.company_website
                })
            
            df = pd.DataFrame(data)
            
            # Excel dosyası oluştur
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Şirketler', index=False)
                
                # İstatistikler sayfası
                stats_data = self._generate_company_stats_data(companies)
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='İstatistikler', index=False)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Excel export hatası: {str(e)}")
    
    def _generate_company_stats_data(self, companies):
        """Şirket istatistik verileri oluştur"""
        stats = []
        
        # Toplam şirket sayısı
        stats.append({'Metrik': 'Toplam Şirket Sayısı', 'Değer': len(companies)})
        
        # Sektör dağılımı
        sectors = {}
        for company in companies:
            if company.sector:
                sectors[company.sector] = sectors.get(company.sector, 0) + 1
        
        if sectors:
            top_sector = max(sectors, key=sectors.get)
            stats.append({'Metrik': 'En Çok Hedeflenen Sektör', 'Değer': f"{top_sector} ({sectors[top_sector]} şirket)"})
        
        # Ülke dağılımı
        countries = {}
        for company in companies:
            if company.country_code:
                countries[company.country_code] = countries.get(company.country_code, 0) + 1
        
        if countries:
            top_country = max(countries, key=countries.get)
            stats.append({'Metrik': 'En Çok Hedeflenen Ülke', 'Değer': f"{top_country} ({countries[top_country]} şirket)"})
        
        # Şirket büyüklüğü dağılımı
        sizes = {}
        for company in companies:
            if company.company_size:
                sizes[company.company_size] = sizes.get(company.company_size, 0) + 1
        
        if sizes:
            stats.append({'Metrik': 'Şirket Büyüklüğü Dağılımı', 'Değer': str(sizes)})
        
        return stats

