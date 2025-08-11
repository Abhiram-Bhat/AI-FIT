import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime, timedelta
from utils.pose_detection import pose_manager

def render_pose_detector():
    """Render pose detection interface"""
    st.title("📹 AI Pose Detection")
    
    # Check camera permissions info
    st.info("🔒 This feature requires camera access. Please allow camera permissions when prompted.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_pose_controls()
    
    with col2:
        render_pose_detection_area()

def render_pose_controls():
    """Render pose detection controls"""
    st.subheader("🎯 Exercise Selection")
    
    # Exercise selection
    exercise = st.selectbox(
        "Choose Exercise to Practice",
        [
            "Push-ups",
            "Squats", 
            "Plank",
            "Lunges",
            "Burpees",
            "Jumping Jacks"
        ]
    )
    
    # Detection settings
    st.subheader("⚙️ Detection Settings")
    
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.1,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Higher values require more confident pose detection"
    )
    
    show_keypoints = st.checkbox("Show Keypoints", value=True)
    show_skeleton = st.checkbox("Show Skeleton", value=True)
    
    # Rep counting settings
    st.subheader("📊 Rep Counting")
    
    target_reps = st.number_input(
        "Target Reps",
        min_value=1,
        max_value=100,
        value=10
    )
    
    # Control buttons
    st.subheader("🎮 Controls")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("▶️ Start Detection", type="primary"):
            start_pose_detection(exercise, confidence_threshold, target_reps)
    
    with col_b:
        if st.button("⏹️ Stop Detection"):
            stop_pose_detection()
    
    # Current session info
    if pose_manager.is_detecting:
        st.success(f"🟢 Detecting: {pose_manager.current_exercise}")
        st.metric("Current Reps", pose_manager.rep_count)
        
        if pose_manager.rep_count >= target_reps:
            st.balloons()
            st.success("🎉 Target reached! Great job!")
            
            if st.button("💾 Save Session"):
                save_pose_session(exercise, target_reps)

def render_pose_detection_area():
    """Render the main pose detection area with camera feed"""
    st.subheader("📹 Live Camera Feed")
    
    # Load the pose detection HTML component
    pose_html = load_pose_detection_html()
    
    # Render the component
    result = components.html(
        pose_html,
        height=600,
        scrolling=True
    )
    
    # Display current analysis if available
    if 'current_pose_analysis' in st.session_state:
        render_pose_analysis(st.session_state.current_pose_analysis)

