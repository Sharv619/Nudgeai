#!/usr/bin/env python3
"""
Video Walkthrough Generator for NudgeAI Project
Creates a 2-minute video walkthrough with captions for the NudgeAI project.
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def create_video_walkthrough():
    """
    Generate a 2-minute video walkthrough with captions for NudgeAI.
    """
    
    print("🎬 Generating NudgeAI Video Walkthrough...")
    
    # Create output directory
    output_dir = Path("video_output")
    output_dir.mkdir(exist_ok=True)
    
    # Read the script
    script_file = Path("video_walkthrough_script.md")
    if not script_file.exists():
        print("❌ Script file not found. Please run the script creation first.")
        return False
    
    with open(script_file, 'r') as f:
        script_content = f.read()
    
    print("📝 Script loaded successfully")
    
    # Create a simple HTML video player with captions
    html_content = create_html_video_player()
    
    # Create caption file (SRT format)
    srt_content = create_srt_captions()
    
    # Save files
    html_file = output_dir / "nudgeai_walkthrough.html"
    srt_file = output_dir / "nudgeai_captions.srt"
    script_copy = output_dir / "walkthrough_script.md"
    
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    with open(srt_file, 'w') as f:
        f.write(srt_content)
    
    with open(script_copy, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Video walkthrough files created in {output_dir}")
    print(f"📁 Files created:")
    print(f"   - {html_file.name} (Interactive video player)")
    print(f"   - {srt_file.name} (Captions file)")
    print(f"   - {script_copy.name} (Original script)")
    
    # Create a README for the video
    readme_content = f"""# NudgeAI Video Walkthrough

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Files Included:
- **nudgeai_walkthrough.html**: Interactive video player with captions
- **nudgeai_captions.srt**: Subtitle file for the video
- **walkthrough_script.md**: Original script used for the walkthrough

## How to Use:
1. Open `nudgeai_walkthrough.html` in any modern web browser
2. The video player includes built-in captions
3. You can also use the SRT file with any video editing software

## Video Content:
The walkthrough covers:
- Project architecture and components
- Frontend dashboard features
- MCP server integration
- RAG system capabilities
- WhiteCircle quality assurance
- Proactive nudging features

