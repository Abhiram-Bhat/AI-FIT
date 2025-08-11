import pandas as pd
import json
import os
from datetime import datetime
import streamlit as st

def load_workout_data():
    """Load workout data from CSV file"""
    try:
        if os.path.exists('data/workout_data.csv'):
            return pd.read_csv('data/workout_data.csv')
        else:
            # Create default workout data
            create_default_workout_data()
            return pd.read_csv('data/workout_data.csv')
    except Exception as e:
        st.error(f"Error loading workout data: {str(e)}")
        return pd.DataFrame()

def create_default_workout_data():
    """Create default workout dataset"""
    workout_data = {
        'exercise_id': range(1, 51),
        'exercise_name': [
            'Push-ups', 'Squats', 'Lunges', 'Plank', 'Burpees',
            'Jumping Jacks', 'Mountain Climbers', 'Sit-ups', 'Pull-ups', 'Deadlifts',
            'Bench Press', 'Shoulder Press', 'Bicep Curls', 'Tricep Dips', 'Leg Press',
            'Chest Flyes', 'Lat Pulldowns', 'Leg Curls', 'Calf Raises', 'Russian Twists',
            'High Knees', 'Butt Kicks', 'Jump Squats', 'Push-up to T', 'Superman',
            'Wall Sits', 'Side Plank', 'Reverse Lunges', 'Incline Push-ups', 'Glute Bridges',
            'Bear Crawls', 'Frog Jumps', 'Pike Push-ups', 'Single-leg Deadlifts', 'Step-ups',
            'Dumbbell Rows', 'Overhead Squats', 'Turkish Get-ups', 'Kettlebell Swings', 'Box Jumps',
            'Barbell Squats', 'Dips', 'Hammer Curls', 'Cable Flyes', 'Leg Extensions',
            'Face Pulls', 'Hip Thrusts', 'Walking Lunges', 'Battle Ropes', 'Medicine Ball Slams'
        ],
        'muscle_group': [
            'Chest', 'Legs', 'Legs', 'Core', 'Full Body',
            'Cardio', 'Cardio', 'Core', 'Back', 'Back',
            'Chest', 'Shoulders', 'Arms', 'Arms', 'Legs',
            'Chest', 'Back', 'Legs', 'Legs', 'Core',
            'Cardio', 'Cardio', 'Legs', 'Chest', 'Back',
            'Legs', 'Core', 'Legs', 'Chest', 'Glutes',
            'Full Body', 'Legs', 'Shoulders', 'Legs', 'Legs',
            'Back', 'Legs', 'Full Body', 'Full Body', 'Legs',
            'Legs', 'Arms', 'Arms', 'Chest', 'Legs',
            'Back', 'Glutes', 'Legs', 'Cardio', 'Full Body'
        ],
        'difficulty': [
            'Beginner', 'Beginner', 'Intermediate', 'Beginner', 'Advanced',
            'Beginner', 'Intermediate', 'Beginner', 'Advanced', 'Advanced',
            'Intermediate', 'Intermediate', 'Beginner', 'Intermediate', 'Intermediate',
            'Intermediate', 'Intermediate', 'Intermediate', 'Beginner', 'Intermediate',
            'Beginner', 'Beginner', 'Intermediate', 'Intermediate', 'Beginner',
            'Beginner', 'Intermediate', 'Beginner', 'Beginner', 'Beginner',
            'Intermediate', 'Intermediate', 'Intermediate', 'Advanced', 'Intermediate',
            'Intermediate', 'Advanced', 'Advanced', 'Intermediate', 'Advanced',
            'Advanced', 'Intermediate', 'Intermediate', 'Intermediate', 'Intermediate',
            'Intermediate', 'Intermediate', 'Intermediate', 'Advanced', 'Advanced'
        ],
        'equipment': [
            'None', 'None', 'None', 'None', 'None',
            'None', 'None', 'None', 'Pull-up Bar', 'Barbell',
            'Barbell', 'Dumbbells', 'Dumbbells', 'None', 'Machine',
            'Dumbbells', 'Machine', 'Machine', 'None', 'None',
            'None', 'None', 'None', 'None', 'None',
            'None', 'None', 'None', 'None', 'None',
            'None', 'None', 'None', 'Dumbbells', 'None',
            'Dumbbells', 'Barbell', 'Kettlebell', 'Kettlebell', 'Box',
            'Barbell', 'Dip Bar', 'Dumbbells', 'Cable', 'Machine',
            'Cable', 'None', 'None', 'Battle Rope', 'Medicine Ball'
        ],
        'calories_per_minute': [
            8, 10, 9, 5, 15,
            8, 12, 6, 10, 12,
            10, 8, 6, 8, 9,
            7, 9, 7, 4, 7,
            10, 9, 12, 9, 4,
            6, 5, 9, 6, 5,
            11, 13, 8, 10, 8,
            9, 11, 14, 13, 14,
            12, 9, 6, 8, 7,
            7, 8, 9, 16, 14
        ]
    }
    
    os.makedirs('data', exist_ok=True)
    df = pd.DataFrame(workout_data)
    df.to_csv('data/workout_data.csv', index=False)

def save_workout_history(user_id, workout_data):
    """Save workout completion to history"""
    try:
        history_file = 'data/workout_history.json'
        
        # Load existing history
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {}
        
        # Add new workout
        if user_id not in history:
            history[user_id] = []
        
        workout_entry = {
            'date': datetime.now().isoformat(),
            'workout': workout_data,
            'completed': True
        }
        
        history[user_id].append(workout_entry)
        
        # Save updated history
        os.makedirs('data', exist_ok=True)
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return True
        
    except Exception as e:
        st.error(f"Error saving workout history: {str(e)}")
        return False

def load_workout_history(user_id):
    """Load workout history for a specific user"""
    try:
        history_file = 'data/workout_history.json'
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
            return history.get(user_id, [])
        
        return []
        
    except Exception as e:
        st.error(f"Error loading workout history: {str(e)}")
        return []

def get_exercise_details(exercise_name):
    """Get detailed information about a specific exercise"""
    df = load_workout_data()
    
    if df.empty:
        return None
    
    exercise_row = df[df['exercise_name'] == exercise_name]
    
    if exercise_row.empty:
        return None
    
    return exercise_row.iloc[0].to_dict()

def filter_exercises(muscle_group=None, difficulty=None, equipment=None):
    """Filter exercises based on criteria"""
    df = load_workout_data()
    
    if df.empty:
        return df
    
    if muscle_group:
        df = df[df['muscle_group'] == muscle_group]
    
    if difficulty:
        df = df[df['difficulty'] == difficulty]
    
    if equipment:
        df = df[df['equipment'] == equipment]
    
    return df

def calculate_workout_calories(workout, duration_minutes):
    """Calculate estimated calories burned for a workout"""
    total_calories = 0
    df = load_workout_data()
    
    if df.empty:
        return 0
    
    for exercise in workout:
        exercise_name = exercise.get('exercise', '')
        exercise_row = df[df['exercise_name'] == exercise_name]
        
        if not exercise_row.empty:
            calories_per_minute = exercise_row.iloc[0]['calories_per_minute']
            # Estimate time spent on this exercise
            exercise_time = duration_minutes / len(workout)
            total_calories += calories_per_minute * exercise_time
    
    return int(total_calories)
