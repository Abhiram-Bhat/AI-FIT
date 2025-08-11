# Overview

AI Fitness Coach is a comprehensive fitness application built with Streamlit that provides personalized workout recommendations, BMI calculations, body type analysis, and real-time pose detection for exercise form correction. The application uses machine learning models including LSTM networks for workout recommendations and computer vision for pose detection to create an intelligent fitness coaching experience.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit for web-based user interface
- **Layout**: Multi-page application with sidebar navigation
- **Components**: Modular component structure with separate files for dashboard, BMI calculator, workout planner, and pose detector
- **State Management**: Streamlit session state for user profiles, workout history, and model loading

## Backend Architecture
- **Application Structure**: Single-file entry point (app.py) with modular components
- **Machine Learning Models**: 
  - LSTM Recommender for personalized workout suggestions based on user history
  - Body Type Classifier using Random Forest for ectomorph/mesomorph/endomorph classification
- **Data Processing**: Utility modules for data loading, pose detection management, and YouTube API integration
- **Model Training**: Synthetic data generation for training ML models when real data is unavailable

## Data Storage Solutions
- **File-based Storage**: JSON files for exercise library and user data
- **CSV Storage**: Workout data and history stored in CSV format
- **Session Storage**: Temporary data stored in Streamlit session state
- **Model Persistence**: Pickle files for saving trained ML models

## Computer Vision Integration
- **Pose Detection**: TensorFlow.js with PoseNet model for real-time exercise form analysis
- **Frontend Integration**: HTML/JavaScript component embedded in Streamlit for camera access
- **Exercise Recognition**: Custom logic for detecting specific exercise movements (push-ups, squats, etc.)
- **Rep Counting**: Angle-based detection system for counting exercise repetitions

## Content Integration
- **Exercise Library**: JSON-based exercise database with instructions, benefits, and modifications
- **Video Integration**: YouTube API integration for exercise demonstration videos with fallback content
- **Calorie Calculation**: Built-in algorithms for estimating calories burned during workouts

# External Dependencies

## Machine Learning Libraries
- **TensorFlow/Keras**: For LSTM neural network implementation and model training
- **Scikit-learn**: For Random Forest classifier and data preprocessing utilities
- **NumPy/Pandas**: For data manipulation and numerical computations

## Web Framework and UI
- **Streamlit**: Primary web application framework
- **Plotly**: Interactive charts and data visualization
- **Streamlit Components**: For embedding custom HTML/JavaScript components

## Computer Vision
- **TensorFlow.js**: Client-side machine learning for pose detection
- **PoseNet**: Pre-trained pose estimation model
- **OpenCV**: Image processing and computer vision utilities

## API Integrations
- **YouTube Data API v3**: For fetching exercise demonstration videos
- **REST API**: Standard HTTP requests for external service communication

## Development Tools
- **Python Standard Library**: JSON, OS, datetime modules for core functionality
- **Environment Variables**: For API key management and configuration