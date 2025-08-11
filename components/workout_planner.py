import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from models.lstm_recommender import LSTMRecommender
from utils.youtube_api import youtube_api
from utils.data_loader import calculate_workout_calories
import random

def render_workout_planner():
    """Render workout planning interface"""
    st.title("🏋️ AI Workout Planner")
    
    # Check if user has profile
    if not st.session_state.user_profile or 'bmi' not in st.session_state.user_profile:
        st.warning("⚠️ Please calculate your BMI first!")
        if st.button("Go to BMI Calculator"):
            st.session_state.page = "BMI Calculator"
            st.rerun()
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_workout_preferences()
    
    with col2:
        render_workout_display()

def render_workout_preferences():
    """Render workout preference settings"""
    st.subheader("🎯 Workout Preferences")
    
    # Workout type selection
    workout_type = st.selectbox(
        "Workout Focus",
        ["AI Recommended", "Strength Training", "Cardio", "HIIT", "Flexibility", "Full Body"],
        index=0
    )
    
    # Duration
    duration = st.slider(
        "Workout Duration (minutes)",
        min_value=15,
        max_value=90,
        value=st.session_state.user_profile.get('workout_duration', 45),
        step=5
    )
    
    # Intensity
    intensity = st.selectbox(
        "Intensity Level",
        ["Beginner", "Intermediate", "Advanced"],
        index=["Beginner", "Intermediate", "Advanced"].index(
            st.session_state.user_profile.get('experience', 'Beginner')
        )
    )
    
    # Equipment available
    equipment = st.multiselect(
        "Available Equipment",
        ["None (Bodyweight)", "Dumbbells", "Barbell", "Resistance Bands", "Pull-up Bar", "Kettlebell", "Machine"],
        default=["None (Bodyweight)"]
    )
    
    # Target muscle groups
    muscle_groups = st.multiselect(
        "Target Muscle Groups",
        ["Chest", "Back", "Shoulders", "Arms", "Legs", "Core", "Glutes", "Cardio"],
        default=["Full Body"]
    )
    
    # Generate workout button
    if st.button("🔥 Generate AI Workout", type="primary"):
        generate_workout(workout_type, duration, intensity, equipment, muscle_groups)

def generate_workout(workout_type, duration, intensity, equipment, muscle_groups):
    """Generate workout using LSTM model"""
    try:
        with st.spinner("🤖 AI is creating your personalized workout..."):
            # Update user profile with current preferences
            st.session_state.user_profile.update({
                'workout_duration': duration,
                'experience': intensity,
                'equipment': equipment,
                'target_muscles': muscle_groups
            })
            
            # Use LSTM recommender if available
            if st.session_state.models_loaded:
                recommender = st.session_state.lstm_recommender
                
                # Prepare user profile for recommendation
                user_profile = st.session_state.user_profile.copy()
                user_profile['goal'] = map_workout_type_to_goal(workout_type)
                
                # Get workout recommendation
                workout_exercises = recommender.recommend_workout(
                    user_profile, 
                    st.session_state.workout_history[-7:] if st.session_state.workout_history else None
                )
                
                # Create complete workout plan
                workout_plan = {
                    'type': workout_type,
                    'duration': duration,
                    'intensity': intensity,
                    'goal': user_profile['goal'],
                    'focus': ', '.join(muscle_groups) if muscle_groups else 'Full Body',
                    'exercises': workout_exercises,
                    'estimated_calories': calculate_workout_calories(workout_exercises, duration),
                    'generated_at': datetime.now().isoformat()
                }
                
            else:
                # Fallback workout generation
                workout_plan = generate_fallback_workout(workout_type, duration, intensity, equipment, muscle_groups)
            
            # Store in session state
            st.session_state.current_workout = workout_plan
            
        st.success("✅ Workout generated successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error generating workout: {str(e)}")
        # Generate fallback workout
        workout_plan = generate_fallback_workout(workout_type, duration, intensity, equipment, muscle_groups)
        st.session_state.current_workout = workout_plan
        st.rerun()

