# NudgeAI Video Walkthrough - Complete Guide with ElevenLabs

## 🎙️ Perfect Solution for Your Mic Issue!

Since your mic doesn't work, ElevenLabs is an excellent choice for generating professional-quality AI voice narration for your video walkthrough.

## 🚀 Quick Start with ElevenLabs

### Step 1: Get Your API Key
1. **Sign up for ElevenLabs** (Free tier available)
   - Go to https://elevenlabs.io
   - Create account (includes free credits)

2. **Get API Key**
   - Log in to https://elevenlabs.io/app/api-keys
   - Click "Create API Key"
   - Copy the key

3. **Set Environment Variable**
   ```bash
   # Linux/Mac
   export ELEVENLABS_API_KEY="your-api-key-here"
   
   # Or create .env file
   echo "ELEVENLABS_API_KEY=your-api-key-here" > .env
   ```

### Step 2: Generate Professional Audio
```bash
cd /home/lade/Hackathons/Mistral/Final/nudgeai
python generate_elevenlabs_audio.py
```

This will generate:
- `video_output/nudgeai_narration.mp3` - Professional AI voice narration
- `video_output/nudgeai_walkthrough_with_audio.mp4` - Video with audio

## 📁 Complete File Package

### Core Video Files
- **`video_output/nudgeai_walkthrough.html`** - Interactive video player
- **`video_output/nudgeai_captions.srt`** - Subtitle file
- **`video_output/walkthrough_script.md`** - Complete 2-minute script
- **`video_output/README.md`** - Documentation

### Audio Generation Scripts
- **`generate_elevenlabs_audio.py`** - ElevenLabs integration (Recommended)
- **`generate_audio_narration.py`** - Multiple TTS methods
- **`video_creation_guide.md`** - Step-by-step instructions

### Setup Guides
- **`video_output/elevenlabs_setup_guide.md`** - ElevenLabs configuration
- **`video_output/manual_audio_instructions.md`** - Alternative methods

## 🎵 ElevenLabs Voice Options

The script uses "Adam" voice (professional male). You can change to:

- **Elli** - Female, professional
- **Antoni** - Male, friendly  
- **Charlotte** - Female, clear
- **Arthur** - Male, deep

To change voice, modify the voice ID in `generate_elevenlabs_audio.py`

## 📋 Your 2-Minute Script

The script covers all key aspects of NudgeAI:

1. **Introduction** (0:00-0:15) - What is NudgeAI?
2. **Architecture** (0:15-0:35) - Tech stack overview
3. **Frontend** (0:35-0:55) - Dashboard features
4. **MCP Server** (0:55-1:15) - API integrations
5. **RAG System** (1:15-1:35) - Semantic search
6. **WhiteCircle** (1:35-1:50) - Quality assurance
7. **Proactive Nudging** (1:50-2:00) - Location-based suggestions

## 🎬 Complete Video Creation Process

### Option 1: Using ElevenLabs (Recommended)
1. Set up ElevenLabs API key
2. Run `python generate_elevenlabs_audio.py`
3. Get professional AI narration
4. Record screen walkthrough
5. Combine audio + screen recording
6. Add SRT captions
7. Export as MP4

### Option 2: Alternative TTS Services
If ElevenLabs doesn't work:
- Google Cloud Text-to-Speech
- Amazon Polly
- NaturalReaders.com
- TTSMP3.com

## 💰 Cost & Limits

**ElevenLabs Free Tier:**
- 10,000 characters per month
- Your script: ~1,500-2,000 characters
- **Cost: $0** (well within free limits!)

## 🎯 Final Output

You'll have:
- Professional AI-narrated audio
- Interactive HTML video player
- Complete subtitle support
- All files ready for presentation

## 🚀 You're All Set!

With ElevenLabs, you get:
- **Professional quality** - Studio-grade AI voices
- **No mic needed** - Perfect solution for your situation
- **Easy setup** - Just API key and run
- **Free tier** - No cost for your usage

**Start with ElevenLabs for the best results! 🎙️✨**