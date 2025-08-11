import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from models.body_type_classifier import BodyTypeClassifier

def render_bmi_calculator():
    """Render BMI calculator and body type classification"""
    st.title("📊 BMI Calculator & Body Type Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📏 Calculate Your BMI")
        
        # Input fields
        height_unit = st.selectbox("Height Unit", ["Centimeters", "Feet & Inches"])
        
        if height_unit == "Centimeters":
            height_cm = st.number_input(
                "Height (cm)", 
                min_value=100.0, 
                max_value=250.0, 
                value=170.0, 
                step=0.5
            )
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                feet = st.number_input("Feet", min_value=3, max_value=8, value=5)
            with col_b:
                inches = st.number_input("Inches", min_value=0, max_value=11, value=7)
            height_cm = (feet * 12 + inches) * 2.54
        
        weight_unit = st.selectbox("Weight Unit", ["Kilograms", "Pounds"])
        
        if weight_unit == "Kilograms":
            weight_kg = st.number_input(
                "Weight (kg)", 
                min_value=30.0, 
                max_value=300.0, 
                value=70.0, 
                step=0.1
            )
        else:
            weight_lbs = st.number_input(
                "Weight (lbs)", 
                min_value=66, 
                max_value=660, 
                value=154, 
                step=1
            )
            weight_kg = weight_lbs * 0.453592
        
        age = st.number_input("Age", min_value=13, max_value=100, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        # Calculate BMI
        if st.button("Calculate BMI & Analyze Body Type", type="primary"):
            bmi = weight_kg / ((height_cm / 100) ** 2)
            
            # Update session state
            st.session_state.user_profile.update({
                'height': height_cm,
                'weight': weight_kg,
                'age': age,
                'gender': gender,
                'bmi': bmi
            })
            
            # Body type classification
            if st.session_state.models_loaded:
                classifier = st.session_state.body_classifier
                body_type_result = classifier.predict_body_type(height_cm, weight_kg, age, gender)
                
                st.session_state.user_profile['body_type'] = body_type_result['body_type']
                st.session_state.user_profile['body_type_confidence'] = body_type_result['confidence']
                st.session_state.user_profile['body_type_probabilities'] = body_type_result['probabilities']
            
            st.success("✅ BMI and body type analysis completed!")
            st.rerun()
    
    with col2:
        st.subheader("📈 Your Results")
        
        if 'bmi' in st.session_state.user_profile:
            profile = st.session_state.user_profile
            bmi = profile['bmi']
            
            # BMI Category
            bmi_category, color = get_bmi_category(bmi)
            
            # Display BMI
            st.metric(
                label="Your BMI",
                value=f"{bmi:.1f}",
                delta=f"{bmi_category}"
            )
            
            # BMI Gauge Chart
            render_bmi_gauge(bmi)
            
            # BMI Information
            render_bmi_info(bmi_category)
        else:
            st.info("👆 Enter your measurements to calculate BMI")
    
    # Body Type Analysis Section
    if 'body_type' in st.session_state.user_profile:
        render_body_type_analysis()

def render_bmi_gauge(bmi):
    """Render BMI gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = bmi,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "BMI Scale"},
        gauge = {
            'axis': {'range': [None, 40]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 18.5], 'color': "lightblue"},
                {'range': [18.5, 25], 'color': "lightgreen"},
                {'range': [25, 30], 'color': "yellow"},
                {'range': [30, 40], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': bmi
            }
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def render_bmi_info(category):
    """Render BMI category information"""
    bmi_info = {
        "Underweight": {
            "description": "Below normal weight range",
            "recommendations": [
                "Focus on gaining healthy weight",
                "Increase caloric intake",
                "Strength training to build muscle",
                "Consult healthcare provider"
            ],
            "color": "info"
        },
        "Normal weight": {
            "description": "Healthy weight range",
            "recommendations": [
                "Maintain current weight",
                "Continue balanced diet",
                "Regular exercise routine",
                "Focus on overall fitness"
            ],
            "color": "success"
        },
        "Overweight": {
            "description": "Above normal weight range",
            "recommendations": [
                "Gradual weight loss (1-2 lbs/week)",
                "Increase physical activity",
                "Reduce caloric intake",
                "Focus on cardio exercises"
            ],
            "color": "warning"
        },
        "Obese": {
            "description": "Significantly above normal weight",
            "recommendations": [
                "Consult healthcare provider",
                "Create sustainable weight loss plan",
                "Start with low-impact exercises",
                "Consider nutritional counseling"
            ],
            "color": "error"
        }
    }
    
    info = bmi_info.get(category, bmi_info["Normal weight"])
    
    if info["color"] == "success":
        st.success(f"✅ {category}: {info['description']}")
    elif info["color"] == "warning":
        st.warning(f"⚠️ {category}: {info['description']}")
    elif info["color"] == "error":
        st.error(f"🚨 {category}: {info['description']}")
    else:
        st.info(f"ℹ️ {category}: {info['description']}")
    
    st.write("**Recommendations:**")
    for rec in info["recommendations"]:
        st.write(f"• {rec}")

def render_body_type_analysis():
    """Render detailed body type analysis"""
    st.subheader("🧬 Body Type Analysis")
    
    profile = st.session_state.user_profile
    body_type = profile['body_type']
    confidence = profile.get('body_type_confidence', 0)
    probabilities = profile.get('body_type_probabilities', {})
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric(
            label="Primary Body Type",
            value=body_type.title(),
            delta=f"{confidence:.1%} confidence"
        )
        
        # Body type probabilities
        if probabilities:
            st.write("**Body Type Probabilities:**")
            for bt, prob in probabilities.items():
                st.progress(prob, text=f"{bt.title()}: {prob:.1%}")
    
    with col2:
        # Body type characteristics
        if st.session_state.models_loaded:
            classifier = st.session_state.body_classifier
            characteristics = classifier.get_body_type_characteristics(body_type)
            
            st.write(f"**{body_type.title()} Characteristics:**")
            st.write(characteristics['description'])
            
            with st.expander("View Detailed Information"):
                st.write("**Physical Traits:**")
                for trait in characteristics['traits']:
                    st.write(f"• {trait}")
                
                st.write("**Workout Focus:**")
                for focus in characteristics['workout_focus']:
                    st.write(f"• {focus}")
                
                st.write("**Nutrition Tips:**")
                for tip in characteristics['nutrition_tips']:
                    st.write(f"• {tip}")

def get_bmi_category(bmi):
    """Get BMI category and associated color"""
    if bmi < 18.5:
        return "Underweight", "info"
    elif 18.5 <= bmi < 25:
        return "Normal weight", "success"
    elif 25 <= bmi < 30:
        return "Overweight", "warning"
    else:
        return "Obese", "error"

def render_bmi_history():
    """Render BMI tracking history"""
    if 'bmi_history' not in st.session_state:
        st.session_state.bmi_history = []
    
    if st.session_state.bmi_history:
        st.subheader("📈 BMI History")
        
        df = pd.DataFrame(st.session_state.bmi_history)
        
        import plotly.express as px
        fig = px.line(
            df, 
            x='date', 
            y='bmi',
            title='BMI Progress Over Time',
            markers=True
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
