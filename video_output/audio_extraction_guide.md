# Audio Extraction Guide

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
