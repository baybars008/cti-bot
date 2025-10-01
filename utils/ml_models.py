"""
CTI-BOT Machine Learning Models
Risk prediction, threat classification ve pattern recognition
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
import joblib
import os
from models.DBModel import Post, HackedCompany
from sqlalchemy import func

class MLModels:
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.scaler = StandardScaler()
        self.model_dir = 'ml_models'
        self._ensure_model_dir()
    
    def _ensure_model_dir(self):
        """Model dizinini oluştur"""
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
    
    def prepare_training_data(self, days=90):
        """Eğitim verilerini hazırla"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Verileri al
            attacks = Post.query.filter(
                Post.created_at >= start_date,
                Post.company_name.isnot(None),
                Post.sector.isnot(None),
                Post.country.isnot(None),
                Post.impact_level.isnot(None)
            ).all()
            
            if len(attacks) < 50:
                return None, "Insufficient data for training"
            
            # Veri hazırlama
            data = []
            for attack in attacks:
                data.append({
                    'sector': attack.sector,
                    'country': attack.country,
                    'threat_actor': attack.name,
                    'hour': attack.created_at.hour if attack.created_at else 0,
                    'weekday': attack.created_at.weekday() if attack.created_at else 0,
                    'month': attack.created_at.month if attack.created_at else 0,
                    'impact_level': attack.impact_level,
                    'data_type_leaked': attack.data_type_leaked,
                    'company_size': getattr(attack, 'company_size', 'Unknown')
                })
            
            df = pd.DataFrame(data)
            
            # Kategorik değişkenleri encode et
            categorical_columns = ['sector', 'country', 'threat_actor', 'data_type_leaked', 'company_size']
            for col in categorical_columns:
                if col in df.columns:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    self.encoders[col] = le
            
            return df, None
            
        except Exception as e:
            return None, f"Data preparation error: {str(e)}"
    
    def train_risk_classifier(self, days=90):
        """Risk seviyesi sınıflandırıcısı eğit"""
        try:
            df, error = self.prepare_training_data(days)
            if error:
                return {'error': error}
            
            # Hedef değişken
            y = df['impact_level']
            X = df.drop(['impact_level'], axis=1)
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scaling
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Model eğitimi
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            rf_model.fit(X_train_scaled, y_train)
            
            # Test
            y_pred = rf_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5)
            
            # Model kaydet
            model_path = os.path.join(self.model_dir, 'risk_classifier.pkl')
            joblib.dump(rf_model, model_path)
            
            # Scaler kaydet
            scaler_path = os.path.join(self.model_dir, 'risk_scaler.pkl')
            joblib.dump(self.scaler, scaler_path)
            
            # Encoders kaydet
            encoders_path = os.path.join(self.model_dir, 'risk_encoders.pkl')
            joblib.dump(self.encoders, encoders_path)
            
            self.models['risk_classifier'] = rf_model
            
            return {
                'model_type': 'risk_classifier',
                'accuracy': accuracy,
                'cv_scores': cv_scores.tolist(),
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'feature_importance': dict(zip(X.columns, rf_model.feature_importances_)),
                'model_saved': True
            }
            
        except Exception as e:
            return {'error': f'Risk classifier training error: {str(e)}'}
    
    def train_threat_classifier(self, days=90):
        """Tehdit aktörü sınıflandırıcısı eğit"""
        try:
            df, error = self.prepare_training_data(days)
            if error:
                return {'error': error}
            
            # Hedef değişken
            y = df['threat_actor']
            X = df.drop(['threat_actor'], axis=1)
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scaling
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Model eğitimi
            gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            gb_model.fit(X_train_scaled, y_train)
            
            # Test
            y_pred = gb_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(gb_model, X_train_scaled, y_train, cv=5)
            
            # Model kaydet
            model_path = os.path.join(self.model_dir, 'threat_classifier.pkl')
            joblib.dump(gb_model, model_path)
            
            self.models['threat_classifier'] = gb_model
            
            return {
                'model_type': 'threat_classifier',
                'accuracy': accuracy,
                'cv_scores': cv_scores.tolist(),
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'feature_importance': dict(zip(X.columns, gb_model.feature_importances_)),
                'model_saved': True
            }
            
        except Exception as e:
            return {'error': f'Threat classifier training error: {str(e)}'}
    
    def train_sector_classifier(self, days=90):
        """Sektör sınıflandırıcısı eğit"""
        try:
            df, error = self.prepare_training_data(days)
            if error:
                return {'error': error}
            
            # Hedef değişken
            y = df['sector']
            X = df.drop(['sector'], axis=1)
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scaling
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Model eğitimi
            svm_model = SVC(kernel='rbf', random_state=42)
            svm_model.fit(X_train_scaled, y_train)
            
            # Test
            y_pred = svm_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(svm_model, X_train_scaled, y_train, cv=5)
            
            # Model kaydet
            model_path = os.path.join(self.model_dir, 'sector_classifier.pkl')
            joblib.dump(svm_model, model_path)
            
            self.models['sector_classifier'] = svm_model
            
            return {
                'model_type': 'sector_classifier',
                'accuracy': accuracy,
                'cv_scores': cv_scores.tolist(),
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'model_saved': True
            }
            
        except Exception as e:
            return {'error': f'Sector classifier training error: {str(e)}'}
    
    def predict_risk_level(self, sector, country, threat_actor, hour, weekday, month, data_type_leaked, company_size):
        """Risk seviyesi tahmin et"""
        try:
            # Model yükle
            if 'risk_classifier' not in self.models:
                model_path = os.path.join(self.model_dir, 'risk_classifier.pkl')
                if os.path.exists(model_path):
                    self.models['risk_classifier'] = joblib.load(model_path)
                else:
                    return {'error': 'Risk classifier model not found'}
            
            # Encoders yükle
            encoders_path = os.path.join(self.model_dir, 'risk_encoders.pkl')
            if os.path.exists(encoders_path):
                self.encoders = joblib.load(encoders_path)
            else:
                return {'error': 'Risk encoders not found'}
            
            # Scaler yükle
            scaler_path = os.path.join(self.model_dir, 'risk_scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            else:
                return {'error': 'Risk scaler not found'}
            
            # Veri hazırlama
            data = {
                'sector': sector,
                'country': country,
                'threat_actor': threat_actor,
                'hour': hour,
                'weekday': weekday,
                'month': month,
                'data_type_leaked': data_type_leaked,
                'company_size': company_size
            }
            
            # Encode et
            for col, encoder in self.encoders.items():
                if col in data:
                    try:
                        data[col] = encoder.transform([str(data[col])])[0]
                    except ValueError:
                        data[col] = 0  # Unknown value
            
            # DataFrame oluştur
            df = pd.DataFrame([data])
            
            # Scaling
            df_scaled = self.scaler.transform(df)
            
            # Tahmin
            prediction = self.models['risk_classifier'].predict(df_scaled)[0]
            probabilities = self.models['risk_classifier'].predict_proba(df_scaled)[0]
            
            # Risk seviyeleri
            risk_levels = ['Düşük', 'Orta', 'Yüksek', 'Kritik']
            predicted_risk = risk_levels[prediction] if prediction < len(risk_levels) else 'Bilinmeyen'
            
            return {
                'predicted_risk': predicted_risk,
                'probabilities': dict(zip(risk_levels, probabilities)),
                'confidence': max(probabilities),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Risk prediction error: {str(e)}'}
    
    def predict_threat_actor(self, sector, country, impact_level, hour, weekday, month, data_type_leaked, company_size):
        """Tehdit aktörü tahmin et"""
        try:
            # Model yükle
            if 'threat_classifier' not in self.models:
                model_path = os.path.join(self.model_dir, 'threat_classifier.pkl')
                if os.path.exists(model_path):
                    self.models['threat_classifier'] = joblib.load(model_path)
                else:
                    return {'error': 'Threat classifier model not found'}
            
            # Encoders yükle
            encoders_path = os.path.join(self.model_dir, 'threat_encoders.pkl')
            if os.path.exists(encoders_path):
                self.encoders = joblib.load(encoders_path)
            else:
                return {'error': 'Threat encoders not found'}
            
            # Scaler yükle
            scaler_path = os.path.join(self.model_dir, 'threat_scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            else:
                return {'error': 'Threat scaler not found'}
            
            # Veri hazırlama
            data = {
                'sector': sector,
                'country': country,
                'impact_level': impact_level,
                'hour': hour,
                'weekday': weekday,
                'month': month,
                'data_type_leaked': data_type_leaked,
                'company_size': company_size
            }
            
            # Encode et
            for col, encoder in self.encoders.items():
                if col in data:
                    try:
                        data[col] = encoder.transform([str(data[col])])[0]
                    except ValueError:
                        data[col] = 0  # Unknown value
            
            # DataFrame oluştur
            df = pd.DataFrame([data])
            
            # Scaling
            df_scaled = self.scaler.transform(df)
            
            # Tahmin
            prediction = self.models['threat_classifier'].predict(df_scaled)[0]
            probabilities = self.models['threat_classifier'].predict_proba(df_scaled)[0]
            
            # Tehdit aktörü isimlerini al
            threat_actors = list(self.encoders['threat_actor'].classes_)
            predicted_actor = threat_actors[prediction] if prediction < len(threat_actors) else 'Bilinmeyen'
            
            return {
                'predicted_actor': predicted_actor,
                'probabilities': dict(zip(threat_actors, probabilities)),
                'confidence': max(probabilities),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Threat actor prediction error: {str(e)}'}
    
    def cluster_attacks(self, days=30, n_clusters=5):
        """Saldırıları kümele"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Verileri al
            attacks = Post.query.filter(
                Post.created_at >= start_date,
                Post.company_name.isnot(None),
                Post.sector.isnot(None),
                Post.country.isnot(None)
            ).all()
            
            if len(attacks) < 10:
                return {'error': 'Insufficient data for clustering'}
            
            # Veri hazırlama
            data = []
            for attack in attacks:
                data.append({
                    'sector': attack.sector,
                    'country': attack.country,
                    'hour': attack.created_at.hour if attack.created_at else 0,
                    'weekday': attack.created_at.weekday() if attack.created_at else 0,
                    'month': attack.created_at.month if attack.created_at else 0
                })
            
            df = pd.DataFrame(data)
            
            # Kategorik değişkenleri encode et
            le_sector = LabelEncoder()
            le_country = LabelEncoder()
            df['sector_encoded'] = le_sector.fit_transform(df['sector'])
            df['country_encoded'] = le_country.fit_transform(df['country'])
            
            # Kümeleme için veri hazırla
            X = df[['sector_encoded', 'country_encoded', 'hour', 'weekday', 'month']]
            
            # Scaling
            X_scaled = self.scaler.fit_transform(X)
            
            # K-means kümeleme
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Sonuçları hazırla
            df['cluster'] = clusters
            cluster_summary = df.groupby('cluster').agg({
                'sector': lambda x: x.mode().iloc[0] if not x.empty else 'Unknown',
                'country': lambda x: x.mode().iloc[0] if not x.empty else 'Unknown',
                'hour': 'mean',
                'weekday': 'mean',
                'month': 'mean'
            }).to_dict('index')
            
            return {
                'clusters': cluster_summary,
                'n_clusters': n_clusters,
                'silhouette_score': silhouette_score(X_scaled, clusters),
                'total_attacks': len(attacks),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Clustering error: {str(e)}'}
    
    def get_model_status(self):
        """Model durumunu al"""
        try:
            status = {}
            model_files = [
                'risk_classifier.pkl',
                'threat_classifier.pkl',
                'sector_classifier.pkl',
                'risk_scaler.pkl',
                'threat_scaler.pkl',
                'risk_encoders.pkl',
                'threat_encoders.pkl'
            ]
            
            for model_file in model_files:
                model_path = os.path.join(self.model_dir, model_file)
                status[model_file] = {
                    'exists': os.path.exists(model_path),
                    'size_mb': os.path.getsize(model_path) / (1024 * 1024) if os.path.exists(model_path) else 0,
                    'modified': datetime.fromtimestamp(os.path.getmtime(model_path)).isoformat() if os.path.exists(model_path) else None
                }
            
            return {
                'model_directory': self.model_dir,
                'models': status,
                'total_models': len([m for m in status.values() if m['exists']]),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Model status error: {str(e)}'}

# Global ML models instance
ml_models = MLModels()

