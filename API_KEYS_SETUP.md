# API Keys Setup Guide

This guide will help you obtain the necessary API keys for the voice-first AI assistant features.

## 🔑 Required API Keys

### 1. ElevenLabs API Key (for TTS)

**Purpose**: Generate high-quality speech synthesis for Cheffy's responses

**How to get it**:
1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for a free account
3. Navigate to your profile settings
4. Copy your API key from the "API Key" section
5. Add it to your backend `.env` file:
   ```bash
   ELEVENLABS_API_KEY=your_api_key_here
   ```

**Free Tier**: 10,000 characters per month (sufficient for testing)

### 2. Picovoice Access Key (for Wake Word Detection)

**Purpose**: Enable local "Hey Cheffy" wake word detection

**How to get it**:
1. Go to [Picovoice Console](https://console.picovoice.ai/)
2. Sign up for a free account
3. Navigate to "Access Keys"
4. Create a new access key
5. Add it to your frontend `.env.local` file:
   ```bash
   VITE_PICOVOICE_ACCESS_KEY=your_access_key_here
   ```

**Free Tier**: 100 hours of wake word detection per month

## 🚀 Quick Setup

### Backend Setup
1. Create a `.env` file in the `backend` directory
2. Add your API keys:
   ```bash
   # Existing keys
   OPENAI_API_KEY=your_openai_key
   
   # New keys for voice features
   ELEVENLABS_API_KEY=your_elevenlabs_key
   REDIS_URL=redis://localhost:6379  # Optional, for caching
   ```

### Frontend Setup
1. Create a `.env.local` file in the `frontend` directory
2. Add your API keys:
   ```bash
   VITE_API_BASE_URL=http://localhost:8000
   VITE_PICOVOICE_ACCESS_KEY=your_picovoice_key
   ```

## 🔧 Installation Steps

### 1. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Start Services
```bash
# Backend (in backend directory)
uvicorn main:app --reload

# Frontend (in frontend directory)
npm run dev
```

## 🎯 Testing Without API Keys

The system is designed to work gracefully without API keys:

- **TTS**: Will fall back to text-only responses
- **Wake Word**: Will be disabled, but text input still works
- **Core AI**: Will continue to function normally

## 🐛 Troubleshooting

### ElevenLabs Issues
- **"API key not found"**: Check your `.env` file in the backend directory
- **"Import error"**: Make sure you've installed the requirements: `pip install elevenlabs`
- **"Rate limit exceeded"**: Upgrade to a paid plan or wait for next month

### Picovoice Issues
- **"Access key not found"**: Check your `.env.local` file in the frontend directory
- **"Import error"**: Make sure you've installed the dependencies: `npm install`
- **"Wake word not detected"**: Check microphone permissions in your browser

### General Issues
- **Environment variables not loading**: Restart your development server
- **CORS errors**: Make sure your backend is running on the correct port
- **Audio not playing**: Check browser audio permissions

## 💡 Tips

1. **Start with text-only**: You can test the core functionality without voice features
2. **Use browser dev tools**: Check the console for helpful error messages
3. **Test microphone permissions**: Make sure your browser allows microphone access
4. **Check network tab**: Monitor API calls to see if keys are working

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for all sensitive data
- Consider using a secrets manager for production
- Rotate keys regularly for security

## 📞 Support

If you encounter issues:
1. Check the browser console for error messages
2. Verify your API keys are correct
3. Ensure all dependencies are installed
4. Check that your environment files are in the correct locations

---

Once you have your API keys set up, the voice-first features will be automatically enabled!
