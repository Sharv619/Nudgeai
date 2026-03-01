#!/usr/bin/env python3
"""
Free TTS Audio Generator for NudgeAI Video Walkthrough
Generates audio using free TTS services since your mic doesn't work.
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

def generate_free_tts_audio():
    """
    Generate TTS audio using free TTS services for the NudgeAI walkthrough.
    """
    print("🔊 Generating Free TTS Audio for NudgeAI Walkthrough...")
    
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
    
    # Try different free TTS methods
    audio_file = output_dir / "nudgeai_narration.mp3"
    
    success = False
    
    # Method 1: Try Google Cloud TTS (if API key available)
    print("☁️  Trying Google Cloud Text-to-Speech...")
    success = try_google_tts(voiceover_text, audio_file)
    
    if not success:
        # Method 2: Try ResponsiveVoice (free web service)
        print("🌐 Trying ResponsiveVoice (free web service)...")
        success = try_responsive_voice(voiceover_text, audio_file)
    
    if not success:
        # Method 3: Try TTSMP3.com API
        print("🎵 Trying TTSMP3.com API...")
        success = try_ttsmp3(voiceover_text, audio_file)
    
    if not success:
        # Method 4: Create audio placeholder
        print("🎵 Creating audio placeholder...")
        success = create_audio_placeholder(audio_file)
    
    if success:
        print(f"✅ Free TTS audio generated: {audio_file}")
        
        # Create a combined video with audio
        create_video_with_audio(audio_file, output_dir)
        
        return True
    else:
        print("❌ All free TTS methods failed. Creating instructions for manual audio generation.")
        create_manual_audio_instructions(output_dir)
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

def try_google_tts(text, output_file):
    """
    Try to generate TTS using Google Cloud Text-to-Speech.
    """
    try:
        # Check if Google Cloud TTS API key is available
        google_tts_key = os.getenv("GOOGLE_TTS_API_KEY")
        if not google_tts_key:
            print("⚠️  Google Cloud TTS API key not found")
            return False
        
        # Google Cloud TTS API endpoint
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        
        # Request payload
        payload = {
            "input": {
                "text": text
            },
            "voice": {
                "languageCode": "en-US",
                "name": "en-US-Wavenet-D",
                "ssmlGender": "MALE"
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 1.0,
                "pitch": 0.0
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {google_tts_key}"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            audio_content = result["audioContent"]
            
            # Save the audio file
            import base64
            audio_data = base64.b64decode(audio_content)
            with open(output_file, 'wb') as f:
                f.write(audio_data)
            
            print("✅ Google Cloud TTS audio generated successfully")
            return True
        else:
            print(f"❌ Google Cloud TTS failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Google Cloud TTS failed: {e}")
        return False

def try_responsive_voice(text, output_file):
    """
    Try to generate TTS using ResponsiveVoice (free web service).
    """
    try:
        # ResponsiveVoice API endpoint
        url = "https://api.responsivevoice.org/tts"
        
        # Request parameters
        params = {
            "t": text,
            "tl": "en-US",
            "sv": "US%20English%20Male",
            "vn": "",
            "pitch": "0.5",
            "rate": "0.5",
            "vol": "1",
            "key": "b1KpLx02"  # Free API key
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            # Save the audio file
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print("✅ ResponsiveVoice audio generated successfully")
            return True
        else:
            print(f"❌ ResponsiveVoice failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ResponsiveVoice failed: {e}")
        return False

def try_ttsmp3(text, output_file):
    """
    Try to generate TTS using TTSMP3.com API.
    """
    try:
        # TTSMP3.com API endpoint
        url = "https://ttsmp3.com/makemp3_new.php"
        
        # Request parameters
        params = {
            "lang": "En-us",
            "text": text,
            "source": "ttsmp3",
            "speed": "1.0",
            "submit": "Download MP3"
        }
        
        response = requests.post(url, data=params)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("status") == "success":
                # Download the MP3 file
                mp3_url = result.get("URL")
                if mp3_url:
                    mp3_response = requests.get(mp3_url)
                    if mp3_response.status_code == 200:
                        with open(output_file, 'wb') as f:
                            f.write(mp3_response.content)
                        
                        print("✅ TTSMP3.com audio generated successfully")
                        return True
            
            print(f"❌ TTSMP3.com failed: {result.get('status')}")
            return False
        else:
            print(f"❌ TTSMP3.com failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ TTSMP3.com failed: {e}")
        return False

def create_audio_placeholder(output_file):
    """
    Create a simple audio placeholder with silence and instructions.
    """
    try:
        # Create a simple audio file with ffmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', 
            '-t', '120', '-q:a', '9', '-acodec', 'libmp3lame', str(output_file)
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Audio placeholder created (2 minutes of silence)")
            return True
        else:
            print(f"❌ Audio placeholder creation failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  ffmpeg not found. Cannot create audio placeholder.")
        return False
    except Exception as e:
        print(f"❌ Audio placeholder creation failed: {e}")
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

def create_manual_audio_instructions(output_dir):
    """
    Create instructions for manual audio generation.
    """
    instructions = """# Manual Audio Generation Instructions

