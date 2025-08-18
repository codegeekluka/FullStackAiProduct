import { create } from 'zustand';
import axios from 'axios';
import wakeWordService from '../services/wakeWordService';
import ttsService from '../services/ttsService';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// AI Assistant Store using Zustand
const useAIAssistantStore = create((set, get) => ({
  // State
  sessionId: null,
  currentRecipe: null,
  messages: [],
  isRecording: false,
  isLoading: false,
  error: null,
  currentStep: 0,
  
  // Voice-first state
  isWakeWordListening: false,
  isVoiceActive: false,
  isTTSPlaying: false,
  sessionStatus: 'idle', // 'idle', 'listening', 'thinking', 'speaking', 'error'
  
  // Initialize services
  initializeServices: async () => {
    try {
      // Initialize TTS service
      await ttsService.initialize();
      
      // Initialize wake word service (will fail gracefully if not available)
      const wakeWordInitialized = await wakeWordService.initialize(
        () => get().onWakeWordDetected(),
        (error) => get().onWakeWordError(error)
      );
      
      if (wakeWordInitialized) {
        console.log('AI Assistant services initialized successfully');
      } else {
        console.log('AI Assistant initialized with limited functionality (wake word detection disabled)');
      }
    } catch (error) {
      console.error('Failed to initialize AI Assistant services:', error);
      set({ error: 'Failed to initialize voice services' });
    }
  },

  // Wake word detection handlers
  onWakeWordDetected: () => {
    console.log('Wake word "Hey Cheffy" detected!');
    set({ 
      isVoiceActive: true, 
      sessionStatus: 'listening',
      isWakeWordListening: false 
    });
    
    // Start recording for user input
    get().startVoiceRecording();
  },

  onWakeWordError: (error) => {
    console.error('Wake word detection error:', error);
    set({ 
      error: 'Wake word detection failed',
      sessionStatus: 'error',
      isWakeWordListening: false 
    });
  },

  // Session management
  startSession: async (recipeId) => {
    try {
      set({ isLoading: true, error: null });

      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/ai/start_session`,
        { recipe_id: recipeId },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const { session_id, recipe_title } = response.data;

      set((state) => ({
        sessionId: session_id,
        currentRecipe: { id: recipeId, title: recipe_title },
        messages: [],
        currentStep: 0,
        sessionStatus: 'listening',
        isLoading: false
      }));

      // Start listening for wake word
      await get().startWakeWordListening();

      return { session_id, recipe_title };
    } catch (error) {
      console.error('Error starting session:', error);
      set({
        error: error.response?.data?.detail || 'Failed to start cooking session',
        isLoading: false,
        sessionStatus: 'error'
      });
      throw error;
    }
  },

  // Check for existing active session
  checkExistingSession: async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_BASE_URL}/ai/sessions`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      const sessions = response.data;
      return sessions.length > 0 ? sessions[0] : null; // Return first active session
    } catch (error) {
      console.error('Error checking existing session:', error);
      return null;
    }
  },

  endSession: async () => {
    try {
      const { sessionId } = get();
      if (sessionId) {
        const token = localStorage.getItem('token');
        await axios.delete(
          `${API_BASE_URL}/ai/sessions/${sessionId}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );
      }
    } catch (error) {
      console.error('Error ending session:', error);
    } finally {
      // Stop all voice services
      await get().stopWakeWordListening();
      await get().stopVoiceRecording();
      ttsService.stop();
      
      set({
        sessionId: null,
        currentRecipe: null,
        messages: [],
        isRecording: false,
        isWakeWordListening: false,
        isVoiceActive: false,
        isTTSPlaying: false,
        sessionStatus: 'idle',
        currentStep: 0,
        error: null
      });
    }
  },

  // Wake word listening
  startWakeWordListening: async () => {
    try {
      const success = await wakeWordService.startListening();
      if (success) {
        set({ 
          isWakeWordListening: true,
          sessionStatus: 'listening'
        });
        console.log('Started listening for "Hey Cheffy"');
      }
    } catch (error) {
      console.error('Failed to start wake word listening:', error);
      set({ error: 'Failed to start voice detection' });
    }
  },

  stopWakeWordListening: async () => {
    try {
      await wakeWordService.stopListening();
      set({ 
        isWakeWordListening: false,
        sessionStatus: 'idle'
      });
    } catch (error) {
      console.error('Failed to stop wake word listening:', error);
    }
  },

  // Voice recording (after wake word detection)
  startVoiceRecording: async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        try {
          await get().processVoiceInput(audioBlob);
        } catch (error) {
          console.error('Failed to process voice input:', error);
        }
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      set({ 
        isRecording: true,
        sessionStatus: 'listening'
      });
      
      // Store recorder reference
      get().currentRecorder = recorder;
    } catch (error) {
      console.error('Failed to start voice recording:', error);
      set({ 
        error: 'Failed to access microphone',
        sessionStatus: 'error'
      });
    }
  },

  stopVoiceRecording: () => {
    const { currentRecorder } = get();
    if (currentRecorder && currentRecorder.state !== 'inactive') {
      currentRecorder.stop();
    }
    set({ 
      isRecording: false,
      sessionStatus: 'thinking'
    });
  },

  // Process voice input
  processVoiceInput: async (audioBlob) => {
    try {
      set({ isLoading: true, sessionStatus: 'thinking' });

      const { sessionId } = get();
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('audio_file', audioBlob, 'recording.wav');

      const response = await axios.post(
        `${API_BASE_URL}/ai/upload_audio`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      const { transcribed_text, response: aiResponse, audio_url, current_step } = response.data;

      // Add messages to chat
      const userMessage = {
        role: 'user',
        text: transcribed_text,
        timestamp: new Date().toISOString(),
        isVoice: true
      };

      const assistantMessage = {
        role: 'assistant',
        text: aiResponse,
        timestamp: new Date().toISOString(),
        audioUrl: audio_url
      };

      set((state) => ({
        messages: [...state.messages, userMessage, assistantMessage],
        currentStep: current_step,
        isLoading: false,
        sessionStatus: 'speaking'
      }));

      // Play TTS response
      if (audio_url) {
        console.log('AI Assistant - Playing TTS audio:', audio_url);
        set({ isTTSPlaying: true });
        try {
          await ttsService.playAudioStream(audio_url);
          console.log('AI Assistant - TTS audio playback completed');
        } catch (error) {
          console.error('AI Assistant - TTS playback failed:', error);
        }
        set({ isTTSPlaying: false });
      } else {
        console.log('AI Assistant - No audio URL provided for TTS');
      }

      // Resume wake word listening after response
      setTimeout(() => {
        get().startWakeWordListening();
      }, 1000);

      return { transcribed_text, aiResponse };
    } catch (error) {
      console.error('Error processing voice input:', error);
      set({
        error: error.response?.data?.detail || 'Failed to process voice input',
        isLoading: false,
        sessionStatus: 'error'
      });
      throw error;
    }
  },

  // Text message handling (fallback)
  sendMessage: async (message, queryType = null) => {
    try {
      const { sessionId } = get();
      if (!sessionId) {
        throw new Error('No active session. Please start cooking with a recipe first.');
      }

      set({ isLoading: true, error: null, sessionStatus: 'thinking' });

      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_BASE_URL}/ai/ask`,
        {
          session_id: sessionId,
          message: message,
          query_type: queryType
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const { response: aiResponse, audio_url, current_step } = response.data;

      const userMessage = {
        role: 'user',
        text: message,
        timestamp: new Date().toISOString()
      };

      const assistantMessage = {
        role: 'assistant',
        text: aiResponse,
        timestamp: new Date().toISOString(),
        audioUrl: audio_url
      };

      set((state) => ({
        messages: [...state.messages, userMessage, assistantMessage],
        currentStep: current_step,
        isLoading: false,
        sessionStatus: 'speaking'
      }));

      // Play TTS response
      if (audio_url) {
        console.log('AI Assistant - Playing TTS audio (text):', audio_url);
        set({ isTTSPlaying: true });
        try {
          await ttsService.playAudioStream(audio_url);
          console.log('AI Assistant - TTS audio playback completed (text)');
        } catch (error) {
          console.error('AI Assistant - TTS playback failed (text):', error);
        }
        set({ isTTSPlaying: false });
      } else {
        console.log('AI Assistant - No audio URL provided for TTS (text)');
      }

      return aiResponse;
    } catch (error) {
      console.error('Error sending message:', error);
      set({
        error: error.response?.data?.detail || 'Failed to send message',
        isLoading: false,
        sessionStatus: 'error'
      });
      throw error;
    }
  },

  // Legacy audio message method (for backward compatibility)
  sendAudioMessage: async (audioBlob) => {
    return get().processVoiceInput(audioBlob);
  },

  // Step management
  updateCurrentStep: async (step) => {
    try {
      const { sessionId } = get();
      if (!sessionId) return;

      const token = localStorage.getItem('token');
      await axios.put(
        `${API_BASE_URL}/ai/sessions/${sessionId}/step`,
        { step },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      set({ currentStep: step });
    } catch (error) {
      console.error('Error updating step:', error);
    }
  },

  // Utility methods
  setIsRecording: (isRecording) => set({ isRecording }),
  clearError: () => set({ error: null }),
  
  // Get session status
  getSessionStatus: () => {
    const state = get();
    return {
      isActive: !!state.sessionId,
      isListening: state.isWakeWordListening,
      isVoiceActive: state.isVoiceActive,
      isTTSPlaying: state.isTTSPlaying,
      sessionStatus: state.sessionStatus
    };
  },

  // Cleanup on unmount
  cleanup: async () => {
    await get().endSession();
    await wakeWordService.release();
  }
}));

export default useAIAssistantStore;
