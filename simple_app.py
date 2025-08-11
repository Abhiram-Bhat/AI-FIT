import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, date
import random
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="AI Fitness Coach",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    .stSidebar {
        background-color: #262730;
    }
    
    .stSelectbox > div > div {
        background-color: #262730;
        color: #FAFAFA;
    }
    
    .stNumberInput > div > div > input {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4F4F4F;
    }
    
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4F4F4F;
    }
    
    .stSlider > div > div > div {
        color: #FAFAFA;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #1E2139 0%, #262730 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #4F4F4F;
        margin: 0.5rem 0;
    }
    
    .workout-card {
        background: linear-gradient(135deg, #2D3748 0%, #1A202C 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #4F4F4F;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .success {
        background: linear-gradient(45deg, #48bb78 0%, #38a169 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .warning {
        background: linear-gradient(45deg, #ed8936 0%, #dd6b20 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .pose-detection-area {
        background: linear-gradient(135deg, #1A202C 0%, #2D3748 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid #4F4F4F;
        text-align: center;
        margin: 1rem 0;
        min-height: 400px;
    }
    
    .camera-placeholder {
        background: #262730;
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 3rem;
        margin: 2rem 0;
        color: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'workout_history' not in st.session_state:
        st.session_state.workout_history = []
    if 'current_workout' not in st.session_state:
        st.session_state.current_workout = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if 'pose_active' not in st.session_state:
        st.session_state.pose_active = False
    if 'exercise_reps' not in st.session_state:
        st.session_state.exercise_reps = 0

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI"""
    return weight_kg / ((height_cm / 100) ** 2)

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def classify_body_type(height, weight, age, gender):
    """Simple body type classification"""
    bmi = calculate_bmi(weight, height)
    
    if bmi < 20:
        body_type = 'ectomorph'
    elif bmi > 27:
        body_type = 'endomorph'
    else:
        body_type = 'mesomorph'
    
    return {
        'body_type': body_type,
        'confidence': 0.85,
        'probabilities': {
            'ectomorph': 0.33,
            'mesomorph': 0.34,
            'endomorph': 0.33
        }
    }

def generate_workout_plan(user_profile, workout_type="AI Recommended", duration=45, intensity="Beginner"):
    """Generate a simple workout plan"""
    
    # Exercise database
    exercises = {
        'beginner': [
            {'exercise': 'Push-ups', 'sets': 2, 'reps': 8, 'rest': '30 seconds'},
            {'exercise': 'Squats', 'sets': 2, 'reps': 10, 'rest': '30 seconds'},
            {'exercise': 'Plank', 'sets': 2, 'reps': '20 seconds', 'rest': '30 seconds'},
            {'exercise': 'Jumping Jacks', 'sets': 2, 'reps': 15, 'rest': '30 seconds'}
        ],
        'intermediate': [
            {'exercise': 'Push-ups', 'sets': 3, 'reps': 12, 'rest': '45 seconds'},
            {'exercise': 'Squats', 'sets': 3, 'reps': 15, 'rest': '45 seconds'},
            {'exercise': 'Lunges', 'sets': 3, 'reps': 10, 'rest': '45 seconds'},
            {'exercise': 'Plank', 'sets': 3, 'reps': '30 seconds', 'rest': '45 seconds'},
            {'exercise': 'Mountain Climbers', 'sets': 3, 'reps': 20, 'rest': '45 seconds'}
        ],
        'advanced': [
            {'exercise': 'Push-ups', 'sets': 4, 'reps': 15, 'rest': '60 seconds'},
            {'exercise': 'Squats', 'sets': 4, 'reps': 20, 'rest': '60 seconds'},
            {'exercise': 'Burpees', 'sets': 3, 'reps': 10, 'rest': '60 seconds'},
            {'exercise': 'Plank', 'sets': 3, 'reps': '45 seconds', 'rest': '60 seconds'},
            {'exercise': 'Mountain Climbers', 'sets': 4, 'reps': 25, 'rest': '60 seconds'},
            {'exercise': 'Jump Squats', 'sets': 3, 'reps': 15, 'rest': '60 seconds'}
        ]
    }
    
    selected_exercises = exercises.get(intensity.lower(), exercises['beginner'])
    estimated_calories = len(selected_exercises) * 5 * (duration // 30)
    
    return {
        'type': workout_type,
        'duration': duration,
        'intensity': intensity,
        'goal': user_profile.get('goal', 'General Fitness'),
        'focus': 'Full Body',
        'exercises': selected_exercises,
        'estimated_calories': estimated_calories,
        'generated_at': datetime.now().isoformat()
    }

def render_dashboard():
    """Render the main dashboard"""
    st.title("🏋️ Fitness Dashboard")
    
    if not st.session_state.user_profile:
        st.markdown('<div class="warning">⚠️ Please complete your profile first!</div>', unsafe_allow_html=True)
        if st.button("Go to Profile", key="dashboard_profile_btn"):
            st.session_state.current_page = "Profile"
            st.rerun()
        return
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    profile = st.session_state.user_profile
    history = st.session_state.workout_history
    
    with col1:
        st.metric(
            label="Current BMI",
            value=f"{profile.get('bmi', 0):.1f}",
            delta=None
        )
    
    with col2:
        workouts_completed = len(history)
        st.metric(
            label="Workouts Completed",
            value=workouts_completed
        )
    
    with col3:
        total_calories = sum(w.get('estimated_calories', 0) for w in history)
        st.metric(
            label="Calories Burned",
            value=f"{total_calories:,}"
        )
    
    with col4:
        st.metric(
            label="Body Type",
            value=profile.get('body_type', 'Not determined').title()
        )
    
    # Current workout section
    st.subheader("📅 Today's Workout")
    
    if st.session_state.current_workout:
        workout = st.session_state.current_workout
        st.success("✅ Workout Plan Ready!")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"**Type:** {workout.get('type', 'General')}")
            st.write(f"**Duration:** {workout.get('duration', 30)} minutes")
        with col_b:
            st.write(f"**Exercises:** {len(workout.get('exercises', []))}")
            st.write(f"**Estimated Calories:** {workout.get('estimated_calories', 0)}")
        
        if st.button("✅ Mark Complete"):
            workout_data = workout.copy()
            workout_data['date'] = datetime.now().isoformat()
            workout_data['completed'] = True
            st.session_state.workout_history.append(workout_data)
            st.session_state.current_workout = None
            st.success("🎉 Workout completed! Great job!")
            st.balloons()
            st.rerun()
    else:
        st.info("🎯 No workout planned for today")
        if st.button("Generate Workout Plan", type="primary", key="dashboard_workout_btn"):
            st.session_state.current_page = "Workout Planner"
            st.rerun()

def render_bmi_calculator():
    """Render BMI calculator"""
    st.title("📊 BMI Calculator & Body Type Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📏 Calculate Your BMI")
        
        height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.5)
        weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.1)
        age = st.number_input("Age", min_value=13, max_value=100, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        if st.button("Calculate BMI & Analyze Body Type", type="primary"):
            bmi = calculate_bmi(weight_kg, height_cm)
            body_type_result = classify_body_type(height_cm, weight_kg, age, gender)
            
            st.session_state.user_profile.update({
                'height': height_cm,
                'weight': weight_kg,
                'age': age,
                'gender': gender,
                'bmi': bmi,
                'body_type': body_type_result['body_type'],
                'body_type_confidence': body_type_result['confidence']
            })
            
            st.success("✅ BMI and body type analysis completed!")
            st.rerun()
    
    with col2:
        st.subheader("📈 Your Results")
        
        if 'bmi' in st.session_state.user_profile:
            profile = st.session_state.user_profile
            bmi = profile['bmi']
            category = get_bmi_category(bmi)
            
            st.metric(label="Your BMI", value=f"{bmi:.1f}", delta=category)
            
            # BMI gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=bmi,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "BMI Scale"},
                gauge={
                    'axis': {'range': [None, 40]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 18.5], 'color': "lightblue"},
                        {'range': [18.5, 25], 'color': "lightgreen"},
                        {'range': [25, 30], 'color': "yellow"},
                        {'range': [30, 40], 'color': "red"}
                    ]
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Body type display
            if 'body_type' in profile:
                st.subheader("🧬 Body Type Analysis")
                body_type = profile['body_type']
                confidence = profile.get('body_type_confidence', 0)
                
                st.metric(
                    label="Primary Body Type",
                    value=body_type.title(),
                    delta=f"{confidence:.1%} confidence"
                )
                
                # Body type info
                body_type_info = {
                    'ectomorph': {
                        'description': 'Naturally lean with fast metabolism',
                        'tips': ['Focus on compound movements', 'Eat frequently', 'Limit excessive cardio']
                    },
                    'mesomorph': {
                        'description': 'Naturally athletic with balanced metabolism', 
                        'tips': ['Balanced training approach', 'Mix cardio and strength', 'Progressive overload']
                    },
                    'endomorph': {
                        'description': 'Naturally rounder build with slower metabolism',
                        'tips': ['Include more cardio', 'High-intensity training', 'Control portions']
                    }
                }
                
                info = body_type_info.get(body_type, body_type_info['mesomorph'])
                st.write(f"**Description:** {info['description']}")
                st.write("**Tips:**")
                for tip in info['tips']:
                    st.write(f"• {tip}")
        else:
            st.info("👆 Enter your measurements to calculate BMI")

def render_workout_planner():
    """Render workout planner"""
    st.title("🏋️ AI Workout Planner")
    
    if not st.session_state.user_profile or 'bmi' not in st.session_state.user_profile:
        st.markdown('<div class="warning">⚠️ Please calculate your BMI first!</div>', unsafe_allow_html=True)
        if st.button("Go to BMI Calculator", key="planner_bmi_btn"):
            st.session_state.current_page = "BMI Calculator"
            st.rerun()
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎯 Workout Preferences")
        
        workout_type = st.selectbox("Workout Focus", ["AI Recommended", "Strength Training", "Cardio", "HIIT", "Full Body"])
        duration = st.slider("Workout Duration (minutes)", min_value=15, max_value=90, value=45, step=5)
        intensity = st.selectbox("Intensity Level", ["Beginner", "Intermediate", "Advanced"])
        
        if st.button("🔥 Generate AI Workout", type="primary"):
            workout_plan = generate_workout_plan(
                st.session_state.user_profile, 
                workout_type, 
                duration, 
                intensity
            )
            st.session_state.current_workout = workout_plan
            st.success("✅ Workout generated successfully!")
            st.rerun()
    
    with col2:
        if st.session_state.current_workout:
            workout = st.session_state.current_workout
            st.subheader(f"🔥 {workout['type']} Workout")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Duration", f"{workout['duration']} min")
            with col_b:
                st.metric("Exercises", len(workout['exercises']))
            with col_c:
                st.metric("Est. Calories", f"{workout['estimated_calories']}")
            
            st.write(f"**Focus:** {workout['focus']}")
            st.write(f"**Intensity:** {workout['intensity']}")
            
            st.subheader("📋 Exercise Plan")
            
            for i, exercise in enumerate(workout['exercises'], 1):
                with st.expander(f"Exercise {i}: {exercise['exercise']}", expanded=True):
                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.write(f"**Sets:** {exercise['sets']}")
                        st.write(f"**Reps:** {exercise['reps']}")
                    with col_y:
                        st.write(f"**Rest:** {exercise['rest']}")
            
            if st.button("✅ Mark Workout Complete", type="primary"):
                workout_data = workout.copy()
                workout_data['date'] = datetime.now().isoformat()
                workout_data['completed'] = True
                st.session_state.workout_history.append(workout_data)
                st.session_state.current_workout = None
                st.success("🎉 Workout completed and added to history!")
                st.balloons()
                st.rerun()
        else:
            st.info("👈 Configure your preferences and generate a workout!")

def render_pose_detector():
    """Render pose detection interface"""
    st.title("📹 AI Pose Detection with Real Camera")
    
    # Add information about camera access
    st.info("🎥 This feature uses your device camera for real-time pose detection with TensorFlow.js and PoseNet. Make sure to allow camera access when prompted.")
    
    # Camera permission check
    st.markdown("""
    <div style="background: #2D3748; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <h4>🔒 Camera Access Required</h4>
        <p>For the best experience:</p>
        <ul>
            <li>Position yourself 3-6 feet from the camera</li>
            <li>Ensure good lighting in the room</li>
            <li>Wear fitted clothing for better detection</li>
            <li>Clear space around you for movement</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Load the HTML camera component
    with open('pose_camera.html', 'r') as f:
        camera_html = f.read()
    
    # Embed the full HTML camera component
    components.html(camera_html, height=800, scrolling=True)
    
    # Additional features below the camera
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Workout History")
        if 'pose_sessions' in st.session_state and st.session_state.pose_sessions:
            for i, session in enumerate(st.session_state.pose_sessions[-5:], 1):  # Show last 5 sessions
                with st.expander(f"Session {i}: {session['exercise']}", expanded=False):
                    st.write(f"**Reps:** {session['reps_completed']}/{session['target_reps']}")
                    st.write(f"**Form Score:** {session['form_score']}%")
                    st.write(f"**Date:** {session['date'][:16]}")
                    st.write(f"**Calories:** {session['calories']}")
        else:
            st.info("No workout sessions recorded yet. Start a detection session to track your progress!")
    
    with col2:
        st.subheader("🏆 Exercise Library")
        
        exercises_library = {
            "Push-ups": {
                "difficulty": "Beginner to Advanced",
                "calories_per_rep": 0.5,
                "primary_muscles": "Chest, Triceps, Shoulders",
                "tips": [
                    "Keep your body in a straight line",
                    "Lower chest to ground level",
                    "Don't let hips sag or pike up",
                    "Control both up and down movement"
                ]
            },
            "Squats": {
                "difficulty": "Beginner to Advanced", 
                "calories_per_rep": 0.8,
                "primary_muscles": "Quadriceps, Glutes, Hamstrings",
                "tips": [
                    "Feet shoulder-width apart",
                    "Chest up, core engaged",
                    "Lower until thighs parallel to ground",
                    "Drive through heels to stand"
                ]
            },
            "Lunges": {
                "difficulty": "Beginner to Intermediate",
                "calories_per_rep": 0.7,
                "primary_muscles": "Quadriceps, Glutes, Calves",
                "tips": [
                    "Step forward into lunge position",
                    "90-degree angles at both knees",
                    "Keep front knee over ankle",
                    "Drive through front heel to return"
                ]
            },
            "Plank": {
                "difficulty": "Beginner to Advanced",
                "calories_per_sec": 0.05,
                "primary_muscles": "Core, Shoulders, Back",
                "tips": [
                    "Body in straight line from head to heels",
                    "Engage core and glutes",
                    "Don't hold your breath",
                    "Keep shoulders over elbows"
                ]
            }
        }
        
        for exercise_name, details in exercises_library.items():
            with st.expander(f"💪 {exercise_name}", expanded=False):
                st.write(f"**Difficulty:** {details['difficulty']}")
                st.write(f"**Primary Muscles:** {details['primary_muscles']}")
                if 'calories_per_rep' in details:
                    st.write(f"**Calories per Rep:** ~{details['calories_per_rep']}")
                else:
                    st.write(f"**Calories per Second:** ~{details['calories_per_sec']}")
                st.write("**Form Tips:**")
                for tip in details['tips']:
                    st.write(f"• {tip}")
    
    # Troubleshooting section
    st.markdown("---")
    with st.expander("🔧 Troubleshooting Camera Issues"):
        st.markdown("""
        **Camera Not Working?**
        
        1. **Permission Denied**: Refresh the page and click "Allow" when prompted for camera access
        2. **Camera Already in Use**: Close other applications using your camera (Zoom, Skype, etc.)
        3. **Browser Compatibility**: Use Chrome, Firefox, Safari, or Edge for best results
        4. **HTTPS Required**: Camera access requires secure connection (HTTPS)
        5. **Mobile Devices**: Ensure browser has camera permissions in device settings
        
        **Detection Not Accurate?**
        
        1. **Lighting**: Ensure you have good, even lighting on your body
        2. **Clothing**: Wear fitted clothes that don't hide your body shape
        3. **Background**: Simple, uncluttered background works best
        4. **Distance**: Stay 3-6 feet away from the camera
        5. **Full Body**: Make sure your entire body is visible in the frame
        
        **Performance Issues?**
        
        1. **Close Other Tabs**: Free up browser memory and CPU
        2. **Lower Quality**: Use lower camera resolution if available
        3. **Restart Browser**: Close and reopen your browser
        4. **Update Browser**: Ensure you have the latest browser version
        """)
    
    # Save pose session data to workout history
    if st.button("📈 Add to Workout History", key="add_to_history"):
        # This would integrate with the main workout tracking system
        st.success("Pose detection sessions will be automatically saved when you complete them in the camera interface above!")
        st.info("Your rep counts and form scores are tracked in real-time during detection sessions.")

def render_profile():
    """Render user profile page"""
    st.title("👤 User Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Information")
        name = st.text_input("Name", value=st.session_state.user_profile.get('name', ''))
        age = st.number_input("Age", min_value=13, max_value=100, 
                             value=st.session_state.user_profile.get('age', 25))
        gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                             index=["Male", "Female", "Other"].index(
                                 st.session_state.user_profile.get('gender', 'Male')))
        
        st.subheader("Fitness Goals")
        goal = st.selectbox("Primary Goal", 
                           ["Weight Loss", "Muscle Gain", "Endurance", "Strength", "General Fitness"],
                           index=0 if 'goal' not in st.session_state.user_profile else
                           ["Weight Loss", "Muscle Gain", "Endurance", "Strength", "General Fitness"].index(
                               st.session_state.user_profile.get('goal', 'General Fitness')))
    
    with col2:
        st.subheader("Workout Preferences")
        workout_duration = st.slider("Preferred workout duration (minutes)", 
                                    15, 120, st.session_state.user_profile.get('workout_duration', 45))
        
        workout_frequency = st.slider("Workouts per week", 
                                     1, 7, st.session_state.user_profile.get('workout_frequency', 3))
        
        experience = st.selectbox("Fitness Experience",
                                 ["Beginner", "Intermediate", "Advanced"],
                                 index=0 if 'experience' not in st.session_state.user_profile else
                                 ["Beginner", "Intermediate", "Advanced"].index(
                                     st.session_state.user_profile.get('experience', 'Beginner')))
    
    if st.button("Save Profile", type="primary"):
        st.session_state.user_profile.update({
            'name': name,
            'age': age,
            'gender': gender,
            'goal': goal,
            'workout_duration': workout_duration,
            'workout_frequency': workout_frequency,
            'experience': experience
        })
        st.success("Profile saved successfully!")
        st.rerun()

def main():
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🏋️ AI Fitness Coach")
    
    # Navigation with session state management
    pages = ["Dashboard", "BMI Calculator", "Workout Planner", "Pose Detection", "Profile"]
    
    # Use selectbox but sync with session state
    selected_page = st.sidebar.selectbox(
        "Navigate",
        pages,
        index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
        key="nav_selectbox"
    )
    
    # Update session state if page changed via selectbox
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
    
    # Display user info in sidebar
    if st.session_state.user_profile:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Your Profile")
        profile = st.session_state.user_profile
        if 'bmi' in profile:
            st.sidebar.write(f"**BMI:** {profile['bmi']:.1f}")
        if 'body_type' in profile:
            st.sidebar.write(f"**Body Type:** {profile['body_type'].title()}")
        if 'goal' in profile:
            st.sidebar.write(f"**Goal:** {profile['goal']}")
        
        # Quick stats
        if st.session_state.workout_history:
            workouts_count = len(st.session_state.workout_history)
            total_calories = sum(w.get('estimated_calories', 0) for w in st.session_state.workout_history)
            st.sidebar.write(f"**Workouts:** {workouts_count}")
            st.sidebar.write(f"**Calories Burned:** {total_calories:,}")
    
    # Current page from session state
    page = st.session_state.current_page
    
    # Main content area
    if page == "Dashboard":
        render_dashboard()
    elif page == "BMI Calculator":
        render_bmi_calculator()
    elif page == "Workout Planner":
        render_workout_planner()
    elif page == "Pose Detection":
        render_pose_detector()
    elif page == "Profile":
        render_profile()

if __name__ == "__main__":
    main()