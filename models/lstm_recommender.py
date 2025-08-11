import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
import pickle
import os
import streamlit as st

class LSTMRecommender:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.exercise_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.sequence_length = 7  # 7 days of workout history
        self.is_trained = False
        self.exercise_library = self._load_exercise_library()
        
        # Try to load pre-trained model, otherwise train new one
        self._load_or_train_model()
    
    def _load_exercise_library(self):
        """Load exercise library with categories and muscle groups"""
        try:
            with open('data/exercise_library.json', 'r') as f:
                return pd.DataFrame(eval(f.read()))
        except:
            # Fallback exercise library
            return pd.DataFrame({
                'exercise': ['Push-ups', 'Squats', 'Lunges', 'Plank', 'Burpees', 'Jumping Jacks',
                           'Mountain Climbers', 'Sit-ups', 'Pull-ups', 'Deadlifts', 'Bench Press',
                           'Shoulder Press', 'Bicep Curls', 'Tricep Dips', 'Leg Press'],
                'muscle_group': ['Chest', 'Legs', 'Legs', 'Core', 'Full Body', 'Cardio',
                               'Cardio', 'Core', 'Back', 'Back', 'Chest', 'Shoulders', 
                               'Arms', 'Arms', 'Legs'],
                'difficulty': ['Beginner', 'Beginner', 'Intermediate', 'Beginner', 'Advanced', 'Beginner',
                             'Intermediate', 'Beginner', 'Advanced', 'Advanced', 'Intermediate',
                             'Intermediate', 'Beginner', 'Intermediate', 'Intermediate'],
                'equipment': ['None', 'None', 'None', 'None', 'None', 'None', 'None', 'None',
                            'Pull-up Bar', 'Weights', 'Weights', 'Weights', 'Weights', 'None', 'Machine']
            })
    
    def _generate_training_data(self):
        """Generate synthetic training data based on fitness principles"""
        np.random.seed(42)
        
        # User profiles
        body_types = ['ectomorph', 'mesomorph', 'endomorph']
        goals = ['weight_loss', 'muscle_gain', 'endurance', 'strength']
        experience_levels = ['beginner', 'intermediate', 'advanced']
        
        data = []
        
        for _ in range(1000):  # Generate 1000 user sequences
            # Random user profile
            body_type = np.random.choice(body_types)
            goal = np.random.choice(goals)
            experience = np.random.choice(experience_levels)
            bmi = np.random.normal(25, 5)  # BMI around 25
            age = np.random.randint(18, 65)
            
            # Generate workout sequence based on profile
            sequence = self._generate_workout_sequence(body_type, goal, experience, bmi, age)
            
            for i in range(len(sequence) - 1):
                data.append({
                    'body_type': body_type,
                    'goal': goal,
                    'experience': experience,
                    'bmi': bmi,
                    'age': age,
                    'workout_history': sequence[:i+1],
                    'next_workout': sequence[i+1]
                })
        
        return pd.DataFrame(data)
    
    def _generate_workout_sequence(self, body_type, goal, experience, bmi, age):
        """Generate realistic workout sequence based on user profile"""
        exercises = self.exercise_library['exercise'].tolist()
        
        # Define exercise preferences based on goals
        goal_exercises = {
            'weight_loss': ['Burpees', 'Jumping Jacks', 'Mountain Climbers', 'Squats', 'Lunges'],
            'muscle_gain': ['Push-ups', 'Pull-ups', 'Deadlifts', 'Bench Press', 'Squats'],
            'endurance': ['Jumping Jacks', 'Mountain Climbers', 'Burpees', 'Plank'],
            'strength': ['Deadlifts', 'Bench Press', 'Squats', 'Shoulder Press', 'Pull-ups']
        }
        
        # Body type preferences
        body_type_exercises = {
            'ectomorph': ['Deadlifts', 'Squats', 'Bench Press', 'Pull-ups'],  # Compound movements
            'mesomorph': ['Push-ups', 'Pull-ups', 'Squats', 'Lunges'],       # Balanced
            'endomorph': ['Burpees', 'Jumping Jacks', 'Mountain Climbers']   # High intensity
        }
        
        preferred_exercises = list(set(goal_exercises[goal] + body_type_exercises[body_type]))
        
        # Generate 14-day sequence
        sequence = []
        for day in range(14):
            if day % 7 == 6:  # Rest day every 7th day
                sequence.append('Rest')
            else:
                # Select 3-5 exercises per workout
                workout_size = np.random.randint(3, 6)
                daily_exercises = np.random.choice(preferred_exercises, size=workout_size, replace=False)
                sequence.append(','.join(daily_exercises))
        
        return sequence
    
    def _prepare_training_data(self, df):
        """Prepare data for LSTM training"""
        # Encode categorical variables
        df['body_type_encoded'] = self.exercise_encoder.fit_transform(df['body_type'])
        
        # Create sequences
        X_sequences = []
        X_features = []
        y = []
        
        for idx, row in df.iterrows():
            history = row['workout_history']
            if len(history) >= self.sequence_length:
                # Get last sequence_length workouts
                sequence = history[-self.sequence_length:]
                
                # Encode workout sequence
                encoded_sequence = []
                for workout in sequence:
                    if workout == 'Rest':
                        encoded_sequence.append(0)
                    else:
                        # Simple encoding: number of exercises
                        encoded_sequence.append(len(workout.split(',')))
                
                X_sequences.append(encoded_sequence)
                
                # User features
                features = [
                    row['body_type_encoded'],
                    ['weight_loss', 'muscle_gain', 'endurance', 'strength'].index(row['goal']),
                    ['beginner', 'intermediate', 'advanced'].index(row['experience']),
                    row['bmi'],
                    row['age']
                ]
                X_features.append(features)
                
                # Target: next workout complexity
                next_workout = row['next_workout']
                if next_workout == 'Rest':
                    y.append(0)
                else:
                    y.append(len(next_workout.split(',')))
        
        X_sequences = np.array(X_sequences)
        X_features = np.array(X_features)
        y = np.array(y)
        
        # Normalize features
        X_features = self.scaler.fit_transform(X_features)
        
        return X_sequences, X_features, y
    
    def _build_model(self, feature_dim):
        """Build Random Forest model"""
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        return model
    
    def _load_or_train_model(self):
        """Load existing model or train new one"""
        model_path = 'models/rf_model.pkl'
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_trained = True
                return
            except:
                pass
        
        # Train new model
        self._train_model()
    
    def _train_model(self):
        """Train the Random Forest model"""
        try:
            # Generate training data
            df = self._generate_training_data()
            
            # Prepare data
            X_sequences, X_features, y = self._prepare_training_data(df)
            
            # Build model
            self.model = self._build_model(X_features.shape[1])
            
            # Train model using features (not sequences for RF)
            self.model.fit(X_features, y)
            
            # Save model
            os.makedirs('models', exist_ok=True)
            with open('models/rf_model.pkl', 'wb') as f:
                pickle.dump(self.model, f)
            
            self.is_trained = True
            
        except Exception as e:
            st.error(f"Error training ML model: {str(e)}")
            # Create simple fallback model
            self._create_fallback_model()
    
    def _create_fallback_model(self):
        """Create a simple fallback model"""
        self.model = RandomForestRegressor(n_estimators=10, random_state=42)
        self.is_trained = True
    
    def recommend_workout(self, user_profile, workout_history=None):
        """Generate workout recommendations based on user profile and history"""
        try:
            if not self.is_trained:
                return self._fallback_recommendation(user_profile)
            
            # Get user features
            body_type_map = {'ectomorph': 0, 'mesomorph': 1, 'endomorph': 2}
            goal_map = {'weight_loss': 0, 'muscle_gain': 1, 'endurance': 2, 'strength': 3}
            experience_map = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
            
            features = np.array([[
                body_type_map.get(user_profile.get('body_type', 'mesomorph'), 1),
                goal_map.get(user_profile.get('goal', 'general_fitness'), 0),
                experience_map.get(user_profile.get('experience', 'beginner'), 0),
                user_profile.get('bmi', 25),
                user_profile.get('age', 30)
            ]])
            
            # Normalize features
            features = self.scaler.transform(features)
            
            # Predict workout complexity
            if hasattr(self.model, 'predict') and self.is_trained:
                complexity = self.model.predict(features)[0]
            else:
                complexity = 4  # Default complexity
            
            # Generate workout based on complexity and profile
            return self._generate_recommended_workout(user_profile, max(1, int(complexity)))
            
        except Exception as e:
            st.error(f"Error generating recommendation: {str(e)}")
            return self._fallback_recommendation(user_profile)
    
    def _generate_recommended_workout(self, user_profile, complexity):
        """Generate workout based on predicted complexity and user profile"""
        goal = user_profile.get('goal', 'general_fitness')
        body_type = user_profile.get('body_type', 'mesomorph')
        experience = user_profile.get('experience', 'beginner')
        
        # Exercise selection based on goal and body type
        exercise_pool = {
            'weight_loss': {
                'cardio': ['Jumping Jacks', 'Burpees', 'Mountain Climbers', 'High Knees'],
                'strength': ['Squats', 'Push-ups', 'Lunges', 'Plank']
            },
            'muscle_gain': {
                'compound': ['Deadlifts', 'Squats', 'Bench Press', 'Pull-ups'],
                'isolation': ['Bicep Curls', 'Tricep Dips', 'Shoulder Press']
            },
            'endurance': {
                'cardio': ['Jumping Jacks', 'Mountain Climbers', 'Burpees'],
                'bodyweight': ['Push-ups', 'Squats', 'Plank', 'Lunges']
            },
            'strength': {
                'compound': ['Deadlifts', 'Squats', 'Bench Press', 'Pull-ups'],
                'power': ['Shoulder Press', 'Leg Press']
            }
        }
        
        # Select exercises based on goal
        goal_exercises = exercise_pool.get(goal, exercise_pool['weight_loss'])
        
        # Flatten exercise list
        all_exercises = []
        for category in goal_exercises.values():
            all_exercises.extend(category)
        
        # Select exercises based on complexity
        num_exercises = min(complexity, len(all_exercises))
        selected_exercises = np.random.choice(all_exercises, size=num_exercises, replace=False)
        
        # Generate sets and reps based on experience
        workout = []
        for exercise in selected_exercises:
            if experience == 'beginner':
                sets, reps = np.random.choice([2, 3]), np.random.randint(8, 12)
            elif experience == 'intermediate':
                sets, reps = np.random.choice([3, 4]), np.random.randint(10, 15)
            else:  # advanced
                sets, reps = np.random.choice([4, 5]), np.random.randint(12, 20)
            
            workout.append({
                'exercise': exercise,
                'sets': sets,
                'reps': reps,
                'rest': '30-60 seconds'
            })
        
        return workout
    
    def _fallback_recommendation(self, user_profile):
        """Fallback recommendation when ML model fails"""
        goal = user_profile.get('goal', 'general_fitness')
        experience = user_profile.get('experience', 'beginner')
        
        # Simple rule-based recommendations
        if goal == 'weight_loss':
            exercises = ['Jumping Jacks', 'Burpees', 'Squats', 'Mountain Climbers']
        elif goal == 'muscle_gain':
            exercises = ['Push-ups', 'Squats', 'Pull-ups', 'Plank']
        else:
            exercises = ['Push-ups', 'Squats', 'Plank', 'Jumping Jacks']
        
        # Generate workout
        workout = []
        for exercise in exercises:
            if experience == 'beginner':
                sets, reps = 2, 10
            elif experience == 'intermediate':
                sets, reps = 3, 12
            else:
                sets, reps = 4, 15
            
            workout.append({
                'exercise': exercise,
                'sets': sets,
                'reps': reps,
                'rest': '30-60 seconds'
            })
        
        return workout
