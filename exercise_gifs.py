"""
Generate animated exercise form GIFs using matplotlib and imageio
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.patches import Circle, Rectangle
import io
import base64

def create_pushup_gif():
    """Create animated pushup form GIF"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_facecolor('#262730')
    fig.patch.set_facecolor('#262730')
    ax.axis('off')
    
    # Body parts
    head = Circle((2, 4), 0.3, color='#667eea', alpha=0.8)
    
    def animate(frame):
        ax.clear()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_facecolor('#262730')
        ax.axis('off')
        
        # Animation cycle
        t = frame / 20.0
        y_offset = 0.5 * np.sin(t * 2 * np.pi)
        
        # Head
        head_pos = (2, 3.5 + y_offset)
        ax.add_patch(Circle(head_pos, 0.3, color='#667eea', alpha=0.8))
        
        # Body (torso)
        body_start = (2, 3.5 + y_offset)
        body_end = (8, 3.5 + y_offset)
        ax.plot([body_start[0], body_end[0]], [body_start[1], body_end[1]], 
                color='#667eea', linewidth=8, alpha=0.8)
        
        # Arms
        arm_y = 3.5 + y_offset
        # Left arm
        ax.plot([2, 1], [arm_y, arm_y - 1 - y_offset*0.5], color='#667eea', linewidth=6, alpha=0.8)
        # Right arm  
        ax.plot([8, 9], [arm_y, arm_y - 1 - y_offset*0.5], color='#667eea', linewidth=6, alpha=0.8)
        
        # Legs
        ax.plot([6, 6], [3.5 + y_offset, 1.5], color='#667eea', linewidth=6, alpha=0.8)
        ax.plot([7, 7], [3.5 + y_offset, 1.5], color='#667eea', linewidth=6, alpha=0.8)
        
        # Ground line
        ax.plot([0, 10], [1.5, 1.5], color='#4F4F4F', linewidth=2, alpha=0.6)
        
        # Title and instructions
        ax.text(5, 5.5, 'PUSH-UP FORM', ha='center', va='center', 
                fontsize=16, color='#FAFAFA', weight='bold')
        ax.text(5, 0.8, 'Lower chest to ground, push back up', ha='center', va='center',
                fontsize=12, color='#FAFAFA', alpha=0.8)
        
        # Form indicator
        if y_offset < -0.2:
            ax.text(5, 2.5, '⬇ DOWN POSITION', ha='center', va='center',
                    fontsize=10, color='#48bb78', weight='bold')
        elif y_offset > 0.2:
            ax.text(5, 2.5, '⬆ UP POSITION', ha='center', va='center',
                    fontsize=10, color='#667eea', weight='bold')
    
    anim = animation.FuncAnimation(fig, animate, frames=40, interval=100, repeat=True)
    plt.tight_layout()
    
    # Save as base64 encoded GIF
    buffer = io.BytesIO()
    anim.save(buffer, format='gif', writer='pillow', fps=10)
    buffer.seek(0)
    gif_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return f"data:image/gif;base64,{gif_base64}"

