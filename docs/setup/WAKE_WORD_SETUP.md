# Wake Word Detection Setup Guide

## 🎯 Overview

This guide will help you set up and test the voice-first AI assistant with working wake word detection.

## ✅ What's Fixed

1. **Working Wake Word**: Now uses "Picovoice" (built-in) instead of placeholder "Hey Cheffy"
2. **Automatic Flow**: Wake word → recording → silence detection → processing
3. **No Manual Buttons**: Fully hands-free operation
4. **Visual Feedback**: Animated indicator when listening for wake word

## 🚀 Quick Setup

### 1. Get Picovoice Access Key

1. Go to [Picovoice Console](https://console.picovoice.ai/)
2. Sign up for a free account
3. Navigate to "Access Keys"
4. Create a new access key
5. Copy the key

### 2. Configure Environment

Add to your `frontend/.env.local`:
```bash
VITE_PICOVOICE_ACCESS_KEY=your_access_key_here
```

### 3. Install Dependencies

```bash
cd frontend
npm install
```

### 4. Test the System

1. Start your backend: `uvicorn main:app --reload`
2. Start your frontend: `npm run dev`
3. Go to the Cheffy page
4. Start a cooking session
5. Say "Picovoice" to activate the assistant

## 🎤 How It Works Now

### **Before (Broken)**:
```
User presses record → Manual recording → User presses stop → Processing
```

### **After (Fixed)**:
```
User says "Picovoice" → Auto-recording starts → User speaks → Silence detected → Auto-stop → Processing
```

## 🔧 Testing Steps

### 1. Basic Wake Word Test
1. Start a cooking session
2. Look for the animated "Listening for 'Picovoice'" button
3. Say "Picovoice" clearly
4. You should see the button change to "Active" and recording start automatically

### 2. Full Voice Flow Test
1. Say "Picovoice"
2. Immediately ask a question like "What's the next step?"
3. Wait for silence (1.5 seconds)
4. Recording should stop automatically
5. You should hear the AI response

### 3. Debug Information
Check browser console for these messages:
- `"Started listening for wake word 'Picovoice'"`
- `"Wake word detected! Keyword index: 0"`
- `"Automatic recording started with silence detection"`
- `"Silence detected, stopping recording"`

## 🎯 Creating Custom "Hey Cheffy" Wake Word

### Option 1: Picovoice Console (Recommended)
1. Go to [Picovoice Console](https://console.picovoice.ai/)
2. Navigate to "Porcupine" → "Custom Keywords"
3. Create a new keyword "Hey Cheffy"
4. Download the `.ppn` file
5. Place it in `frontend/public/models/hey-cheffy.ppn`
6. Update `wakeWordService.js`:

```javascript
// Replace this line in wakeWordService.js
keywords: ['picovoice'], // Using built-in wake word for testing

// With this:
keywords: [{ builtin: null, custom: "/models/hey-cheffy.ppn" }]
```

### Option 2: Use Built-in Keywords
For testing, you can use these built-in wake words:
- `'picovoice'` (current)
- `'porcupine'`
- `'alexa'`
- `'computer'`

## 🐛 Troubleshooting

### Wake Word Not Detected
1. **Check microphone permissions**: Allow microphone access in browser
2. **Check access key**: Verify `VITE_PICOVOICE_ACCESS_KEY` is set correctly
3. **Check console errors**: Look for initialization errors
4. **Test with different wake word**: Try "porcupine" instead of "picovoice"

### Recording Not Starting
1. **Check browser console**: Look for "Wake word detected!" message
2. **Check audio permissions**: Ensure microphone is accessible
3. **Restart browser**: Sometimes permissions need a fresh start

### Silence Detection Issues
1. **Adjust threshold**: Modify the silence threshold (currently 1500ms) in `wakeWordService.js`
2. **Check audio levels**: The system monitors volume levels - speak clearly
3. **Background noise**: Reduce background noise for better detection

### Performance Issues
1. **Close other tabs**: Audio processing can be resource-intensive
2. **Check browser**: Use Chrome or Firefox for best compatibility
3. **Update dependencies**: Ensure all packages are up to date

## 📊 Expected Behavior

### Visual Indicators
- **Gray button**: Session active, not listening
- **Animated button**: Listening for wake word
- **"Active" button**: Recording in progress
- **"Thinking"**: Processing audio

### Audio Flow
1. **Silent**: Wake word detection active
2. **"Picovoice"**: Triggers recording
3. **Your voice**: Being recorded
4. **Silence**: Auto-stops recording
5. **AI response**: TTS playback

## 🎉 Success Criteria

✅ Wake word detection works without manual intervention  
✅ Recording starts automatically after wake word  
✅ Recording stops automatically after silence  
✅ AI responds with voice  
✅ Visual indicators show correct status  
✅ No manual button presses required  

## 🔄 Next Steps

Once this is working:
1. Create custom "Hey Cheffy" wake word
2. Fine-tune silence detection timing
3. Add wake word sensitivity controls
4. Implement wake word training for better accuracy

## 📞 Support

If you encounter issues:
1. Check browser console for error messages
2. Verify all environment variables are set
3. Test with different browsers
4. Check microphone permissions
5. Try with built-in wake words first
