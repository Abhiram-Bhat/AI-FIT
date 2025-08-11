import cv2
import numpy as np
import streamlit as st
import json
from datetime import datetime

class PoseDetectionManager:
    def __init__(self):
        self.is_detecting = False
        self.current_exercise = None
        self.rep_count = 0
        self.last_pose_state = None
        self.confidence_threshold = 0.5
    
    def start_detection(self, exercise_name):
        """Start pose detection for a specific exercise"""
        self.current_exercise = exercise_name
        self.rep_count = 0
        self.last_pose_state = None
        self.is_detecting = True
    
    def stop_detection(self):
        """Stop pose detection"""
        self.is_detecting = False
        self.current_exercise = None
    
    def get_exercise_keypoints(self, exercise_name):
        """Get required keypoints for each exercise"""
        exercise_keypoints = {
            'push-ups': {
                'primary_joints': ['leftShoulder', 'rightShoulder', 'leftElbow', 'rightElbow', 'leftWrist', 'rightWrist'],
                'angle_joints': [
                    {'name': 'left_arm', 'points': ['leftShoulder', 'leftElbow', 'leftWrist']},
                    {'name': 'right_arm', 'points': ['rightShoulder', 'rightElbow', 'rightWrist']}
                ],
                'rep_detection': {
                    'up_angle_min': 160,
                    'down_angle_max': 90
                }
            },
            'squats': {
                'primary_joints': ['leftHip', 'rightHip', 'leftKnee', 'rightKnee', 'leftAnkle', 'rightAnkle'],
                'angle_joints': [
                    {'name': 'left_leg', 'points': ['leftHip', 'leftKnee', 'leftAnkle']},
                    {'name': 'right_leg', 'points': ['rightHip', 'rightKnee', 'rightAnkle']}
                ],
                'rep_detection': {
                    'up_angle_min': 160,
                    'down_angle_max': 90
                }
            },
            'plank': {
                'primary_joints': ['leftShoulder', 'rightShoulder', 'leftHip', 'rightHip', 'leftAnkle', 'rightAnkle'],
                'angle_joints': [
                    {'name': 'body_line', 'points': ['leftShoulder', 'leftHip', 'leftAnkle']}
                ],
                'hold_detection': {
                    'target_angle': 180,
                    'tolerance': 20
                }
            },
            'lunges': {
                'primary_joints': ['leftHip', 'rightHip', 'leftKnee', 'rightKnee', 'leftAnkle', 'rightAnkle'],
                'angle_joints': [
                    {'name': 'front_leg', 'points': ['leftHip', 'leftKnee', 'leftAnkle']},
                    {'name': 'back_leg', 'points': ['rightHip', 'rightKnee', 'rightAnkle']}
                ],
                'rep_detection': {
                    'up_angle_min': 160,
                    'down_angle_max': 90
                }
            }
        }
        
        exercise_key = exercise_name.lower().replace('-', '').replace(' ', '')
        
        for key, config in exercise_keypoints.items():
            if key in exercise_key or exercise_key in key:
                return config
        
        # Default configuration
        return exercise_keypoints['push-ups']
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        try:
            # Convert points to numpy arrays
            a = np.array(point1)
            b = np.array(point2)
            c = np.array(point3)
            
            # Calculate vectors
            ba = a - b
            bc = c - b
            
            # Calculate angle
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            
            return np.degrees(angle)
        except:
            return 0
    
    def analyze_pose(self, pose_data):
        """Analyze pose for exercise form and rep counting"""
        if not self.is_detecting or not self.current_exercise:
            return None
        
        try:
            exercise_config = self.get_exercise_keypoints(self.current_exercise)
            analysis_result = {
                'exercise': self.current_exercise,
                'rep_count': self.rep_count,
                'form_feedback': [],
                'angles': {},
                'confidence': 0
            }
            
            # Extract keypoints from pose data
            keypoints = {}
            if 'pose' in pose_data and 'keypoints' in pose_data['pose']:
                for i, kp in enumerate(pose_data['pose']['keypoints']):
                    if i < len(self.get_posenet_keypoint_names()):
                        keypoints[self.get_posenet_keypoint_names()[i]] = {
                            'x': kp['position']['x'],
                            'y': kp['position']['y'],
                            'confidence': kp['score']
                        }
            
            # Calculate angles for exercise
            for angle_config in exercise_config.get('angle_joints', []):
                angle_name = angle_config['name']
                joint_names = angle_config['points']
                
                if all(joint in keypoints for joint in joint_names):
                    points = [
                        [keypoints[joint]['x'], keypoints[joint]['y']]
                        for joint in joint_names
                    ]
                    
                    if len(points) == 3:
                        angle = self.calculate_angle(points[0], points[1], points[2])
                        analysis_result['angles'][angle_name] = angle
            
            # Rep counting logic
            if 'rep_detection' in exercise_config:
                rep_config = exercise_config['rep_detection']
                primary_angle = list(analysis_result['angles'].values())[0] if analysis_result['angles'] else 0
                
                # Simple rep counting based on angle thresholds
                current_state = 'up' if primary_angle > rep_config['up_angle_min'] else 'down'
                
                if self.last_pose_state == 'down' and current_state == 'up':
                    self.rep_count += 1
                    analysis_result['rep_count'] = self.rep_count
                
                self.last_pose_state = current_state
            
            # Form feedback
            analysis_result['form_feedback'] = self.generate_form_feedback(
                self.current_exercise, analysis_result['angles'], keypoints
            )
            
            # Calculate overall confidence
            confidences = [kp['confidence'] for kp in keypoints.values()]
            analysis_result['confidence'] = np.mean(confidences) if confidences else 0
            
            return analysis_result
            
        except Exception as e:
            st.error(f"Error analyzing pose: {str(e)}")
            return None
    
    def generate_form_feedback(self, exercise, angles, keypoints):
        """Generate form feedback based on exercise and pose analysis"""
        feedback = []
        
        try:
            if exercise.lower() in ['push-ups', 'pushups']:
                if 'left_arm' in angles and 'right_arm' in angles:
                    left_angle = angles['left_arm']
                    right_angle = angles['right_arm']
                    
                    if abs(left_angle - right_angle) > 20:
                        feedback.append("⚠️ Keep both arms aligned")
                    
                    if left_angle < 60 or right_angle < 60:
                        feedback.append("✅ Good depth! Go full range")
                    elif left_angle > 170 and right_angle > 170:
                        feedback.append("✅ Good starting position")
                    else:
                        feedback.append("💪 Keep going!")
            
            elif exercise.lower() in ['squats', 'squat']:
                if 'left_leg' in angles and 'right_leg' in angles:
                    left_angle = angles['left_leg']
                    right_angle = angles['right_leg']
                    
                    if left_angle < 90 or right_angle < 90:
                        feedback.append("✅ Great squat depth!")
                    elif left_angle > 160 and right_angle > 160:
                        feedback.append("✅ Good standing position")
                    else:
                        feedback.append("💪 Keep your chest up!")
            
            elif exercise.lower() in ['plank']:
                if 'body_line' in angles:
                    body_angle = angles['body_line']
                    
                    if 160 <= body_angle <= 180:
                        feedback.append("✅ Perfect plank form!")
                    elif body_angle < 160:
                        feedback.append("⚠️ Keep your hips up")
                    else:
                        feedback.append("⚠️ Don't arch your back")
            
            # General feedback
            if not feedback:
                feedback.append("💪 Keep it up!")
            
            return feedback
            
        except Exception as e:
            return ["📊 Analyzing your form..."]
    
    def get_posenet_keypoint_names(self):
        """Get list of PoseNet keypoint names in order"""
        return [
            'nose', 'leftEye', 'rightEye', 'leftEar', 'rightEar',
            'leftShoulder', 'rightShoulder', 'leftElbow', 'rightElbow',
            'leftWrist', 'rightWrist', 'leftHip', 'rightHip',
            'leftKnee', 'rightKnee', 'leftAnkle', 'rightAnkle'
        ]
    
    def save_workout_session(self, exercise_name, duration_seconds, reps_completed):
        """Save completed workout session"""
        try:
            session_data = {
                'exercise': exercise_name,
                'duration': duration_seconds,
                'reps': reps_completed,
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Save to session state
            if 'pose_sessions' not in st.session_state:
                st.session_state.pose_sessions = []
            
            st.session_state.pose_sessions.append(session_data)
            
            return True
            
        except Exception as e:
            st.error(f"Error saving workout session: {str(e)}")
            return False
    
    def get_workout_stats(self):
        """Get workout statistics from saved sessions"""
        if 'pose_sessions' not in st.session_state:
            return {}
        
        sessions = st.session_state.pose_sessions
        
        if not sessions:
            return {}
        
        stats = {
            'total_sessions': len(sessions),
            'total_reps': sum(session['reps'] for session in sessions),
            'total_duration': sum(session['duration'] for session in sessions),
            'exercises_performed': list(set(session['exercise'] for session in sessions)),
            'sessions_this_week': len([s for s in sessions 
                                     if (datetime.now() - datetime.fromisoformat(s['timestamp'])).days <= 7])
        }
        
        return stats

# Global instance
pose_manager = PoseDetectionManager()