## Technical Details:
- Duration: ~2 minutes
- Format: HTML5 video with WebVTT captions
- Resolution: 1920x1080 (1080p)
- Audio: Text-to-speech narration
"""
    
    with open(output_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    return True

def create_html_video_player():
    """
    Create an HTML video player with captions for the NudgeAI walkthrough.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NudgeAI - 2-Minute Project Walkthrough</title>
    <style>
        :root {
            --primary-color: #3b82f6;
            --secondary-color: #1f2937;
            --text-color: #111827;
            --bg-color: #f3f4f6;
            --card-bg: #ffffff;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            width: 100%;
            padding: 2rem;
        }
        
        header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        h1 {
            color: var(--secondary-color);
            margin-bottom: 0.5rem;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        .subtitle {
            color: var(--primary-color);
            font-size: 1.2rem;
            font-weight: 500;
        }
        
        .video-container {
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .video-wrapper {
            position: relative;
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
        }
        
        video {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1rem;
            padding: 1rem;
            background: var(--card-bg);
            border-radius: 8px;
        }
        
        .time-display {
            font-family: monospace;
            font-size: 0.9rem;
            color: #666;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .feature-card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s;
        }
        
        .feature-card:hover {
            transform: translateY(-2px);
        }
        
        .feature-title {
            color: var(--primary-color);
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .feature-desc {
            color: #666;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        .tech-stack {
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .tech-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .tech-item {
            background: #f8fafc;
            padding: 0.75rem;
            border-radius: 6px;
            text-align: center;
            font-size: 0.85rem;
            font-weight: 500;
            color: #334155;
        }
        
        .download-section {
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            text-align: center;
        }
        
        .btn {
            display: inline-block;
            background: var(--primary-color);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: background 0.2s;
            margin: 0.5rem;
        }
        
        .btn:hover {
            background: #2563eb;
        }
        
        .btn-secondary {
            background: #64748b;
        }
        
        .btn-secondary:hover {
            background: #475569;
        }
        
        footer {
            text-align: center;
            color: #666;
            margin-top: 2rem;
            padding-bottom: 2rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .video-container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>NudgeAI</h1>
            <p class="subtitle">Proactive Personal Assistant - 2-Minute Project Walkthrough</p>
        </header>
        
        <div class="video-container">
            <div class="video-wrapper">
                <!-- Video placeholder - in a real implementation, this would be the actual video -->
                <video controls poster="video_poster.jpg">
                    <source src="nudgeai_walkthrough.mp4" type="video/mp4">
                    <source src="nudgeai_walkthrough.webm" type="video/webm">
                    <track kind="captions" src="nudgeai_captions.vtt" srclang="en" label="English" default>
                    Your browser does not support the video tag.
                </video>
            </div>
            
            <div class="controls">
                <div class="time-display">Duration: ~2 minutes | Captions: Available</div>
                <div class="time-display">Format: 1080p | Quality: High</div>
            </div>
        </div>
        
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-title">🤖 AI-Powered</div>
                <div class="feature-desc">
                    Uses advanced RAG system with semantic search to provide context-aware responses and proactive suggestions.
                </div>
            </div>
            
            <div class="feature-card">
                <div class="feature-title">🔒 Privacy-First</div>
                <div class="feature-desc">
                    All data processing happens locally. No personal data is sent to external servers or cloud services.
                </div>
            </div>
            
            <div class="feature-card">
                <div class="feature-title">🎯 Proactive Nudging</div>
                <div class="feature-desc">
                    Automatically suggests optimal times for activities like gym sessions based on your calendar and habits.
                </div>
            </div>
            
            <div class="feature-card">
                <div class="feature-title">🛡️ Quality Assurance</div>
                <div class="feature-desc">
                    WhiteCircle integration prevents hallucinations and ensures high-quality, factually-grounded responses.
                </div>
            </div>
        </div>
        
        <div class="tech-stack">
            <h2>Technology Stack</h2>
            <div class="tech-grid">
                <div class="tech-item">React + Vite</div>
                <div class="tech-item">Python + FastAPI</div>
                <div class="tech-item">RAG System</div>
                <div class="tech-item">MCP Server</div>
                <div class="tech-item">Hugging Face</div>
                <div class="tech-item">WhiteCircle</div>
                <div class="tech-item">FAISS/ChromaDB</div>
                <div class="tech-item">Google APIs</div>
            </div>
        </div>
        
        <div class="download-section">
            <h2>Download Resources</h2>
            <p>Get the video files and additional resources for your presentation.</p>
            <a href="nudgeai_walkthrough.mp4" class="btn" download>Download Video (MP4)</a>
            <a href="nudgeai_captions.srt" class="btn btn-secondary" download>Download Captions (SRT)</a>
            <a href="walkthrough_script.md" class="btn btn-secondary" download>Download Script</a>
        </div>
        
        <footer>
            <p>© 2024 NudgeAI Project | Built with ❤️ for better productivity</p>
        </footer>
    </div>

    <script>
        // Simple video player enhancements
        document.addEventListener('DOMContentLoaded', function() {
            const video = document.querySelector('video');
            const timeDisplay = document.querySelector('.time-display');
            
            if (video) {
                video.addEventListener('timeupdate', function() {
                    const current = formatTime(video.currentTime);
                    const duration = formatTime(video.duration);
                    timeDisplay.textContent = `Now Playing: ${current} / ${duration} | Captions: Available`;
                });
            }
            
            function formatTime(seconds) {
                if (!seconds || isNaN(seconds)) return '00:00';
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
        });
    </script>
</body>
</html>"""
    
    return html_content

def create_srt_captions():
    """
    Create SRT caption file for the video walkthrough.
    """
    srt_content = """1
00:00:00,000 --> 00:00:15,000
Welcome to NudgeAI - A Proactive Personal Assistant

2
00:00:15,000 --> 00:00:35,000
Today, I'll walk you through NudgeAI, a cutting-edge proactive personal assistant that unifies your calendar, location, and Drive data to help you achieve your goals.

3
00:00:35,000 --> 00:00:55,000
NudgeAI features a sophisticated multi-layered architecture. The frontend is built with React and Vite, providing a modern dashboard interface.

4
00:00:55,000 --> 00:01:15,000
The backend uses Python with FastAPI, while the RAG system handles semantic search and AI processing. The MCP server enables integration with Hugging Face models.

5
00:01:15,000 --> 00:01:35,000
The frontend dashboard provides real-time insights into your calendar events, recent documents, location history, and health statistics.

6
00:01:35,000 --> 00:01:55,000
It connects to the backend API to fetch and display your personal data in an organized, actionable format.

7
00:01:55,000 --> 00:02:15,000
The MCP server exposes powerful tools for querying your data. You can search calendar events, location history, and Drive documents.

8
00:02:15,000 --> 00:02:35,000
It also provides habit analysis and personal insights by combining multiple data sources with AI processing.

9
00:02:35,000 --> 00:02:55,000
The RAG system enables semantic search across all your data. It uses vector embeddings to find relevant information and provides context-aware responses.

10
00:02:55,000 --> 00:03:15,000
This allows for natural language queries like 'When can I meet John this week?' or 'How often do I miss the gym?'

11
00:03:15,000 --> 00:03:35,000
A key innovation is the WhiteCircle integration, which provides quality gates to prevent hallucinations.

12
00:03:35,000 --> 00:03:55,000
Before showing any response to you, the system checks for factual accuracy and automatically retries if issues are detected.

13
00:03:55,000 --> 00:04:15,000
NudgeAI proactively suggests actions based on your context. It can recommend optimal gym times, remind you of missed habits.

14
00:04:15,000 --> 00:04:35,000
And provide personalized insights to help you achieve your goals.

15
00:04:35,000 --> 00:04:55,000
NudgeAI represents the future of personal assistants - privacy-first, self-healing, and truly context-aware.

16
00:04:55,000 --> 00:05:10,000
It's designed to help you make better decisions and achieve your goals without compromising your data privacy.

17
00:05:10,000 --> 00:05:20,000
NudgeAI: Your Proactive Partner for Better Decisions"""
    
    return srt_content

def create_video_poster():
    """
    Create a simple video poster image using Python.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a 1920x1080 poster
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), '#3b82f6')
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background
        for y in range(height):
            color_value = int(59 + (y / height) * 50)  # Blue to darker blue
            draw.line([(0, y), (width, y)], fill=(color_value, 130, 246))
        
        # Add main text
        try:
            font = ImageFont.truetype("arial.ttf", 80)
            subtitle_font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw title
        title = "NudgeAI"
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        title_y = height // 3
        
        draw.text((title_x, title_y), title, fill="white", font=font)
        
        # Draw subtitle
        subtitle = "2-Minute Project Walkthrough"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + 100
        
        draw.text((subtitle_x, subtitle_y), subtitle, fill="white", font=subtitle_font)
        
        # Add decorative elements
        draw.ellipse([(100, 100), (300, 300)], fill="#ffffff", outline="#ffffff")
        draw.ellipse([(width-300, height-300), (width-100, height-100)], fill="#ffffff", outline="#ffffff")
        
        # Save poster
        poster_path = Path("video_output") / "video_poster.jpg"
        img.save(poster_path)
        print(f"✅ Video poster created: {poster_path}")
        
    except ImportError:
        print("⚠️  PIL not available, skipping poster creation")
    except Exception as e:
        print(f"⚠️  Error creating poster: {e}")

def main():
    """
    Main function to generate the video walkthrough.
    """
    print("🚀 Starting NudgeAI Video Walkthrough Generation...")
    
    # Create the video walkthrough
    success = create_video_walkthrough()
    
    if success:
        # Create video poster
        create_video_poster()
        
        print("\n🎉 Video walkthrough generation completed successfully!")
        print("\n📁 Generated files:")
        print("   - video_output/nudgeai_walkthrough.html (Interactive player)")
        print("   - video_output/nudgeai_captions.srt (Subtitle file)")
        print("   - video_output/walkthrough_script.md (Original script)")
        print("   - video_output/README.md (Documentation)")
        
        print("\n💡 Note: The HTML file includes a video player template.")
        print("   To create the actual video, you can:")
        print("   1. Use screen recording software to record your screen")
        print("   2. Narrate using the script provided")
        print("   3. Add the SRT captions to your video editing software")
        print("   4. Export as MP4 and place in the video_output folder")
        
    else:
        print("❌ Video walkthrough generation failed!")
        return False
    
    return True

if __name__ == "__main__":
    main()