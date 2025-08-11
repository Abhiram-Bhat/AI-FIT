import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, date
from components.dashboard import render_dashboard
from components.bmi_calculator import render_bmi_calculator
from components.workout_planner import render_workout_planner
from components.pose_detector import render_pose_detector
from utils.data_loader import load_workout_data, save_workout_history
from models.lstm_recommender import LSTMRecommender
from models.body_type_classifier import BodyTypeClassifier

# Page configuration
st.set_page_config(
    page_title="AI Fitness Coach",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'workout_history' not in st.session_state:
    st.session_state.workout_history = []
if 'current_workout' not in st.session_state:
    st.session_state.current_workout = None
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False

def load_models():
    """Load ML models on first run"""
    if not st.session_state.models_loaded:
        with st.spinner("Loading AI models..."):
            try:
                st.session_state.lstm_recommender = LSTMRecommender()
                st.session_state.body_classifier = BodyTypeClassifier()
                st.session_state.models_loaded = True
                st.success("AI models loaded successfully!")
            except Exception as e:
                st.error(f"Error loading models: {str(e)}")
                return False
    return True

def main():
    # Load models
    if not load_models():
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("🏋️ AI Fitness Coach")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Navigate",
        ["Dashboard", "BMI Calculator", "Workout Planner", "Pose Detection", "Profile"]
    )
    
    # Display user info in sidebar if available
    if st.session_state.user_profile:
        st.sidebar.subheader("Your Profile")
        profile = st.session_state.user_profile
        st.sidebar.write(f"**BMI:** {profile.get('bmi', 'Not calculated'):.1f}")
        st.sidebar.write(f"**Body Type:** {profile.get('body_type', 'Not determined')}")
        st.sidebar.write(f"**Fitness Goal:** {profile.get('goal', 'Not set')}")
    
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
        render_profile_page()

def render_profile_page():
    """Render user profile configuration page"""
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
                           index=["Weight Loss", "Muscle Gain", "Endurance", "Strength", "General Fitness"].index(
                               st.session_state.user_profile.get('goal', 'General Fitness')))
        
        activity_level = st.selectbox("Activity Level",
                                     ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                                     index=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"].index(
                                         st.session_state.user_profile.get('activity_level', 'Moderately Active')))
    
    with col2:
        st.subheader("Health Information")
        injuries = st.text_area("Any injuries or limitations?", 
                               value=st.session_state.user_profile.get('injuries', ''))
        
        experience = st.selectbox("Fitness Experience",
                                 ["Beginner", "Intermediate", "Advanced"],
                                 index=["Beginner", "Intermediate", "Advanced"].index(
                                     st.session_state.user_profile.get('experience', 'Beginner')))
        
        st.subheader("Workout Preferences")
        workout_duration = st.slider("Preferred workout duration (minutes)", 
                                    15, 120, st.session_state.user_profile.get('workout_duration', 45))
        
        workout_frequency = st.slider("Workouts per week", 
                                     1, 7, st.session_state.user_profile.get('workout_frequency', 3))
    
    if st.button("Save Profile", type="primary"):
        st.session_state.user_profile.update({
            'name': name,
            'age': age,
            'gender': gender,
            'goal': goal,
            'activity_level': activity_level,
            'injuries': injuries,
            'experience': experience,
            'workout_duration': workout_duration,
            'workout_frequency': workout_frequency
        })
        st.success("Profile saved successfully!")
        st.rerun()

if __name__ == "__main__":
    main()
