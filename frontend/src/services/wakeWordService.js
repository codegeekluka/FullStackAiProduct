import { Porcupine } from "@picovoice/porcupine-web";
import { WebVoiceProcessor } from "@picovoice/web-voice-processor";

class WakeWordService {
  constructor(accessKey, onDetection, onError) {
    this.accessKey = accessKey;
    this.onDetection = onDetection;
    this.onError = onError;
    this.porcupine = null;
    this.voiceProcessor = null;
  }

  async initialize() {
    try {
      console.log("WakeWordService: Starting initialization...");
      
      // Load your custom Hey Cheffy model
      console.log("WakeWordService: Loading custom model...");
      const ppnBase64 = await this.loadPpnAsBase64(
        "/models/Hey-Cheffy_en_wasm_v3_0_0.ppn"
      );
      
      console.log("WakeWordService: Model loaded, base64 length:", ppnBase64.length);
      console.log("WakeWordService: Access key available:", !!this.accessKey);

      const keywords = [
        {
          base64: ppnBase64, // 👈 custom wake word as base64
          label: "Hey Cheffy",
          sensitivity: 0.65,
        },
      ];
      
      console.log("WakeWordService: Keywords array:", keywords);

      this.porcupine = await Porcupine.create({
        accessKey: this.accessKey,
        keywords: keywords,
        processErrorCallback: (error) => {
          if (this.onError) this.onError(error);
        },
      });

      this.voiceProcessor = new WebVoiceProcessor(this.porcupine);
      this.voiceProcessor.addListener(() => {
        if (this.onDetection) this.onDetection("Hey Cheffy");
      });
      
      console.log("WakeWordService: Initialization completed successfully");
    } catch (error) {
      console.error("WakeWordService: Initialization failed:", error);
      throw error;
    }
  }

  async loadPpnAsBase64(url) {
    try {
      console.log("WakeWordService: Fetching model from:", url);
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch model: ${response.status} ${response.statusText}`);
      }
      
      console.log("WakeWordService: Model fetch successful, converting to base64...");
      const arrayBuffer = await response.arrayBuffer();
      const bytes = new Uint8Array(arrayBuffer);
      let binary = "";
      bytes.forEach((b) => (binary += String.fromCharCode(b)));
      const base64 = btoa(binary);
      
      console.log("WakeWordService: Model converted to base64, length:", base64.length);
      return base64;
    } catch (error) {
      console.error("WakeWordService: Failed to load model:", error);
      throw error;
    }
  }

  async start() {
    if (this.voiceProcessor) {
      await this.voiceProcessor.start();
      console.log("WakeWordService: Listening for 'Hey Cheffy'...");
    }
  }

  async stop() {
    if (this.voiceProcessor) {
      await this.voiceProcessor.stop();
      console.log("WakeWordService: Stopped listening");
    }
  }

  async release() {
    if (this.voiceProcessor) await this.voiceProcessor.release();
    if (this.porcupine) await this.porcupine.release();
    this.porcupine = null;
    this.voiceProcessor = null;
    console.log("WakeWordService: Released resources");
  }
}

export default WakeWordService;