def render_workout_display():
    """Display current workout plan"""
    if not st.session_state.current_workout:
        st.info("👈 Configure your preferences and generate a workout!")
        
        # Show sample workout structure
        render_sample_workout()
        return
    
    workout = st.session_state.current_workout
    
    # Workout header
    st.subheader(f"🔥 {workout['type']} Workout")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric("Duration", f"{workout['duration']} min")
    with col_b:
        st.metric("Exercises", len(workout['exercises']))
    with col_c:
        st.metric("Est. Calories", f"{workout['estimated_calories']}")
    
    # Workout details
    st.write(f"**Focus:** {workout['focus']}")
    st.write(f"**Intensity:** {workout['intensity']}")
    
    # Exercise list
    st.subheader("📋 Exercise Plan")
    
    for i, exercise in enumerate(workout['exercises'], 1):
        with st.expander(f"Exercise {i}: {exercise['exercise']}", expanded=True):
            col_x, col_y, col_z = st.columns([2, 1, 1])
            
            with col_x:
                st.write(f"**Sets:** {exercise['sets']}")
                st.write(f"**Reps:** {exercise['reps']}")
                st.write(f"**Rest:** {exercise['rest']}")
            
            with col_y:
                # YouTube video button
                if st.button(f"📹 Watch Demo", key=f"video_{i}"):
                    show_exercise_video(exercise['exercise'])
            
            with col_z:
                # Mark exercise complete
                if st.button(f"✅ Complete", key=f"complete_{i}"):
                    mark_exercise_complete(i-1)
    
    # Workout actions
    st.subheader("🚀 Workout Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏃 Start Workout", type="primary"):
            start_workout_session()
    
    with col2:
        if st.button("📹 Use Pose Detection"):
            st.session_state.page = "Pose Detection"
            st.rerun()
    
    with col3:
        if st.button("✅ Mark Complete"):
            complete_workout()

def show_exercise_video(exercise_name):
    """Show YouTube video for exercise"""
    with st.spinner("🔍 Finding instructional videos..."):
        videos = youtube_api.search_workout_videos(exercise_name, max_results=3)
        
        if videos:
            st.subheader(f"📹 {exercise_name} - Instructional Videos")
            
            for video in videos:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if video['thumbnail']:
                        st.image(video['thumbnail'], width=150)
                
                with col2:
                    st.write(f"**{video['title']}**")
                    st.write(f"*by {video['channel']}*")
                    st.write(video['description'][:100] + "...")
                    
                    if video['embed_url']:
                        if st.button(f"▶️ Play Video", key=f"play_{video['video_id']}"):
                            st.video(video['embed_url'])
                    else:
                        st.link_button("🔗 Watch on YouTube", video['url'])
                
                st.divider()
        else:
            st.warning("No instructional videos found for this exercise.")

def start_workout_session():
    """Start a timed workout session"""
    if 'workout_session' not in st.session_state:
        st.session_state.workout_session = {
            'started': True,
            'start_time': datetime.now(),
            'current_exercise': 0,
            'completed_exercises': []
        }
        st.success("🏃 Workout session started! Timer is running.")
        st.rerun()

def mark_exercise_complete(exercise_index):
    """Mark a specific exercise as complete"""
    if 'workout_session' not in st.session_state:
        st.session_state.workout_session = {
            'started': True,
            'start_time': datetime.now(),
            'current_exercise': 0,
            'completed_exercises': []
        }
    
    if exercise_index not in st.session_state.workout_session['completed_exercises']:
        st.session_state.workout_session['completed_exercises'].append(exercise_index)
        st.success(f"✅ Exercise {exercise_index + 1} completed!")
        
        # Check if all exercises are complete
        total_exercises = len(st.session_state.current_workout['exercises'])
        if len(st.session_state.workout_session['completed_exercises']) == total_exercises:
            st.balloons()
            st.success("🎉 All exercises completed! Great job!")

