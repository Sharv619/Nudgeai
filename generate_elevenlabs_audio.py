#!/usr/bin/env python3
"""
ElevenLabs TTS Audio Generator for NudgeAI Video Walkthrough
Generates professional-quality audio using ElevenLabs API since your mic doesn't work.
"""

import os
import requests
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_elevenlabs_audio():
    """
    Generate TTS audio using ElevenLabs API for the NudgeAI walkthrough.
    """
    print("🔊 Generating ElevenLabs Audio for NudgeAI Walkthrough...")
    
    # Read the script
    script_file = Path("video_walkthrough_script.md")
    if not script_file.exists():
        print("❌ Script file not found. Please run the script creation first.")
        return False
    
    with open(script_file, 'r') as f:
        script_content = f.read()
    
    # Extract the voiceover text from the script
    voiceover_text = extract_voiceover_text(script_content)
    
    # Create output directory
    output_dir = Path("video_output")
    output_dir.mkdir(exist_ok=True)
    
    # Check for ElevenLabs API key
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ElevenLabs API key not found. Please set ELEVENLABS_API_KEY environment variable.")
        print("💡 Get your API key from: https://elevenlabs.io/app/api-keys")
        create_elevenlabs_setup_guide(output_dir)
        return False
    
    # Generate audio
    audio_file = output_dir / "nudgeai_narration.mp3"
    success = generate_with_elevenlabs(voiceover_text, audio_file, api_key)
    
    if success:
        print(f"✅ ElevenLabs audio generated: {audio_file}")
        
        # Create a combined video with audio
        create_video_with_audio(audio_file, output_dir)
        
        return True
    else:
        print("❌ ElevenLabs audio generation failed.")
        return False

def extract_voiceover_text(script_content):
    """
    Extract the voiceover text from the script.
    """
    lines = script_content.split('\n')
    voiceover_lines = []
    
    for line in lines:
        if line.startswith("**Voiceover:**"):
            # Extract text after "**Voiceover:**"
            voiceover_text = line.replace("**Voiceover:**", "").strip()
            voiceover_lines.append(voiceover_text)
        elif line.startswith("Voiceover:"):
            # Extract text after "Voiceover:"
            voiceover_text = line.replace("Voiceover:", "").strip()
            voiceover_lines.append(voiceover_text)
    
    # Join all voiceover lines
    full_script = " ".join(voiceover_lines)
    
    # Clean up the script
    full_script = full_script.replace("**", "").replace("*", "")
    
    return full_script

