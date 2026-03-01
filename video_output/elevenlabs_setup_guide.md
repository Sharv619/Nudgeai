# ElevenLabs Setup Guide

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
