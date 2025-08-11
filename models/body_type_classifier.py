import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os

class BodyTypeClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self._load_or_train_model()
    
    def _generate_training_data(self):
        """Generate synthetic training data for body type classification"""
        np.random.seed(42)
        
        data = []
        
        # Ectomorph characteristics (tall, lean)
        for _ in range(300):
            height = np.random.normal(175, 10)  # cm
            weight = np.random.normal(60, 8)    # kg
            age = np.random.randint(18, 65)
            gender = np.random.choice([0, 1])   # 0: Female, 1: Male
            
            # Adjust for gender
            if gender == 1:  # Male
                height += 5
                weight += 15
            
            bmi = weight / ((height/100) ** 2)
            
            # Ectomorphs typically have lower BMI
            if bmi < 25:
                data.append([height, weight, age, gender, bmi, 'ectomorph'])
        
        # Mesomorph characteristics (athletic build)
        for _ in range(300):
            height = np.random.normal(170, 8)
            weight = np.random.normal(70, 10)
            age = np.random.randint(18, 65)
            gender = np.random.choice([0, 1])
            
            if gender == 1:  # Male
                height += 8
                weight += 20
            
            bmi = weight / ((height/100) ** 2)
            
            # Mesomorphs typically have moderate BMI with muscle
            if 20 <= bmi <= 27:
                data.append([height, weight, age, gender, bmi, 'mesomorph'])
        
        # Endomorph characteristics (rounder build)
        for _ in range(300):
            height = np.random.normal(165, 8)
            weight = np.random.normal(80, 15)
            age = np.random.randint(18, 65)
            gender = np.random.choice([0, 1])
            
            if gender == 1:  # Male
                height += 10
                weight += 25
            
            bmi = weight / ((height/100) ** 2)
            
            # Endomorphs typically have higher BMI
            if bmi >= 23:
                data.append([height, weight, age, gender, bmi, 'endomorph'])
        
        df = pd.DataFrame(data, columns=['height', 'weight', 'age', 'gender', 'bmi', 'body_type'])
        return df
    
    def _load_or_train_model(self):
        """Load existing model or train new one"""
        model_path = 'models/body_type_model.pkl'
        scaler_path = 'models/body_type_scaler.pkl'
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
                return
            except:
                pass
        
        # Train new model
        self._train_model()
    
    def _train_model(self):
        """Train the body type classification model"""
        try:
            # Generate training data
            df = self._generate_training_data()
            
            # Prepare features and target
            X = df[['height', 'weight', 'age', 'gender', 'bmi']].values
            y = df['body_type'].values
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            
            # Save model and scaler
            os.makedirs('models', exist_ok=True)
            with open('models/body_type_model.pkl', 'wb') as f:
                pickle.dump(self.model, f)
            with open('models/body_type_scaler.pkl', 'wb') as f:
                pickle.dump(self.scaler, f)
            
            self.is_trained = True
            
        except Exception as e:
            print(f"Error training body type model: {str(e)}")
            self.is_trained = False
    
    def predict_body_type(self, height, weight, age, gender):
        """Predict body type based on user characteristics"""
        try:
            if not self.is_trained:
                return self._rule_based_classification(height, weight, age, gender)
            
            # Calculate BMI
            bmi = weight / ((height/100) ** 2)
            
            # Prepare features
            gender_encoded = 1 if gender.lower() == 'male' else 0
            features = np.array([[height, weight, age, gender_encoded, bmi]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Get confidence
            confidence = max(probabilities)
            
            return {
                'body_type': prediction,
                'confidence': confidence,
                'probabilities': {
                    class_name: prob 
                    for class_name, prob in zip(self.model.classes_, probabilities)
                }
            }
            
        except Exception as e:
            print(f"Error predicting body type: {str(e)}")
            return self._rule_based_classification(height, weight, age, gender)
    
    def _rule_based_classification(self, height, weight, age, gender):
        """Simple rule-based body type classification as fallback"""
        bmi = weight / ((height/100) ** 2)
        
        if bmi < 20:
            body_type = 'ectomorph'
        elif bmi > 27:
            body_type = 'endomorph'
        else:
            body_type = 'mesomorph'
        
        return {
            'body_type': body_type,
            'confidence': 0.7,  # Default confidence
            'probabilities': {
                'ectomorph': 0.33,
                'mesomorph': 0.34,
                'endomorph': 0.33
            }
        }
    
    def get_body_type_characteristics(self, body_type):
        """Get characteristics and recommendations for each body type"""
        characteristics = {
            'ectomorph': {
                'description': 'Naturally lean and tall with fast metabolism',
                'traits': [
                    'Difficulty gaining weight and muscle',
                    'Fast metabolism',
                    'Narrow shoulders and hips',
                    'Long limbs'
                ],
                'workout_focus': [
                    'Compound movements',
                    'Heavy weights, low reps',
                    'Shorter workouts',
                    'Focus on major muscle groups'
                ],
                'nutrition_tips': [
                    'Eat frequently',
                    'High calorie intake',
                    'Complex carbohydrates',
                    'Protein with every meal'
                ]
            },
            'mesomorph': {
                'description': 'Naturally athletic build with balanced metabolism',
                'traits': [
                    'Gains muscle easily',
                    'Moderate metabolism',
                    'Broad shoulders',
                    'Athletic build'
                ],
                'workout_focus': [
                    'Balanced training',
                    'Mix of cardio and strength',
                    'Variety in exercises',
                    'Progressive overload'
                ],
                'nutrition_tips': [
                    'Balanced macronutrients',
                    'Moderate calorie intake',
                    'Pre and post workout nutrition',
                    'Stay hydrated'
                ]
            },
            'endomorph': {
                'description': 'Naturally rounder build with slower metabolism',
                'traits': [
                    'Gains weight easily',
                    'Slower metabolism',
                    'Wider hips',
                    'Stores fat easily'
                ],
                'workout_focus': [
                    'High intensity cardio',
                    'Circuit training',
                    'Frequent workouts',
                    'Metabolic conditioning'
                ],
                'nutrition_tips': [
                    'Control portions',
                    'Lower carbohydrate intake',
                    'High protein diet',
                    'Frequent small meals'
                ]
            }
        }
        
        return characteristics.get(body_type, characteristics['mesomorph'])