def create_squat_gif():
    """Create animated squat form GIF"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.set_facecolor('#262730')
    fig.patch.set_facecolor('#262730')
    ax.axis('off')
    
    def animate(frame):
        ax.clear()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_facecolor('#262730')
        ax.axis('off')
        
        # Animation cycle
        t = frame / 30.0
        y_offset = -1.2 * np.sin(t * 2 * np.pi) ** 2  # Squat down motion
        
        # Head
        head_pos = (5, 6.5 + y_offset)
        ax.add_patch(Circle(head_pos, 0.3, color='#667eea', alpha=0.8))
        
        # Body (torso)
        torso_top = (5, 6.2 + y_offset)
        torso_bottom = (5, 4.5 + y_offset)
        ax.plot([torso_top[0], torso_bottom[0]], [torso_top[1], torso_bottom[1]], 
                color='#667eea', linewidth=8, alpha=0.8)
        
        # Arms (raised forward during squat)
        arm_extend = max(0, -y_offset) * 1.5
        ax.plot([5, 3.5 - arm_extend], [5.5 + y_offset, 5.5 + y_offset], 
                color='#667eea', linewidth=6, alpha=0.8)
        ax.plot([5, 6.5 + arm_extend], [5.5 + y_offset, 5.5 + y_offset], 
                color='#667eea', linewidth=6, alpha=0.8)
        
        # Legs
        leg_angle = max(0, -y_offset) * 0.8
        # Left leg
        ax.plot([5, 4.5 - leg_angle], [4.5 + y_offset, 2.5 + y_offset], 
                color='#667eea', linewidth=6, alpha=0.8)
        ax.plot([4.5 - leg_angle, 4.5 - leg_angle], [2.5 + y_offset, 1.5], 
                color='#667eea', linewidth=6, alpha=0.8)
        
        # Right leg
        ax.plot([5, 5.5 + leg_angle], [4.5 + y_offset, 2.5 + y_offset], 
                color='#667eea', linewidth=6, alpha=0.8)
        ax.plot([5.5 + leg_angle, 5.5 + leg_angle], [2.5 + y_offset, 1.5], 
                color='#667eea', linewidth=6, alpha=0.8)
        
        # Ground line
        ax.plot([0, 10], [1.5, 1.5], color='#4F4F4F', linewidth=2, alpha=0.6)
        
        # Title and instructions
        ax.text(5, 7.5, 'SQUAT FORM', ha='center', va='center', 
                fontsize=16, color='#FAFAFA', weight='bold')
        ax.text(5, 0.8, 'Lower hips back, keep chest up', ha='center', va='center',
                fontsize=12, color='#FAFAFA', alpha=0.8)
        
        # Form indicator
        if y_offset < -0.8:
            ax.text(5, 3.8 + y_offset, '⬇ BOTTOM POSITION', ha='center', va='center',
                    fontsize=10, color='#48bb78', weight='bold')
        elif y_offset > -0.2:
            ax.text(5, 3.8 + y_offset, '⬆ STANDING', ha='center', va='center',
                    fontsize=10, color='#667eea', weight='bold')
    
    anim = animation.FuncAnimation(fig, animate, frames=60, interval=100, repeat=True)
    plt.tight_layout()
    
    # Save as base64 encoded GIF
    buffer = io.BytesIO()
    anim.save(buffer, format='gif', writer='pillow', fps=10)
    buffer.seek(0)
    gif_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return f"data:image/gif;base64,{gif_base64}"

def create_lunge_gif():
    """Create animated lunge form GIF"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.set_facecolor('#262730')
    fig.patch.set_facecolor('#262730')
    ax.axis('off')
    
    def animate(frame):
        ax.clear()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.set_facecolor('#262730')
        ax.axis('off')
        
        # Animation cycle
        t = frame / 40.0
        lunge_offset = 1.5 * np.sin(t * 2 * np.pi)  # Forward/back motion
        y_offset = -0.8 * np.abs(np.sin(t * 2 * np.pi))  # Up/down motion
        
        # Head
        head_pos = (5 + lunge_offset*0.3, 6.5 + y_offset)
        ax.add_patch(Circle(head_pos, 0.3, color='#667eea', alpha=0.8))
        
        # Body (torso)
        torso_top = (5 + lunge_offset*0.3, 6.2 + y_offset)
        torso_bottom = (5 + lunge_offset*0.3, 4.5 + y_offset)
        ax.plot([torso_top[0], torso_bottom[0]], [torso_top[1], torso_bottom[1]], 
                color='#667eea', linewidth=8, alpha=0.8)
        
        # Arms
        ax.plot([torso_top[0], torso_top[0] - 1], [5.5 + y_offset, 5.5 + y_offset], 
                color='#667eea', linewidth=6, alpha=0.8)
        ax.plot([torso_top[0], torso_top[0] + 1], [5.5 + y_offset, 5.5 + y_offset], 
                color='#667eea', linewidth=6, alpha=0.8)
        
        # Legs - front leg
        front_leg_x = 5 + lunge_offset*0.3 + lunge_offset
        ax.plot([5 + lunge_offset*0.3, front_leg_x], [4.5 + y_offset, 3 + y_offset], 
                color='#667eea', linewidth=6, alpha=0.8)
        ax.plot([front_leg_x, front_leg_x], [3 + y_offset, 1.5], 
                color='#667eea', linewidth=6, alpha=0.8)
        
        # Legs - back leg
        back_leg_x = 5 + lunge_offset*0.3 - lunge_offset
        ax.plot([5 + lunge_offset*0.3, back_leg_x], [4.5 + y_offset, 3 + y_offset], 
                color='#667eea', linewidth=6, alpha=0.8)
        ax.plot([back_leg_x, back_leg_x], [3 + y_offset, 2], 
                color='#667eea', linewidth=6, alpha=0.8)
        
        # Ground line
        ax.plot([0, 10], [1.5, 1.5], color='#4F4F4F', linewidth=2, alpha=0.6)
        
        # Title and instructions
        ax.text(5, 7.5, 'LUNGE FORM', ha='center', va='center', 
                fontsize=16, color='#FAFAFA', weight='bold')
        ax.text(5, 0.8, 'Step forward, 90° angles, push back', ha='center', va='center',
                fontsize=12, color='#FAFAFA', alpha=0.8)
        
        # Form indicator
        if abs(lunge_offset) > 1:
            ax.text(5, 3.5 + y_offset, '⬇ LUNGE POSITION', ha='center', va='center',
                    fontsize=10, color='#48bb78', weight='bold')
        else:
            ax.text(5, 3.5 + y_offset, '⬆ STARTING POSITION', ha='center', va='center',
                    fontsize=10, color='#667eea', weight='bold')
    
    anim = animation.FuncAnimation(fig, animate, frames=80, interval=100, repeat=True)
    plt.tight_layout()
    
    # Save as base64 encoded GIF
    buffer = io.BytesIO()
    anim.save(buffer, format='gif', writer='pillow', fps=10)
    buffer.seek(0)
    gif_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return f"data:image/gif;base64,{gif_base64}"