def generate_with_elevenlabs(text, output_file, api_key):
    """
    Generate audio using ElevenLabs API.
    """
    try:
        # ElevenLabs API endpoint - Using free voice and model
        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
        
        # Voice settings (Adam - professional male voice)
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        # Request payload - Using free model
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2",  # Free model
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.85
            }
        }
        
        print("📡 Sending request to ElevenLabs API...")
        
        # Make the request
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            # Save the audio file
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print("✅ ElevenLabs audio generated successfully")
            return True
        else:
            print(f"❌ ElevenLabs API error: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_video_with_audio(audio_file, output_dir):
    """
    Create a simple video with the generated audio and a static image.
    """
    try:
        # Create a simple video with the audio
        video_file = output_dir / "nudgeai_walkthrough_with_audio.mp4"
        image_file = output_dir / "video_poster.jpg"
        
        # If no image exists, create a simple one
        if not image_file.exists():
            create_simple_poster(image_file)
        
        # Use ffmpeg to create video with audio
        ffmpeg_cmd = [
            'ffmpeg', '-loop', '1', '-i', str(image_file), '-i', str(audio_file),
            '-c:v', 'libx264', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k',
            '-shortest', str(video_file)
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ Video with audio created: {video_file}")
            return True
        else:
            print(f"❌ Video creation failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  ffmpeg not found. Cannot create video with audio.")
        return False
    except Exception as e:
        print(f"❌ Video creation failed: {e}")
        return False

def create_simple_poster(image_file):
    """
    Create a simple poster image using Python.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a 1920x1080 poster
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), '#3b82f6')
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background
        for y in range(height):
            color_value = int(59 + (y / height) * 50)
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
        
        # Save poster
        img.save(image_file)
        print(f"✅ Simple poster created: {image_file}")
        
    except ImportError:
        print("⚠️  PIL not available, skipping poster creation")
    except Exception as e:
        print(f"⚠️  Error creating poster: {e}")

def create_elevenlabs_setup_guide(output_dir):
    """
    Create a setup guide for ElevenLabs integration.
    """
    guide = """# ElevenLabs Setup Guide

## Get Your ElevenLabs API Key

1. **Sign up for ElevenLabs**
   - Go to https://elevenlabs.io
   - Create a free account (includes free credits)

2. **Get Your API Key**
   - Log in to your ElevenLabs account
   - Go to https://elevenlabs.io/app/api-keys
   - Click "Create API Key"
   - Copy the generated key

3. **Set Environment Variable**
   - **Linux/Mac**: Add to your ~/.bashrc or ~/.zshrc:
     ```bash
     export ELEVENLABS_API_KEY="your-api-key-here"
     ```
   - **Windows**: Set in System Properties > Environment Variables
   - **Or create a .env file**:
     ```
     ELEVENLABS_API_KEY=your-api-key-here
     ```

4. **Install Required Package**
   ```bash
   pip install requests
   ```

## Alternative: Direct API Usage

If you prefer not to use environment variables, you can modify the script to include your API key directly:

```python
api_key = "your-api-key-here"  # Replace with your actual key
```

## Voice Options

The script uses the "Adam" voice (ID: 21m00Tcm4TlvDq8ikWAM). You can change to other voices:

- **Elli** (ID: 21m00Tcm4TlvDq8ikWAM) - Female, professional
- **Antoni** (ID: ErXwobaYiN019PkySvjV) - Male, friendly
- **Charlotte** (ID: XB0fDUnXU5powig78fxF) - Female, clear
- **Arthur** (ID: V1inm9XFEjcjZx2ehLX0) - Male, deep

To use a different voice, change the voice ID in the script.

## API Limits

- Free tier: 10,000 characters per month
- Your script is approximately 1,500-2,000 characters
- Should fit easily within free limits

## Troubleshooting

- **401 Error**: Check your API key is correct
- **429 Error**: You've hit rate limits, wait and try again
- **Network Error**: Check your internet connection
- **Audio Quality**: Adjust voice_settings in the script

## After Getting Audio

1. The script will generate `nudgeai_narration.mp3`
2. Use it with your screen recording
3. Add captions using the SRT file
4. Export final video as MP4
"""
    
    guide_file = output_dir / "elevenlabs_setup_guide.md"
    with open(guide_file, 'w') as f:
        f.write(guide)
    
    print(f"📝 ElevenLabs setup guide created: {guide_file}")

def main():
    """
    Main function to generate ElevenLabs audio.
    """
    print("🚀 Starting ElevenLabs Audio Generation for NudgeAI Walkthrough...")
    
    success = generate_elevenlabs_audio()
    
    if success:
        print("\n🎉 ElevenLabs audio generation completed successfully!")
        print("\n📁 Generated files:")
        print("   - video_output/nudgeai_narration.mp3 (Professional audio narration)")
        print("   - video_output/nudgeai_walkthrough_with_audio.mp4 (Video with audio)")
        
        print("\n💡 Next steps:")
        print("   1. Test the audio quality")
        print("   2. Combine with your screen recording if needed")
        print("   3. Add captions using the SRT file")
        print("   4. Export final video")
        
    else:
        print("\n❌ ElevenLabs audio generation failed!")
        print("📁 Check video_output/elevenlabs_setup_guide.md for setup instructions")
    
    return success

if __name__ == "__main__":
    import subprocess
    main()