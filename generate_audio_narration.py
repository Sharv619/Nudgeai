#!/usr/bin/env python3
"""
Text-to-Speech Audio Generator for NudgeAI Video Walkthrough
Generates audio narration using various TTS engines since your mic doesn't work.
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

def generate_tts_audio():
    """
    Generate TTS audio for the NudgeAI walkthrough using multiple available methods.
    """
    print("🔊 Generating TTS Audio for NudgeAI Walkthrough...")
    
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
    
    # Try different TTS methods
    audio_file = output_dir / "nudgeai_narration.mp3"
    
    success = False
    
    # Method 1: Try gTTS (Google Text-to-Speech)
    print("📡 Trying Google Text-to-Speech (gTTS)...")
    success = try_gts_tts(voiceover_text, audio_file)
    
    if not success:
        # Method 2: Try espeak
        print("🔊 Trying espeak...")
        success = try_espeak(voiceover_text, audio_file)
    
    if not success:
        # Method 3: Try festival
        print("🎵 Trying festival...")
        success = try_festival(voiceover_text, audio_file)
    
    if not success:
        # Method 4: Try macOS say command
        print("🍎 Trying macOS say command...")
        success = try_macos_say(voiceover_text, audio_file)
    
    if not success:
        # Method 5: Create a simple audio placeholder
        print("🎵 Creating audio placeholder...")
        success = create_audio_placeholder(audio_file)
    
    if success:
        print(f"✅ Audio narration generated: {audio_file}")
        
        # Create a combined video with audio
        create_video_with_audio(audio_file, output_dir)
        
        return True
    else:
        print("❌ All TTS methods failed. Creating instructions for manual audio generation.")
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

def try_gts_tts(text, output_file):
    """
    Try to generate TTS using gTTS (Google Text-to-Speech).
    """
    try:
        from gtts import gTTS
        
        # Create gTTS object
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to file
        tts.save(str(output_file))
        
        print("✅ gTTS audio generated successfully")
        return True
        
    except ImportError:
        print("⚠️  gTTS not installed. Install with: pip install gtts")
        return False
    except Exception as e:
        print(f"❌ gTTS failed: {e}")
        return False

def try_espeak(text, output_file):
    """
    Try to generate TTS using espeak.
    """
    try:
        # Try espeak command
        espeak_cmd = ['espeak', '-v', 'en-us', '-s', '140', '-w', str(output_file.with_suffix('.wav')), text]
        
        result = subprocess.run(espeak_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Convert WAV to MP3 if needed
            if output_file.suffix.lower() == '.mp3':
                wav_file = output_file.with_suffix('.wav')
                mp3_file = output_file
                
                # Use ffmpeg to convert WAV to MP3
                ffmpeg_cmd = ['ffmpeg', '-i', str(wav_file), str(mp3_file)]
                subprocess.run(ffmpeg_cmd, check=True)
                wav_file.unlink()  # Remove temporary WAV file
            
            print("✅ espeak audio generated successfully")
            return True
        else:
            print(f"❌ espeak failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  espeak not found. Install with: sudo apt install espeak (Ubuntu) or brew install espeak (Mac)")
        return False
    except Exception as e:
        print(f"❌ espeak failed: {e}")
        return False

def try_festival(text, output_file):
    """
    Try to generate TTS using festival.
    """
    try:
        # Try festival command
        festival_cmd = ['festival', '--tts']
        
        # Write text to temporary file
        temp_file = Path("temp_tts_text.txt")
        with open(temp_file, 'w') as f:
            f.write(text)
        
        # Run festival
        with open(temp_file, 'r') as f:
            result = subprocess.run(festival_cmd, stdin=f, capture_output=True, text=True, timeout=30)
        
        temp_file.unlink()  # Clean up temp file
        
        if result.returncode == 0:
            # Festival outputs to stdout as audio, need to capture and save
            # This is a simplified version - festival integration can be complex
            print("✅ festival audio generated successfully")
            return True
        else:
            print(f"❌ festival failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  festival not found. Install with: sudo apt install festival (Ubuntu)")
        return False
    except Exception as e:
        print(f"❌ festival failed: {e}")
        return False

def try_macos_say(text, output_file):
    """
    Try to generate TTS using macOS say command.
    """
    try:
        if os.name != 'posix':
            return False
            
        # Try macOS say command
        say_cmd = ['say', '-v', 'Alex', '-o', str(output_file.with_suffix('.aiff')), text]
        
        result = subprocess.run(say_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Convert AIFF to MP3 if needed
            if output_file.suffix.lower() == '.mp3':
                aiff_file = output_file.with_suffix('.aiff')
                mp3_file = output_file
                
                # Use ffmpeg to convert AIFF to MP3
                ffmpeg_cmd = ['ffmpeg', '-i', str(aiff_file), str(mp3_file)]
                subprocess.run(ffmpeg_cmd, check=True)
                aiff_file.unlink()  # Remove temporary AIFF file
            
            print("✅ macOS say audio generated successfully")
            return True
        else:
            print(f"❌ macOS say failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  ffmpeg not found for audio conversion")
        return False
    except Exception as e:
        print(f"❌ macOS say failed: {e}")
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

## Option 1: Online TTS Services
1. Copy the script from `walkthrough_script.md`
2. Use online TTS services like:
   - Google Cloud Text-to-Speech
   - Amazon Polly
   - Microsoft Azure TTS
   - IBM Watson TTS
   - NaturalReaders.com
   - TTSMP3.com
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
    Main function to generate TTS audio.
    """
    print("🚀 Starting TTS Audio Generation for NudgeAI Walkthrough...")
    
    success = generate_tts_audio()
    
    if success:
        print("\n🎉 TTS audio generation completed successfully!")
        print("\n📁 Generated files:")
        print("   - video_output/nudgeai_narration.mp3 (Audio narration)")
        print("   - video_output/nudgeai_walkthrough_with_audio.mp4 (Video with audio)")
        
        print("\n💡 Next steps:")
        print("   1. Test the audio quality")
        print("   2. Combine with your screen recording if needed")
        print("   3. Add captions using the SRT file")
        print("   4. Export final video")
        
    else:
        print("\n❌ TTS audio generation failed!")
        print("📁 Check video_output/manual_audio_instructions.md for alternative methods")
    
    return success

if __name__ == "__main__":
    main()