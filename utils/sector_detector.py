# Sektör Tespit Algoritması
# Şirket adı, website ve diğer bilgilere göre sektör tespiti yapar

import re
import json
from typing import Dict, List, Optional, Tuple

class SectorDetector:
    def __init__(self):
        self.sector_keywords = {
            'finans': [
                'bank', 'banka', 'finance', 'finans', 'credit', 'kredi', 'loan', 'kredi',
                'insurance', 'sigorta', 'investment', 'yatırım', 'capital', 'sermaye',
                'payment', 'ödeme', 'card', 'kart', 'money', 'para', 'currency', 'döviz',
                'crypto', 'kripto', 'bitcoin', 'ethereum', 'wallet', 'cüzdan'
            ],
            'sağlık': [
                'health', 'sağlık', 'medical', 'tıbbi', 'hospital', 'hastane', 'clinic',
                'klinik', 'pharmacy', 'eczane', 'drug', 'ilaç', 'medicine', 'tıp',
                'doctor', 'doktor', 'nurse', 'hemşire', 'patient', 'hasta', 'treatment',
                'tedavi', 'therapy', 'terapi', 'surgery', 'cerrahi', 'dental', 'diş'
            ],
            'eğitim': [
                'education', 'eğitim', 'school', 'okul', 'university', 'üniversite',
                'college', 'kolej', 'academy', 'akademi', 'institute', 'enstitü',
                'training', 'eğitim', 'course', 'kurs', 'student', 'öğrenci', 'teacher',
                'öğretmen', 'professor', 'profesör', 'research', 'araştırma', 'study',
                'çalışma', 'learning', 'öğrenme', 'knowledge', 'bilgi'
            ],
            'teknoloji': [
                'tech', 'teknoloji', 'software', 'yazılım', 'hardware', 'donanım',
                'computer', 'bilgisayar', 'internet', 'web', 'ağ', 'network', 'network',
                'data', 'veri', 'cloud', 'bulut', 'ai', 'artificial', 'yapay', 'intelligence',
                'machine', 'makine', 'learning', 'öğrenme', 'mobile', 'mobil', 'app',
                'uygulama', 'digital', 'dijital', 'cyber', 'siber', 'security', 'güvenlik'
            ],
            'e-ticaret': [
                'ecommerce', 'e-ticaret', 'shop', 'mağaza', 'store', 'dükkan', 'market',
                'pazar', 'retail', 'perakende', 'wholesale', 'toptan', 'sale', 'satış',
                'buy', 'satın', 'sell', 'sat', 'product', 'ürün', 'service', 'hizmet',
                'customer', 'müşteri', 'order', 'sipariş', 'delivery', 'teslimat'
            ],
            'enerji': [
                'energy', 'enerji', 'power', 'güç', 'electric', 'elektrik', 'gas', 'gaz',
                'oil', 'petrol', 'fuel', 'yakıt', 'renewable', 'yenilenebilir', 'solar',
                'güneş', 'wind', 'rüzgar', 'nuclear', 'nükleer', 'coal', 'kömür',
                'electricity', 'elektrik', 'utility', 'hizmet'
            ],
            'ulaştırma': [
                'transport', 'ulaştırma', 'logistics', 'lojistik', 'shipping', 'nakliye',
                'delivery', 'teslimat', 'cargo', 'kargo', 'freight', 'yük', 'truck',
                'kamyon', 'car', 'araç', 'vehicle', 'taşıt', 'airline', 'havayolu',
                'railway', 'demiryolu', 'port', 'liman', 'airport', 'havaalanı'
            ],
            'turizm': [
                'tourism', 'turizm', 'travel', 'seyahat', 'hotel', 'otel', 'restaurant',
                'restoran', 'tourism', 'turizm', 'vacation', 'tatil', 'holiday', 'bayram',
                'trip', 'gezi', 'journey', 'yolculuk', 'accommodation', 'konaklama',
                'booking', 'rezervasyon', 'ticket', 'bilet', 'flight', 'uçuş'
            ],
            'gayrimenkul': [
                'real estate', 'gayrimenkul', 'property', 'mülk', 'house', 'ev',
                'apartment', 'apartman', 'building', 'bina', 'construction', 'inşaat',
                'development', 'geliştirme', 'rent', 'kira', 'sale', 'satış',
                'investment', 'yatırım', 'land', 'arazi', 'commercial', 'ticari'
            ],
            'medya': [
                'media', 'medya', 'news', 'haber', 'tv', 'televizyon', 'radio', 'radyo',
                'newspaper', 'gazete', 'magazine', 'dergi', 'publishing', 'yayıncılık',
                'broadcast', 'yayın', 'entertainment', 'eğlence', 'film', 'movie',
                'cinema', 'sinema', 'music', 'müzik', 'art', 'sanat', 'culture', 'kültür'
            ]
        }
        
        self.company_size_keywords = {
            'küçük': ['startup', 'başlangıç', 'küçük', 'small', 'mini', 'micro'],
            'orta': ['orta', 'medium', 'mid', 'orta ölçek', 'medium-sized'],
            'büyük': ['büyük', 'large', 'enterprise', 'kurumsal', 'corporate', 'global', 'küresel']
        }
        
        self.impact_keywords = {
            'düşük': ['minor', 'küçük', 'low', 'düşük', 'minimal', 'minimal'],
            'orta': ['medium', 'orta', 'moderate', 'orta düzey', 'moderate'],
            'yüksek': ['high', 'yüksek', 'major', 'büyük', 'significant', 'önemli'],
            'kritik': ['critical', 'kritik', 'severe', 'ciddi', 'catastrophic', 'felaket']
        }

    def detect_sector(self, company_name: str, website: str = "", description: str = "") -> str:
        """
        Şirket adı, website ve açıklamaya göre sektör tespiti yapar
        """
        text_to_analyze = f"{company_name} {website} {description}".lower()
        
        sector_scores = {}
        
        for sector, keywords in self.sector_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    score += 1
            sector_scores[sector] = score
        
        # En yüksek skorlu sektörü döndür
        if sector_scores:
            best_sector = max(sector_scores, key=sector_scores.get)
            if sector_scores[best_sector] > 0:
                return best_sector
        
        return 'diğer'

    def detect_company_size(self, company_name: str, website: str = "", description: str = "") -> str:
        """
        Şirket büyüklüğünü tespit eder
        """
        text_to_analyze = f"{company_name} {website} {description}".lower()
        
        for size, keywords in self.company_size_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    return size
        
        return 'orta'  # Varsayılan olarak orta

    def detect_impact_level(self, title: str, description: str = "") -> str:
        """
        Saldırının etki seviyesini tespit eder
        """
        text_to_analyze = f"{title} {description}".lower()
        
        for impact, keywords in self.impact_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    return impact
        
        return 'orta'  # Varsayılan olarak orta

    def detect_data_type(self, title: str, description: str = "") -> str:
        """
        Sızıntıya uğrayan veri türünü tespit eder
        """
        text_to_analyze = f"{title} {description}".lower()
        
        data_types = {
            'kişisel': ['personal', 'kişisel', 'identity', 'kimlik', 'name', 'isim', 'address', 'adres', 'phone', 'telefon'],
            'finansal': ['financial', 'finansal', 'credit', 'kredi', 'card', 'kart', 'bank', 'banka', 'money', 'para'],
            'ticari': ['commercial', 'ticari', 'business', 'iş', 'trade', 'ticaret', 'customer', 'müşteri', 'client', 'müvekkil'],
            'sağlık': ['health', 'sağlık', 'medical', 'tıbbi', 'patient', 'hasta', 'healthcare', 'sağlık hizmeti'],
            'eğitim': ['education', 'eğitim', 'student', 'öğrenci', 'academic', 'akademik', 'school', 'okul']
        }
        
        for data_type, keywords in data_types.items():
            for keyword in keywords:
                if keyword.lower() in text_to_analyze:
                    return data_type
        
        return 'genel'

    def extract_company_name(self, title: str, website: str = "") -> str:
        """
        Başlıktan şirket adını çıkarır
        """
        # Yaygın kelimeleri temizle
        common_words = ['data', 'breach', 'hack', 'leak', 'sızıntı', 'veri', 'ihlal', 'saldırı']
        
        # Website'den domain adını çıkar
        if website and website != "None":
            try:
                from urllib.parse import urlparse
                domain = urlparse(website).netloc
                if domain:
                    # www. ve .com gibi uzantıları temizle
                    domain = domain.replace('www.', '').split('.')[0]
                    return domain.title()
            except:
                pass
        
        # Başlıktan şirket adını çıkar
        title_clean = title
        for word in common_words:
            title_clean = title_clean.replace(word, '')
        
        # İlk kelimeyi şirket adı olarak al
        words = title_clean.split()
        if words:
            return words[0].title()
        
        return title

    def analyze_post(self, post_data: dict) -> dict:
        """
        Post verilerini analiz eder ve zenginleştirilmiş veri döndürür
        """
        title = post_data.get('title', '')
        website = post_data.get('website', '')
        description = post_data.get('description', '')
        country = post_data.get('country', '')
        
        # Şirket adını çıkar
        company_name = self.extract_company_name(title, website)
        
        # Sektör tespiti
        sector = self.detect_sector(company_name, website, description)
        
        # Şirket büyüklüğü tespiti
        company_size = self.detect_company_size(company_name, website, description)
        
        # Etki seviyesi tespiti
        impact_level = self.detect_impact_level(title, description)
        
        # Veri türü tespiti
        data_type = self.detect_data_type(title, description)
        
        # Gelir aralığı tahmini (şirket büyüklüğüne göre)
        revenue_ranges = {
            'küçük': '0-1M',
            'orta': '1M-10M',
            'büyük': '10M-100M'
        }
        revenue_range = revenue_ranges.get(company_size, '1M-10M')
        
        # Çalışan sayısı tahmini
        employee_counts = {
            'küçük': 50,
            'orta': 500,
            'büyük': 5000
        }
        employee_count = employee_counts.get(company_size, 500)
        
        return {
            'company_name': company_name,
            'sector': sector,
            'company_size': company_size,
            'impact_level': impact_level,
            'data_type_leaked': data_type,
            'revenue_range': revenue_range,
            'employee_count': employee_count,
            'industry_category': sector  # Şimdilik sektör ile aynı
        }

# Kullanım örneği
if __name__ == "__main__":
    detector = SectorDetector()
    
    # Test verisi
    test_post = {
        'title': 'Turkish Bank Data Breach Exposes Customer Information',
        'website': 'https://turkishbank.com.tr',
        'description': 'A major Turkish bank has suffered a data breach affecting millions of customers',
        'country': 'TR'
    }
    
    result = detector.analyze_post(test_post)
    print(json.dumps(result, indent=2, ensure_ascii=False))

