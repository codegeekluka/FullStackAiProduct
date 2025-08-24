# Voice-First AI Assistant Architecture

## Overview

This document describes the refactored voice-first architecture for Cheffy AI, implementing the master prompt requirements for a production-grade, scalable cooking assistant.

## 🎯 Architecture Goals

- **Voice-First Experience**: Users say "Hey Cheffy" to activate the assistant
- **Cost Optimization**: Local wake word detection to avoid idle API costs
- **Streaming TTS**: ElevenLabs integration for natural speech responses
- **Session Management**: Proper cooking session state management
- **Scalable Design**: Modular architecture ready for mobile deployment

## 🔧 Key Components

### 1. Wake Word Detection (Frontend)

**File**: `frontend/src/services/wakeWordService.js`

- **Technology**: Picovoice Porcupine Web SDK
- **Wake Word**: "Hey Cheffy"
- **Benefits**: 
  - Runs locally in browser
  - No idle microphone streaming
  - Cost-effective activation
  - Works offline

**Implementation**:
```javascript
// Initialize wake word detection
await wakeWordService.initialize(
  () => onWakeWordDetected(),
  (error) => onWakeWordError(error)
);

// Start listening for wake word
await wakeWordService.startListening();
```

### 2. Text-to-Speech Service (Frontend)

**File**: `frontend/src/services/ttsService.js`

- **Technology**: ElevenLabs API
- **Features**:
  - Streaming audio playback
  - Audio caching
  - Queue management
  - Multiple voice support

**Implementation**:
```javascript
// Play streaming TTS response
await ttsService.playAudioStream(audioUrl);

// Generate and play text
await ttsService.playText("Hello, I'm Cheffy!");
```

### 3. AI Assistant Store (Frontend)

**File**: `frontend/src/stores/aiAssistantStore.js`

- **State Management**: Zustand
- **Features**:
  - Session lifecycle management
  - Voice-first workflow
  - Message history
  - Error handling

**Key States**:
- `sessionStatus`: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error'
- `isWakeWordListening`: Boolean for wake word detection
- `isVoiceActive`: Boolean for voice recording
- `isTTSPlaying`: Boolean for audio playback

### 4. Backend TTS Service

**File**: `backend/services/tts_service.py`

- **Technology**: ElevenLabs Python SDK
- **Features**:
  - Audio generation and caching
  - Redis integration for scalability
  - Streaming response support
  - Voice customization

**API Endpoints**:
- `POST /api/assistant/tts` - Generate TTS audio
- `GET /api/assistant/tts/stream/{response_id}` - Stream cached audio

### 5. Enhanced AI Assistant API

**File**: `backend/Apis/ai_assistant.py`

**New Features**:
- TTS integration in responses
- Session management endpoints
- Audio URL generation
- Step tracking

**Updated Endpoints**:
- `POST /ai/start_session` - Start cooking session with wake word instructions
- `POST /ai/ask` - Returns text + audio URL
- `POST /ai/upload_audio` - Voice input processing with TTS response
- `GET /ai/sessions` - List active sessions
- `PUT /ai/sessions/{session_id}/step` - Update current step
- `DELETE /ai/sessions/{session_id}` - End session

## 🚀 Voice-First Workflow

### 1. Session Start
```
User clicks "Begin Session" → 
Backend creates session → 
Frontend initializes wake word detection → 
Starts listening for "Hey Cheffy"
```

### 2. Wake Word Detection
```
User says "Hey Cheffy" → 
Porcupine detects wake word → 
Stops wake word listening → 
Starts voice recording for user input
```

### 3. Voice Processing
```
User speaks question → 
Recording stops → 
Audio sent to backend → 
Whisper transcribes → 
AI generates response → 
ElevenLabs creates TTS → 
Audio streamed back to frontend
```

### 4. Response Playback
```
Frontend receives audio URL → 
TTS service plays streaming audio → 
User hears Cheffy's response → 
Resumes wake word listening
```

## 📱 UI/UX Design

### Status Indicators
- **👂 Listening**: Wake word detection active
- **🎤 Recording**: Voice input being captured
- **🤔 Thinking**: AI processing request
- **🗣️ Speaking**: TTS audio playing
- **❌ Error**: Something went wrong

### Voice-First Interface
- Minimal UI focused on voice interaction
- Clear status feedback
- Text input as fallback
- Kitchen-friendly touch targets

## 🔧 Configuration

### Environment Variables

**Frontend** (`.env.local`):
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_PICOVOICE_ACCESS_KEY=your_picovoice_key
```

**Backend** (`.env`):
```bash
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
REDIS_URL=redis://localhost:6379
```

### Dependencies

**Frontend**:
```json
{
  "@picovoice/porcupine-web": "^3.0.2",
  "@picovoice/web-voice-processor": "^3.0.2"
}
```

**Backend**:
```txt
elevenlabs==0.3.0
redis==5.0.1
```

## 🎯 Cost Optimization

### Wake Word Detection
- **Local Processing**: No API calls for wake word detection
- **Selective Activation**: Only activates STT after wake word
- **Idle Cost Prevention**: No continuous microphone streaming

### TTS Caching
- **Response Caching**: Audio responses cached in Redis
- **Streaming URLs**: Efficient audio delivery
- **Batch Processing**: Multiple requests handled efficiently

### Session Management
- **Automatic Cleanup**: Inactive sessions cleaned up
- **Resource Management**: Proper cleanup of audio streams
- **Memory Optimization**: Efficient state management

## 🔄 Session Lifecycle

1. **Initialize**: Services start, wake word detection begins
2. **Active**: User can interact via voice or text
3. **Processing**: AI generates responses with TTS
4. **Cleanup**: Resources released, session ended

## 🚀 Future Enhancements

### Mobile Support
- React Native compatibility
- Native wake word detection
- Offline capabilities

### Advanced Features
- Multi-language support
- Custom voice training
- Recipe step automation
- Smart kitchen integration

### Scalability
- Microservices architecture
- Load balancing
- CDN for audio delivery
- Real-time collaboration

## 🐛 Troubleshooting

### Wake Word Issues
- Check microphone permissions
- Verify Picovoice access key
- Test in quiet environment

### TTS Problems
- Verify ElevenLabs API key
- Check audio playback permissions
- Monitor network connectivity

### Session Errors
- Check authentication
- Verify recipe access
- Monitor database connectivity

## 📊 Performance Metrics

- **Wake Word Latency**: < 500ms
- **TTS Generation**: < 2s
- **Audio Streaming**: < 100ms latency
- **Session Response**: < 3s total

## 🔒 Security Considerations

- **API Key Management**: Secure environment variables
- **Audio Privacy**: Local processing where possible
- **Session Isolation**: User-specific sessions
- **Content Moderation**: OpenAI moderation API

---

This architecture provides a solid foundation for a production-ready voice-first cooking assistant that scales efficiently while maintaining cost-effectiveness and user experience.