def create_plank_gif():
    """Create animated plank form GIF"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_facecolor('#262730')
    fig.patch.set_facecolor('#262730')
    ax.axis('off')
    
    def animate(frame):
        ax.clear()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_facecolor('#262730')
        ax.axis('off')
        
        # Animation cycle - slight breathing motion
        t = frame / 30.0
        breathe = 0.1 * np.sin(t * 4 * np.pi)
        
        # Head
        head_pos = (2, 3.5 + breathe)
        ax.add_patch(Circle(head_pos, 0.3, color='#667eea', alpha=0.8))
        
        # Body (straight line plank)
        body_start = (2, 3.5 + breathe)
        body_end = (8, 3.5 + breathe)
        ax.plot([body_start[0], body_end[0]], [body_start[1], body_end[1]], 
                color='#667eea', linewidth=8, alpha=0.8)
        
        # Arms (supporting body)
        ax.plot([2, 1.5], [3.5 + breathe, 2.5], color='#667eea', linewidth=6, alpha=0.8)
        ax.plot([8, 8.5], [3.5 + breathe, 2.5], color='#667eea', linewidth=6, alpha=0.8)
        
        # Legs (straight)
        ax.plot([5, 5], [3.5 + breathe, 2.5], color='#667eea', linewidth=6, alpha=0.8)
        ax.plot([6, 6], [3.5 + breathe, 2.5], color='#667eea', linewidth=6, alpha=0.8)
        
        # Ground line
        ax.plot([0, 10], [2.5, 2.5], color='#4F4F4F', linewidth=2, alpha=0.6)
        
        # Alignment guide line
        ax.plot([2, 8], [3.5, 3.5], color='#48bb78', linewidth=2, alpha=0.6, linestyle='--')
        
        # Title and instructions
        ax.text(5, 5, 'PLANK FORM', ha='center', va='center', 
                fontsize=16, color='#FAFAFA', weight='bold')
        ax.text(5, 1.8, 'Straight line from head to heels', ha='center', va='center',
                fontsize=12, color='#FAFAFA', alpha=0.8)
        
        # Form indicator
        ax.text(5, 4.2, 'HOLD STEADY', ha='center', va='center',
                fontsize=10, color='#48bb78', weight='bold')
        
        # Timer simulation
        timer = int((frame % 300) / 10)  # 30 second cycle
        ax.text(9, 4.5, f'{timer}s', ha='center', va='center',
                fontsize=14, color='#667eea', weight='bold')
    
    anim = animation.FuncAnimation(fig, animate, frames=300, interval=100, repeat=True)
    plt.tight_layout()
    
    # Save as base64 encoded GIF
    buffer = io.BytesIO()
    anim.save(buffer, format='gif', writer='pillow', fps=10)
    buffer.seek(0)
    gif_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return f"data:image/gif;base64,{gif_base64}"

if __name__ == "__main__":
    print("Generating exercise form GIFs...")
    
    pushup_gif = create_pushup_gif()
    print("✓ Push-up GIF generated")
    
    squat_gif = create_squat_gif()
    print("✓ Squat GIF generated")
    
    lunge_gif = create_lunge_gif()
    print("✓ Lunge GIF generated")
    
    plank_gif = create_plank_gif()
    print("✓ Plank GIF generated")
    
    print("All exercise form GIFs generated successfully!")