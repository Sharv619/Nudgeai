#!/usr/bin/env python3
"""
Web-based TTS Solution for NudgeAI Video Walkthrough
Creates a simple HTML page that uses browser's built-in TTS to generate audio.
"""

import os
from pathlib import Path

def create_web_tts_solution():
    """
    Create a web-based TTS solution using browser's built-in speech synthesis.
    """
    print("🌐 Creating Web-based TTS Solution...")
    
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
    
    # Create HTML TTS page
    html_content = create_tts_html_page(voiceover_text)
    
    # Save files
    html_file = output_dir / "nudgeai_tts_generator.html"
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Web TTS solution created: {html_file}")
    
    # Create a simple audio extraction guide
    create_audio_extraction_guide(output_dir)
    
    return True

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

def create_tts_html_page(script_text):
    """
    Create an HTML page with browser TTS functionality.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NudgeAI TTS Audio Generator</title>
    <style>
        :root {{
            --primary-color: #3b82f6;
            --secondary-color: #1f2937;
            --text-color: #111827;
            --bg-color: #f3f4f6;
            --card-bg: #ffffff;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .container {{
            max-width: 800px;
            width: 100%;
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            color: var(--secondary-color);
            margin-bottom: 1rem;
            text-align: center;
        }}
        
        .subtitle {{
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 500;
        }}
        
        .controls {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 1rem;
        }}
        
        .btn-primary {{
            background-color: var(--primary-color);
            color: white;
        }}
        
        .btn-primary:hover {{
            background-color: #2563eb;
        }}
        
        .btn-secondary {{
            background-color: #64748b;
            color: white;
        }}
        
        .btn-secondary:hover {{
            background-color: #475569;
        }}
        
        .btn-danger {{
            background-color: #ef4444;
            color: white;
        }}
        
        .btn-danger:hover {{
            background-color: #dc2626;
        }}
        
        .status {{
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 500;
            min-height: 1.5rem;
        }}
        
        .settings {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
            padding: 1rem;
            background: #f8fafc;
            border-radius: 8px;
        }}
        
        .setting-group {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .setting-group label {{
            font-size: 0.875rem;
            color: #666;
        }}
        
        .setting-group input {{
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
        }}
        
        .script-preview {{
            background: #f1f5f9;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            max-height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9rem;
        }}
        
        .instructions {{
            background: #e0f2fe;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            border-left: 4px solid var(--primary-color);
        }}
        
        .instructions h3 {{
            margin: 0 0 0.5rem 0;
            color: var(--primary-color);
        }}
        
        .instructions ol {{
            margin: 0;
            padding-left: 1.5rem;
        }}
        
        .instructions li {{
            margin-bottom: 0.5rem;
            line-height: 1.5;
        }}
        
        .progress {{
            width: 100%;
            height: 8px;
            background-color: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 2rem;
        }}
        
        .progress-bar {{
            height: 100%;
            background-color: var(--primary-color);
            width: 0%;
            transition: width 0.1s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ NudgeAI TTS Audio Generator</h1>
        <p class="subtitle">Generate audio narration using your browser's built-in speech synthesis</p>
        
        <div class="instructions">
            <h3>How to Use:</h3>
            <ol>
                <li>Adjust the voice settings below (optional)</li>
                <li>Click "Start Narration" to begin</li>
                <li>Use your computer's screen recording software to record the audio</li>
                <li>Record for the full 2 minutes while the narration plays</li>
                <li>Save the recording as MP3 and place it in the video_output folder</li>
            </ol>
        </div>
        
        <div class="settings">
            <div class="setting-group">
                <label for="rate">Speech Rate</label>
                <input type="range" id="rate" min="0.5" max="2" step="0.1" value="1">
                <span id="rate-value">1.0</span>
            </div>
            <div class="setting-group">
                <label for="pitch">Pitch</label>
                <input type="range" id="pitch" min="0" max="2" step="0.1" value="1">
                <span id="pitch-value">1.0</span>
            </div>
            <div class="setting-group">
                <label for="volume">Volume</label>
                <input type="range" id="volume" min="0" max="1" step="0.1" value="1">
                <span id="volume-value">1.0</span>
            </div>
        </div>
        
        <div class="script-preview">
            <strong>Script Text:</strong><br><br>
            {script_text}
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="startNarration()">▶️ Start Narration</button>
            <button class="btn btn-secondary" onclick="pauseNarration()">⏸️ Pause</button>
            <button class="btn btn-danger" onclick="stopNarration()">⏹️ Stop</button>
        </div>
        
        <div class="status" id="status">Ready to start narration</div>
        
        <div class="progress">
            <div class="progress-bar" id="progress-bar"></div>
        </div>
        
        <div class="instructions">
            <h3>Recording Tips:</h3>
            <ul>
                <li><strong>Use screen recording software</strong> like OBS Studio, Camtasia, or QuickTime</li>
                <li><strong>Record system audio</strong> to capture the browser's speech synthesis</li>
                <li><strong>Test the volume</strong> first to ensure good audio quality</li>
                <li><strong>Minimize background noise</strong> during recording</li>
                <li><strong>Save as MP3</strong> and name it: nudgeai_narration.mp3</li>
            </ul>
        </div>
    </div>

    <script>
        let utterance = null;
        let voices = [];
        let isSpeaking = false;
        let startTime = 0;
        let totalDuration = 0;
        
        const scriptText = `{script_text}`;
        
        // Initialize
        window.onload = function() {{
            speechSynthesis.onvoiceschanged = function() {{
                voices = speechSynthesis.getVoices();
                updateStatus("Voice loaded. Ready to start.");
            }};
            
            // Update status elements
            document.getElementById('rate').addEventListener('input', function() {{
                document.getElementById('rate-value').textContent = this.value;
            }});
            
            document.getElementById('pitch').addEventListener('input', function() {{
                document.getElementById('pitch-value').textContent = this.value;
            }});
            
            document.getElementById('volume').addEventListener('input', function() {{
                document.getElementById('volume-value').textContent = this.value;
            }});
        }};
        
        function startNarration() {{
            if (isSpeaking) {{
                stopNarration();
            }}
            
            utterance = new SpeechSynthesisUtterance(scriptText);
            
            // Get voice settings
            const rate = parseFloat(document.getElementById('rate').value);
            const pitch = parseFloat(document.getElementById('pitch').value);
            const volume = parseFloat(document.getElementById('volume').value);
            
            // Set voice properties
            utterance.rate = rate;
            utterance.pitch = pitch;
            utterance.volume = volume;
            
            // Try to select a good voice
            if (voices.length > 0) {{
                // Prefer English voices
                const englishVoices = voices.filter(v => v.lang.includes('en'));
                if (englishVoices.length > 0) {{
                    utterance.voice = englishVoices[0];
                }} else {{
                    utterance.voice = voices[0];
                }}
            }}
            
            // Event handlers
            utterance.onstart = function() {{
                isSpeaking = true;
                startTime = Date.now();
                totalDuration = estimateDuration(scriptText, rate);
                updateStatus("Narration started...");
                updateProgress();
            }};
            
            utterance.onend = function() {{
                isSpeaking = false;
                updateStatus("Narration completed!");
                document.getElementById('progress-bar').style.width = '100%';
            }};
            
            utterance.onerror = function(event) {{
                updateStatus("Error: " + event.error);
                isSpeaking = false;
            }};
            
            speechSynthesis.speak(utterance);
        }}
        
        function pauseNarration() {{
            if (isSpeaking) {{
                speechSynthesis.pause();
                updateStatus("Narration paused");
            }}
        }}
        
        function stopNarration() {{
            speechSynthesis.cancel();
            isSpeaking = false;
            updateStatus("Narration stopped");
            document.getElementById('progress-bar').style.width = '0%';
        }}
        
        function updateStatus(message) {{
            document.getElementById('status').textContent = message;
        }}
        
        function updateProgress() {{
            if (!isSpeaking) return;
            
            const elapsed = Date.now() - startTime;
            const progress = Math.min((elapsed / totalDuration) * 100, 100);
            document.getElementById('progress-bar').style.width = progress + '%';
            
            if (progress < 100) {{
                requestAnimationFrame(updateProgress);
            }}
        }}
        
        function estimateDuration(text, rate) {{
            // Rough estimation: ~150 words per minute
            const words = text.split(' ').length;
            const baseDuration = (words / 150) * 60 * 1000; // in milliseconds
            return baseDuration / rate;
        }}
    </script>
</body>
</html>"""
    
    return html_content

