import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Mic, Square, Loader2, X, Volume2 } from 'lucide-react';
import { sendVoiceNote, type ConversationResponse } from '../lib/api';
import { Pill } from './ui';

interface VoiceAssistantProps {
  patientId: number;
}

export const VoiceAssistant: React.FC<VoiceAssistantProps> = ({ patientId }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [aiResponse, setAiResponse] = useState<ConversationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const getVoiceStatus = () => {
    if (error) return 'Voice request failed';
    if (!aiResponse) return '';
    if (aiResponse.audio_base64) return 'Response spoken aloud';
    return 'Voice response ready';
  };

  const startRecording = async () => {
    try {
      setError(null);
      setAiResponse(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        // Stop all audio tracks
        stream.getTracks().forEach((track) => track.stop());
        
        await handleAudioUpload(audioBlob);
      };

      mediaRecorder.start(100); // Record in 100ms chunks
      setIsRecording(true);
    } catch (err) {
      console.error('Microphone access error:', err);
      setError('Cannot access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleAudioUpload = async (blob: Blob) => {
    try {
      setIsProcessing(true);
      const result = await sendVoiceNote(patientId, blob);
      setAiResponse(result);
      
      // Auto-play the TTS response if returned
      if (result.audio_base64) {
        const audio = new Audio(`data:audio/mp3;base64,${result.audio_base64}`);
        audio.play().catch(err => console.error('Audio playback failed:', err));
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Voice transcription failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col items-end gap-4">
      {/* Response Toast */}
      <AnimatePresence>
        {(aiResponse || error) && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="w-full max-w-[340px] rounded-[1.75rem] border border-white/10 bg-surface/90 p-5 shadow-[0_24px_54px_-12px_rgba(27,28,21,0.25)] backdrop-blur-2xl"
          >
            <div className="mb-3 flex items-start justify-between">
              {aiResponse ? (
                <div>
                  <Pill tone={aiResponse.route_type === 'medical_text' ? 'terracotta' : 'sage'}>
                    {aiResponse.primary_model.split('/')[1] || aiResponse.primary_model}
                  </Pill>
                </div>
              ) : (
                <Pill tone="terracotta">Error</Pill>
              )}
              <button
                onClick={() => { setAiResponse(null); setError(null); }}
                className="rounded-full bg-white/10 p-1.5 text-on-surface/50 transition-colors hover:text-on-surface"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            
            <div className="flex items-center gap-2 text-[0.95rem] text-on-surface/80">
              {!error ? <Volume2 className="h-4 w-4 text-primary" /> : null}
              <p className="leading-7">{error ? error : getVoiceStatus()}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Action Button */}
      <div className="relative">
        {isRecording && (
          <span className="absolute -inset-2 animate-pulse rounded-full bg-terracotta-fixed/30" />
        )}
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`relative flex h-16 w-16 items-center justify-center rounded-full text-white shadow-xl transition-all duration-300 ${
            isProcessing
              ? 'bg-surface-container-high text-on-surface/50'
              : isRecording
              ? 'bg-terracotta scale-105'
              : 'bg-gradient-to-br from-primary to-primary-container hover:scale-105'
          }`}
        >
          {isProcessing ? (
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          ) : isRecording ? (
            <Square className="h-6 w-6 fill-current" />
          ) : (
            <Mic className="h-7 w-7" />
          )}
        </button>
      </div>
    </div>
  );
};