def complete_workout():
    """Mark entire workout as complete"""
    if st.session_state.current_workout:
        workout_data = st.session_state.current_workout.copy()
        workout_data['date'] = datetime.now().isoformat()
        workout_data['completed'] = True
        
        # Calculate actual duration if session was started
        if 'workout_session' in st.session_state and st.session_state.workout_session.get('started'):
            start_time = st.session_state.workout_session['start_time']
            actual_duration = (datetime.now() - start_time).total_seconds() / 60
            workout_data['actual_duration'] = actual_duration
        
        # Add to history
        st.session_state.workout_history.append(workout_data)
        
        # Clear current workout and session
        st.session_state.current_workout = None
        if 'workout_session' in st.session_state:
            del st.session_state.workout_session
        
        st.success("🎉 Workout completed and added to history!")
        st.balloons()
        
        # Show completion stats
        st.metric("Workout Duration", f"{workout_data.get('actual_duration', workout_data['duration']):.0f} minutes")
        st.metric("Exercises Completed", len(workout_data['exercises']))
        st.metric("Calories Burned", f"~{workout_data['estimated_calories']}")
        
        if st.button("🏠 Return to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()

def render_sample_workout():
    """Render a sample workout structure"""
    st.subheader("📋 Sample Workout Structure")
    
    sample_exercises = [
        {"exercise": "Push-ups", "sets": 3, "reps": 12, "rest": "30 seconds"},
        {"exercise": "Squats", "sets": 3, "reps": 15, "rest": "30 seconds"},
        {"exercise": "Plank", "sets": 3, "reps": "30 seconds", "rest": "30 seconds"},
        {"exercise": "Jumping Jacks", "sets": 3, "reps": 20, "rest": "30 seconds"}
    ]
    
    for i, exercise in enumerate(sample_exercises, 1):
        st.write(f"**{i}. {exercise['exercise']}**")
        st.write(f"   Sets: {exercise['sets']} | Reps: {exercise['reps']} | Rest: {exercise['rest']}")

def map_workout_type_to_goal(workout_type):
    """Map workout type to fitness goal for LSTM model"""
    mapping = {
        "Strength Training": "muscle_gain",
        "Cardio": "weight_loss", 
        "HIIT": "weight_loss",
        "Flexibility": "endurance",
        "Full Body": "general_fitness",
        "AI Recommended": "general_fitness"
    }
    return mapping.get(workout_type, "general_fitness")

def generate_fallback_workout(workout_type, duration, intensity, equipment, muscle_groups):
    """Generate fallback workout when AI model is not available"""
    # Basic exercise library
    exercise_library = {
        "Chest": [
            {"exercise": "Push-ups", "equipment": "None"},
            {"exercise": "Incline Push-ups", "equipment": "None"},
            {"exercise": "Chest Press", "equipment": "Dumbbells"}
        ],
        "Legs": [
            {"exercise": "Squats", "equipment": "None"},
            {"exercise": "Lunges", "equipment": "None"},
            {"exercise": "Jump Squats", "equipment": "None"}
        ],
        "Core": [
            {"exercise": "Plank", "equipment": "None"},
            {"exercise": "Sit-ups", "equipment": "None"},
            {"exercise": "Russian Twists", "equipment": "None"}
        ],
        "Back": [
            {"exercise": "Pull-ups", "equipment": "Pull-up Bar"},
            {"exercise": "Superman", "equipment": "None"},
            {"exercise": "Bent-over Rows", "equipment": "Dumbbells"}
        ],
        "Arms": [
            {"exercise": "Tricep Dips", "equipment": "None"},
            {"exercise": "Bicep Curls", "equipment": "Dumbbells"},
            {"exercise": "Pike Push-ups", "equipment": "None"}
        ],
        "Cardio": [
            {"exercise": "Jumping Jacks", "equipment": "None"},
            {"exercise": "Burpees", "equipment": "None"},
            {"exercise": "High Knees", "equipment": "None"}
        ]
    }
    
    # Select exercises based on muscle groups and equipment
    selected_exercises = []
    target_groups = muscle_groups if muscle_groups else ["Chest", "Legs", "Core", "Cardio"]
    
    for group in target_groups:
        if group in exercise_library:
            available_exercises = [
                ex for ex in exercise_library[group] 
                if ex["equipment"] in equipment or ex["equipment"] == "None"
            ]
            if available_exercises:
                selected_exercises.extend(random.sample(
                    available_exercises, 
                    min(2, len(available_exercises))
                ))
    
    # Create workout plan
    workout_exercises = []
    for exercise in selected_exercises:
        # Adjust sets/reps based on intensity
        if intensity == "Beginner":
            sets, reps = 2, 10
        elif intensity == "Intermediate":
            sets, reps = 3, 12
        else:  # Advanced
            sets, reps = 4, 15
        
        workout_exercises.append({
            "exercise": exercise["exercise"],
            "sets": sets,
            "reps": reps,
            "rest": "30-60 seconds"
        })
    
    # Ensure minimum number of exercises
    if len(workout_exercises) < 4:
        basic_exercises = [
            {"exercise": "Push-ups", "sets": 3, "reps": 12, "rest": "30 seconds"},
            {"exercise": "Squats", "sets": 3, "reps": 15, "rest": "30 seconds"},
            {"exercise": "Plank", "sets": 3, "reps": "30 seconds", "rest": "30 seconds"},
            {"exercise": "Jumping Jacks", "sets": 3, "reps": 20, "rest": "30 seconds"}
        ]
        workout_exercises = basic_exercises
    
    return {
        'type': workout_type,
        'duration': duration,
        'intensity': intensity,
        'goal': map_workout_type_to_goal(workout_type),
        'focus': ', '.join(muscle_groups) if muscle_groups else 'Full Body',
        'exercises': workout_exercises,
        'estimated_calories': calculate_workout_calories(workout_exercises, duration),
        'generated_at': datetime.now().isoformat()
    }