def create_audio_extraction_guide(output_dir):
    """
    Create a guide for extracting audio from the web TTS solution.
    """
    guide = """# Audio Extraction Guide

## Using the Web TTS Solution

The `nudgeai_tts_generator.html` file provides a browser-based TTS solution that uses your computer's built-in speech synthesis.

### Step-by-Step Instructions:

1. **Open the HTML file** in your web browser:
   - Navigate to `video_output/nudgeai_tts_generator.html`
   - Open it in Chrome, Firefox, Safari, or Edge

2. **Adjust Settings** (Optional):
   - Speech Rate: Controls how fast the voice speaks (0.5 to 2.0)
   - Pitch: Controls the voice tone (0.0 to 2.0)
   - Volume: Controls the loudness (0.0 to 1.0)

3. **Record the Audio**:
   - Use screen recording software that can capture system audio
   - Recommended software:
     - **OBS Studio** (Free, cross-platform)
     - **Camtasia** (Paid, professional)
     - **QuickTime Player** (Mac, free)
     - **Windows Game Bar** (Windows 10+, free)

4. **Recording Setup**:
   - Configure your recording software to capture system audio
   - Test the volume levels before recording
   - Ensure no background noise or interruptions

5. **Start Recording**:
   - Click "Start Narration" in the browser
   - Begin recording with your screen recording software
   - Let the full narration play (approximately 2 minutes)
   - Stop recording when the narration ends

6. **Save the Audio**:
   - Export the recording as MP3 format
   - Name the file: `nudgeai_narration.mp3`
   - Place it in the `video_output` folder

### Alternative: Direct Audio Recording

If you prefer not to use screen recording software:

1. **Use a separate device** (phone, tablet, or second computer)
2. **Play the narration** from the browser
3. **Record with the device's microphone**
4. **Transfer the recording** to your computer
5. **Convert to MP3** if needed
6. **Save as** `nudgeai_narration.mp3` in the `video_output` folder

### Audio Specifications:
- Format: MP3
- Duration: ~2 minutes
- Quality: Standard recording quality
- Volume: Consistent level throughout

### Troubleshooting:
- **No sound**: Check browser permissions for speech synthesis
- **Poor quality**: Use better recording software or environment
- **Volume issues**: Adjust browser/system volume before recording
- **Background noise**: Record in a quiet environment

### After Getting Audio:
1. Place `nudgeai_narration.mp3` in the `video_output` folder
2. Use it with your screen recording of the NudgeAI project
3. Add captions using the SRT file
4. Export final video as MP4

This solution requires no API keys, no subscriptions, and works with any modern browser!
"""
    
    guide_file = output_dir / "audio_extraction_guide.md"
    with open(guide_file, 'w') as f:
        f.write(guide)
    
    print(f"📝 Audio extraction guide created: {guide_file}")

def main():
    """
    Main function to create the web TTS solution.
    """
    print("🚀 Creating Web-based TTS Solution for NudgeAI Walkthrough...")
    
    success = create_web_tts_solution()
    
    if success:
        print("\n🎉 Web TTS solution created successfully!")
        print("\n📁 Generated files:")
        print("   - video_output/nudgeai_tts_generator.html (Browser-based TTS)")
        print("   - video_output/audio_extraction_guide.md (Recording instructions)")
        
        print("\n💡 How to use:")
        print("   1. Open the HTML file in your browser")
        print("   2. Adjust voice settings if desired")
        print("   3. Use screen recording software to capture the audio")
        print("   4. Save as nudgeai_narration.mp3 in video_output folder")
        print("   5. Combine with your screen recording")
        
    else:
        print("\n❌ Web TTS solution creation failed!")
    
    return success

if __name__ == "__main__":
    main()