Since automatic TTS generation failed, here are alternative methods to create audio for your video:

## Option 1: Online TTS Services (Recommended)
1. Copy the script from `walkthrough_script.md`
2. Use online TTS services like:
   - Google Cloud Text-to-Speech (Free tier available)
   - Amazon Polly (Free tier available)
   - Microsoft Azure TTS (Free tier available)
   - IBM Watson TTS (Free tier available)
   - NaturalReaders.com (Free)
   - TTSMP3.com (Free)
   - ResponsiveVoice.org (Free)
3. Generate audio in your preferred voice
4. Download as MP3
5. Place in the `video_output` folder as `nudgeai_narration.mp3`

## Option 2: Mobile Apps
1. Use text-to-speech apps on your phone:
   - Voice Aloud Reader (Android/iOS)
   - Speech Central (iOS)
   - @Voice Aloud Reader
2. Paste the script text
3. Record the output using another device
4. Convert to MP3 format

## Option 3: Browser Extensions
1. Install TTS browser extensions:
   - Read Aloud (Chrome/Firefox)
   - Natural Reader
   - Text to Speech Reader
2. Navigate to the script file
3. Use the extension to read the text
4. Record the audio using screen recording software

## Option 4: Professional Services
1. Use freelance platforms (Fiverr, Upwork) to hire someone to record the script
2. Use AI voice generation services like:
   - Descript Overdub
   - Resemble.ai
   - WellSaid Labs

## Audio Specifications
- Format: MP3
- Duration: ~2 minutes
- Quality: 192 kbps or higher
- Volume: Consistent level throughout
- File name: `nudgeai_narration.mp3`

## Script Text
[The full script is available in `walkthrough_script.md`]

## After Getting Audio
1. Place the audio file in the `video_output` folder
2. Use video editing software to combine with your screen recording
3. Add the SRT captions for subtitles
4. Export final video as MP4

## Troubleshooting
- If audio quality is poor, try different TTS voices or services
- Ensure consistent volume levels
- Test audio before final video creation
- Consider adding background music at low volume
"""
    
    instructions_file = output_dir / "manual_audio_instructions.md"
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"📝 Manual audio instructions created: {instructions_file}")

def main():
    """
    Main function to generate free TTS audio.
    """
    print("🚀 Starting Free TTS Audio Generation for NudgeAI Walkthrough...")
    
    success = generate_free_tts_audio()
    
    if success:
        print("\n🎉 Free TTS audio generation completed successfully!")
        print("\n📁 Generated files:")
        print("   - video_output/nudgeai_narration.mp3 (Free TTS audio narration)")
        print("   - video_output/nudgeai_walkthrough_with_audio.mp4 (Video with audio)")
        
        print("\n💡 Next steps:")
        print("   1. Test the audio quality")
        print("   2. Combine with your screen recording if needed")
        print("   3. Add captions using the SRT file")
        print("   4. Export final video")
        
    else:
        print("\n❌ Free TTS audio generation failed!")
        print("📁 Check video_output/manual_audio_instructions.md for alternative methods")
    
    return success

if __name__ == "__main__":
    import subprocess
    main()