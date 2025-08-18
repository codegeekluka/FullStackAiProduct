// Try to import Porcupine, but don't fail if not available
let Porcupine, WebVoiceProcessor;
let PICOVOICE_AVAILABLE = false;

try {
  const picovoice = require('@picovoice/porcupine-web');
  Porcupine = picovoice.Porcupine;
  WebVoiceProcessor = picovoice.WebVoiceProcessor;
  PICOVOICE_AVAILABLE = true;
} catch (error) {
  console.log('Picovoice not available. Wake word detection will be disabled.');
  PICOVOICE_AVAILABLE = false;
}

class WakeWordService {
  constructor() {
    this.porcupine = null;
    this.voiceProcessor = null;
    this.isListening = false;
    this.onWakeWordDetected = null;
    this.onError = null;
    this.isAvailable = PICOVOICE_AVAILABLE;
  }

  async initialize(onWakeWordDetected, onError) {
    if (!this.isAvailable) {
      console.log('Wake word service not available. Picovoice not installed or API key missing.');
      return false;
    }

    try {
      this.onWakeWordDetected = onWakeWordDetected;
      this.onError = onError;

      const accessKey = process.env.VITE_PICOVOICE_ACCESS_KEY;
      if (!accessKey) {
        console.log('VITE_PICOVOICE_ACCESS_KEY not found. Wake word detection will be disabled.');
        this.isAvailable = false;
        return false;
      }

      // Initialize Porcupine with "Hey Cheffy" wake word
      // Note: In production, you'd need to create a custom wake word model
      // For now, we'll use a placeholder - you'll need to replace with actual model
      this.porcupine = await Porcupine.create({
        accessKey: accessKey,
        keywords: ['hey cheffy'], // Custom wake word model
        processErrorCallback: (error) => {
          console.error('Porcupine error:', error);
          if (this.onError) this.onError(error);
        }
      });

      // Initialize voice processor
      this.voiceProcessor = new WebVoiceProcessor(this.porcupine, {
        processErrorCallback: (error) => {
          console.error('Voice processor error:', error);
          if (this.onError) this.onError(error);
        }
      });

      // Set up wake word detection callback
      this.porcupine.addListener((keywordIndex) => {
        console.log('Wake word detected!');
        if (this.onWakeWordDetected) {
          this.onWakeWordDetected();
        }
      });

      console.log('Wake word service initialized successfully');
      return true;
    } catch (error) {
      console.error('Failed to initialize wake word service:', error);
      this.isAvailable = false;
      if (this.onError) this.onError(error);
      return false;
    }
  }

  async startListening() {
    if (!this.isAvailable || !this.voiceProcessor || this.isListening) {
      return false;
    }

    try {
      await this.voiceProcessor.start();
      this.isListening = true;
      console.log('Started listening for wake word');
      return true;
    } catch (error) {
      console.error('Failed to start listening:', error);
      if (this.onError) this.onError(error);
      return false;
    }
  }

  async stopListening() {
    if (!this.voiceProcessor || !this.isListening) {
      return false;
    }

    try {
      await this.voiceProcessor.stop();
      this.isListening = false;
      console.log('Stopped listening for wake word');
      return true;
    } catch (error) {
      console.error('Failed to stop listening:', error);
      if (this.onError) this.onError(error);
      return false;
    }
  }

  async release() {
    try {
      if (this.voiceProcessor) {
        await this.voiceProcessor.release();
      }
      if (this.porcupine) {
        await this.porcupine.release();
      }
      this.isListening = false;
      console.log('Wake word service released');
    } catch (error) {
      console.error('Error releasing wake word service:', error);
    }
  }

  getStatus() {
    return {
      isAvailable: this.isAvailable,
      isInitialized: !!this.porcupine,
      isListening: this.isListening
    };
  }
}

// Create singleton instance
const wakeWordService = new WakeWordService();
export default wakeWordService;
