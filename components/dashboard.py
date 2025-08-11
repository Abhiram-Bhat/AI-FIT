import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_loader import load_workout_history, calculate_workout_calories
from utils.pose_detection import pose_manager

def render_dashboard():
    """Render the main dashboard"""
    st.title("🏋️ Fitness Dashboard")
    
    # Check if user has profile
    if not st.session_state.user_profile:
        st.warning("⚠️ Please complete your profile first!")
        if st.button("Go to Profile"):
            st.session_state.page = "Profile"
            st.rerun()
        return
    
    # Dashboard metrics
    render_dashboard_metrics()
    
    # Current workout section
    render_current_workout_section()
    
    # Progress charts
    render_progress_charts()
    
    # Recent activity
    render_recent_activity()

def render_dashboard_metrics():
    """Render key metrics at the top of dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    # Get user stats
    profile = st.session_state.user_profile
    history = st.session_state.workout_history
    pose_stats = pose_manager.get_workout_stats()
    
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
            value=workouts_completed,
            delta=f"+{workouts_completed - pose_stats.get('total_sessions', 0)}" if workouts_completed > 0 else None
        )
    
    with col3:
        total_reps = pose_stats.get('total_reps', 0)
        st.metric(
            label="Total Reps",
            value=total_reps,
            delta=f"+{pose_stats.get('sessions_this_week', 0)}" if pose_stats.get('sessions_this_week', 0) > 0 else None
        )
    
    with col4:
        # Calculate total calories from all workouts
        total_calories = sum(
            calculate_workout_calories(workout.get('exercises', []), workout.get('duration', 30))
            for workout in history
        )
        st.metric(
            label="Calories Burned",
            value=f"{total_calories:,}",
            delta="+50" if total_calories > 0 else None
        )

def render_current_workout_section():
    """Render current workout status and quick actions"""
    st.subheader("📅 Today's Workout")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.current_workout:
            workout = st.session_state.current_workout
            st.success("✅ Workout Plan Ready!")
            
            # Display workout summary
            st.write(f"**Goal:** {workout.get('goal', 'General Fitness')}")
            st.write(f"**Focus:** {workout.get('focus', 'Full Body')}")
            st.write(f"**Estimated Duration:** {workout.get('duration', 30)} minutes")
            st.write(f"**Exercises:** {len(workout.get('exercises', []))}")
            
            # Quick actions
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button("🏃 Start Workout", type="primary"):
                    st.session_state.page = "Workout Planner"
                    st.rerun()
            
            with col_b:
                if st.button("📹 Pose Detection"):
                    st.session_state.page = "Pose Detection"
                    st.rerun()
            
            with col_c:
                if st.button("✅ Mark Complete"):
                    mark_workout_complete()
        else:
            st.info("🎯 No workout planned for today")
            if st.button("Generate Workout Plan", type="primary"):
                st.session_state.page = "Workout Planner"
                st.rerun()
    
    with col2:
        # Body type info
        body_type = st.session_state.user_profile.get('body_type', 'Not determined')
        st.info(f"**Body Type:** {body_type.title()}")
        
        # Quick tips based on body type
        tips = get_body_type_tips(body_type)
        if tips:
            st.write("💡 **Quick Tip:**")
            st.write(tips[0])

def render_progress_charts():
    """Render progress visualization charts"""
    st.subheader("📊 Progress Analytics")
    
    if not st.session_state.workout_history:
        st.info("Complete your first workout to see progress charts!")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Workout frequency chart
        render_workout_frequency_chart()
    
    with col2:
        # Calories burned over time
        render_calories_chart()

def render_workout_frequency_chart():
    """Render workout frequency over time"""
    history = st.session_state.workout_history
    
    # Create DataFrame from history
    df_data = []
    for workout in history:
        df_data.append({
            'date': pd.to_datetime(workout.get('date', datetime.now().isoformat())),
            'completed': 1
        })
    
    if not df_data:
        return
    
    df = pd.DataFrame(df_data)
    df = df.groupby(df['date'].dt.date)['completed'].sum().reset_index()
    df.columns = ['Date', 'Workouts']
    
    fig = px.line(
        df, 
        x='Date', 
        y='Workouts',
        title='Daily Workout Frequency',
        markers=True
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def render_calories_chart():
    """Render calories burned over time"""
    history = st.session_state.workout_history
    
    df_data = []
    for workout in history:
        calories = calculate_workout_calories(
            workout.get('exercises', []), 
            workout.get('duration', 30)
        )
        df_data.append({
            'date': pd.to_datetime(workout.get('date', datetime.now().isoformat())),
            'calories': calories
        })
    
    if not df_data:
        return
    
    df = pd.DataFrame(df_data)
    df = df.groupby(df['date'].dt.date)['calories'].sum().reset_index()
    df.columns = ['Date', 'Calories']
    
    fig = px.bar(
        df, 
        x='Date', 
        y='Calories',
        title='Daily Calories Burned',
        color='Calories',
        color_continuous_scale='Reds'
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def render_recent_activity():
    """Render recent workout activity"""
    st.subheader("🕒 Recent Activity")
    
    history = st.session_state.workout_history
    pose_sessions = pose_manager.get_workout_stats()
    
    if not history and not pose_sessions:
        st.info("No recent activity to display. Start your first workout!")
        return
    
    # Combine workout history and pose sessions
    all_activities = []
    
    # Add workout history
    for workout in history[-5:]:  # Last 5 workouts
        all_activities.append({
            'type': 'Workout Completed',
            'date': workout.get('date', datetime.now().isoformat()),
            'details': f"{len(workout.get('exercises', []))} exercises, {workout.get('duration', 30)} minutes",
            'icon': '🏋️'
        })
    
    # Add pose detection sessions
    if 'pose_sessions' in st.session_state:
        for session in st.session_state.pose_sessions[-3:]:  # Last 3 sessions
            all_activities.append({
                'type': 'Pose Detection Session',
                'date': session.get('timestamp', datetime.now().isoformat()),
                'details': f"{session.get('exercise', 'Exercise')}: {session.get('reps', 0)} reps",
                'icon': '📹'
            })
    
    # Sort by date
    all_activities.sort(key=lambda x: x['date'], reverse=True)
    
    # Display activities
    for activity in all_activities[:8]:  # Show top 8
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            st.write(activity['icon'])
        
        with col2:
            st.write(f"**{activity['type']}**")
            st.write(activity['details'])
        
        with col3:
            date_obj = pd.to_datetime(activity['date'])
            st.write(date_obj.strftime('%m/%d %H:%M'))

def mark_workout_complete():
    """Mark current workout as complete and add to history"""
    if st.session_state.current_workout:
        workout_data = st.session_state.current_workout.copy()
        workout_data['date'] = datetime.now().isoformat()
        workout_data['completed'] = True
        
        # Add to history
        st.session_state.workout_history.append(workout_data)
        
        # Clear current workout
        st.session_state.current_workout = None
        
        st.success("🎉 Workout completed! Great job!")
        st.balloons()
        st.rerun()

def get_body_type_tips(body_type):
    """Get quick tips based on body type"""
    tips = {
        'ectomorph': [
            "Focus on compound movements to build mass",
            "Eat frequently throughout the day",
            "Limit cardio to preserve muscle mass"
        ],
        'mesomorph': [
            "Maintain balanced cardio and strength training",
            "Vary your workout routines regularly",
            "Focus on progressive overload"
        ],
        'endomorph': [
            "Include more cardio in your routine",
            "Focus on high-intensity interval training",
            "Control portion sizes for better results"
        ]
    }
    
    return tips.get(body_type.lower(), [])