def load_pose_detection_html():
    """Load the HTML component for pose detection"""
    try:
        with open('static/pose_detection.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Return basic HTML if file not found
        return create_basic_pose_html()

def create_basic_pose_html():
    """Create basic pose detection HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.15.0/dist/tf.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/posenet@2.2.2/dist/posenet.min.js"></script>
        <style>
            body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
            #video-container { position: relative; display: flex; justify-content: center; }
            #video { border: 2px solid #ccc; border-radius: 10px; }
            #canvas { position: absolute; top: 0; left: 0; pointer-events: none; }
            #status { margin-top: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px; }
            .controls { margin: 20px 0; text-align: center; }
            button { margin: 5px; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .start { background: #4CAF50; color: white; }
            .stop { background: #f44336; color: white; }
            #feedback { margin-top: 10px; padding: 10px; background: #e3f2fd; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div id="video-container">
            <video id="video" width="640" height="480" autoplay></video>
            <canvas id="canvas" width="640" height="480"></canvas>
        </div>
        
        <div class="controls">
            <button class="start" onclick="startCamera()">📹 Start Camera</button>
            <button class="stop" onclick="stopCamera()">⏹️ Stop Camera</button>
        </div>
        
        <div id="status">
            <strong>Status:</strong> <span id="status-text">Ready to start</span>
        </div>
        
        <div id="feedback">
            <strong>Form Feedback:</strong>
            <div id="feedback-text">Position yourself in front of the camera and start exercising!</div>
        </div>

        <script>
            let video, canvas, ctx, net;
            let isDetecting = false;
            let repCount = 0;
            let lastPoseState = null;
            
            async function setupCamera() {
                video = document.getElementById('video');
                canvas = document.getElementById('canvas');
                ctx = canvas.getContext('2d');
                
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: 640, height: 480 } 
                });
                video.srcObject = stream;
                
                return new Promise((resolve) => {
                    video.onloadedmetadata = () => {
                        resolve(video);
                    };
                });
            }
            
            async function loadPoseNet() {
                updateStatus('Loading PoseNet model...');
                net = await posenet.load({
                    architecture: 'MobileNetV1',
                    outputStride: 16,
                    inputResolution: { width: 640, height: 480 },
                    multiplier: 0.75
                });
                updateStatus('PoseNet model loaded successfully!');
            }
            
            async function startCamera() {
                try {
                    updateStatus('Setting up camera...');
                    await setupCamera();
                    await loadPoseNet();
                    
                    isDetecting = true;
                    updateStatus('Pose detection active');
                    detectPoses();
                } catch (err) {
                    updateStatus('Error: ' + err.message);
                    console.error(err);
                }
            }
            
            function stopCamera() {
                isDetecting = false;
                updateStatus('Pose detection stopped');
                
                if (video.srcObject) {
                    video.srcObject.getTracks().forEach(track => track.stop());
                }
            }
            
            async function detectPoses() {
                if (!isDetecting) return;
                
                try {
                    const pose = await net.estimateSinglePose(video, {
                        flipHorizontal: false
                    });
                    
                    drawPose(pose);
                    analyzePose(pose);
                    
                } catch (err) {
                    console.error('Detection error:', err);
                }
                
                requestAnimationFrame(detectPoses);
            }
            
            function drawPose(pose) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Draw keypoints
                pose.keypoints.forEach(keypoint => {
                    if (keypoint.score > 0.5) {
                        ctx.beginPath();
                        ctx.arc(keypoint.position.x, keypoint.position.y, 5, 0, 2 * Math.PI);
                        ctx.fillStyle = '#FF0000';
                        ctx.fill();
                    }
                });
                
                // Draw skeleton
                const adjacentKeyPoints = posenet.getAdjacentKeyPoints(pose.keypoints, 0.5);
                adjacentKeyPoints.forEach(keypoints => {
                    ctx.beginPath();
                    ctx.moveTo(keypoints[0].position.x, keypoints[0].position.y);
                    ctx.lineTo(keypoints[1].position.x, keypoints[1].position.y);
                    ctx.strokeStyle = '#00FF00';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                });
            }
            
            function analyzePose(pose) {
                // Simple rep counting for push-ups
                const leftShoulder = pose.keypoints.find(kp => kp.part === 'leftShoulder');
                const leftElbow = pose.keypoints.find(kp => kp.part === 'leftElbow');
                const leftWrist = pose.keypoints.find(kp => kp.part === 'leftWrist');
                
                if (leftShoulder && leftElbow && leftWrist && 
                    leftShoulder.score > 0.5 && leftElbow.score > 0.5 && leftWrist.score > 0.5) {
                    
                    const angle = calculateAngle(
                        leftShoulder.position, 
                        leftElbow.position, 
                        leftWrist.position
                    );
                    
                    const currentState = angle > 160 ? 'up' : angle < 90 ? 'down' : 'middle';
                    
                    if (lastPoseState === 'down' && currentState === 'up') {
                        repCount++;
                        updateFeedback(`Great! Rep ${repCount} completed. Keep going!`);
                    } else if (currentState === 'down') {
                        updateFeedback('Good depth! Push back up.');
                    } else if (currentState === 'up') {
                        updateFeedback('Ready for next rep. Lower down slowly.');
                    }
                    
                    lastPoseState = currentState;
                }
            }
            
            function calculateAngle(a, b, c) {
                const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
                let angle = Math.abs(radians * 180.0 / Math.PI);
                if (angle > 180.0) {
                    angle = 360 - angle;
                }
                return angle;
            }
            
            function updateStatus(message) {
                document.getElementById('status-text').textContent = message;
            }
            
            function updateFeedback(message) {
                document.getElementById('feedback-text').textContent = message;
            }
            
            // Initialize when page loads
            window.onload = function() {
                updateStatus('Click "Start Camera" to begin');
            };
        </script>
    </body>
    </html>
    """

def render_pose_analysis(analysis):
    """Render pose analysis results"""
    if not analysis:
        return
    
    st.subheader("🔍 Pose Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Rep Count", analysis.get('rep_count', 0))
        st.metric("Confidence", f"{analysis.get('confidence', 0):.1%}")
    
    with col2:
        # Form feedback
        feedback = analysis.get('form_feedback', [])
        if feedback:
            st.write("**Form Feedback:**")
            for fb in feedback:
                st.write(f"• {fb}")
    
    # Angle information
    angles = analysis.get('angles', {})
    if angles:
        st.write("**Joint Angles:**")
        for angle_name, angle_value in angles.items():
            st.write(f"• {angle_name.replace('_', ' ').title()}: {angle_value:.1f}°")

def start_pose_detection(exercise, confidence_threshold, target_reps):
    """Start pose detection session"""
    pose_manager.start_detection(exercise)
    pose_manager.confidence_threshold = confidence_threshold
    
    st.session_state.pose_session = {
        'exercise': exercise,
        'target_reps': target_reps,
        'start_time': datetime.now(),
        'active': True
    }
    
    st.success(f"🟢 Started pose detection for {exercise}")

def stop_pose_detection():
    """Stop pose detection session"""
    pose_manager.stop_detection()
    
    if 'pose_session' in st.session_state:
        st.session_state.pose_session['active'] = False
    
    st.info("⏹️ Pose detection stopped")

def save_pose_session(exercise, target_reps):
    """Save completed pose detection session"""
    if 'pose_session' in st.session_state:
        session = st.session_state.pose_session
        duration = (datetime.now() - session['start_time']).total_seconds()
        
        success = pose_manager.save_workout_session(
            exercise, 
            duration, 
            pose_manager.rep_count
        )
        
        if success:
            st.success("💾 Session saved to history!")
            
            # Show session summary
            st.subheader("📊 Session Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Exercise", exercise)
            with col2:
                st.metric("Reps Completed", pose_manager.rep_count)
            with col3:
                st.metric("Duration", f"{duration/60:.1f} min")
            
            # Reset for next session
            pose_manager.rep_count = 0
            del st.session_state.pose_session
        else:
            st.error("❌ Failed to save session")

def render_pose_history():
    """Render pose detection session history"""
    st.subheader("📈 Pose Detection History")
    
    stats = pose_manager.get_workout_stats()
    
    if not stats:
        st.info("No pose detection sessions yet. Start your first session!")
        return
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", stats['total_sessions'])
    with col2:
        st.metric("Total Reps", stats['total_reps'])
    with col3:
        st.metric("Total Time", f"{stats['total_duration']/60:.1f} min")
    with col4:
        st.metric("This Week", stats['sessions_this_week'])
    
    # Exercise breakdown
    if stats['exercises_performed']:
        st.write("**Exercises Practiced:**")
        for exercise in stats['exercises_performed']:
            st.write(f"• {exercise}")

# Add pose history to the main render function
def render_pose_detector():
    """Render pose detection interface with history"""
    st.title("📹 AI Pose Detection")
    
    tab1, tab2 = st.tabs(["🎯 Live Detection", "📊 History"])
    
    with tab1:
        # Check camera permissions info
        st.info("🔒 This feature requires camera access. Please allow camera permissions when prompted.")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            render_pose_controls()
        
        with col2:
            render_pose_detection_area()
    
    with tab2:
        render_pose_history()
