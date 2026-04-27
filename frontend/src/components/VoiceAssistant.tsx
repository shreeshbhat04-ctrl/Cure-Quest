import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Mic, Square, Loader2, X, Volume2 } from 'lucide-react';
import { confirmAction, type ActionOption } from '../lib/api';
import { Pill } from './ui';

interface VoiceAssistantProps {
  patientId: number;
}

interface AudioChunk {
  type: 'metadata' | 'audio' | 'error';
  chunk?: string;
  transcript?: string;
  full_message?: string;
  route_type?: string;
  primary_model?: string;
  action_id?: number;
  options?: ActionOption[];
  allow_custom_input?: boolean;
  message?: string;
}

export const VoiceAssistant: React.FC<VoiceAssistantProps> = ({ patientId }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [metadata, setMetadata] = useState<Partial<AudioChunk> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState('');
  const [customActionInput, setCustomActionInput] = useState('');
  const [isConfirmingAction, setIsConfirmingAction] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioQueueRef = useRef<string[]>([]);
  const isPlayingRef = useRef(false);

  const startRecording = async () => {
    try {
      setError(null);
      setMetadata(null);
      setStatus('');
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
        stream.getTracks().forEach((track) => track.stop());
        await handleStreamingAudioUpload(audioBlob);
      };

      mediaRecorder.start(100);
      setIsRecording(true);
    } catch (err) {
      setError('Cannot access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const playNextInQueue = () => {
    if (audioQueueRef.current.length === 0) {
      isPlayingRef.current = false;
      return;
    }

    isPlayingRef.current = true;
    const nextChunk = audioQueueRef.current.shift();
    if (nextChunk) {
      const audio = new Audio(`data:audio/mp3;base64,${nextChunk}`);
      audio.onended = () => {
        playNextInQueue();
      };
      audio.play().catch(err => {
        console.error('Playback failed:', err);
        playNextInQueue();
      });
    }
  };

  const handleStreamingAudioUpload = async (blob: Blob) => {
    setIsProcessing(true);
    audioQueueRef.current = [];
    isPlayingRef.current = false;

    try {
      const formData = new FormData();
      formData.append('audio', blob);
      formData.append('patient_id', patientId.toString());

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/orchestration/voice-route-stream`, {
        method: 'POST',
        body: formData,
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data: AudioChunk = JSON.parse(line);
            if (data.type === 'metadata') {
              setMetadata(data);
              setStatus('Response incoming...');
            } else if (data.type === 'audio' && data.chunk) {
              audioQueueRef.current.push(data.chunk);
              if (!isPlayingRef.current) {
                playNextInQueue();
              }
            } else if (data.type === 'error') {
              setError(data.message || 'Unknown error');
            }
          } catch (e) {
            console.error('Failed to parse chunk:', e);
          }
        }
      }
      setStatus('Response complete');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Streaming failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleConfirmVoiceAction = async (selectedOption?: string, useCustom: boolean = false) => {
    if (!metadata?.action_id || isConfirmingAction) return;
    const customInput = customActionInput.trim();
    if (useCustom && !customInput) return;

    setIsConfirmingAction(true);
    try {
      const result = await confirmAction(
        metadata.action_id,
        selectedOption,
        useCustom ? customInput : undefined,
      );
      const resultMessage = (result.result?.message as string | undefined) || `Action ${result.status}.`;
      setStatus('Action confirmed');
      setMetadata((prev) => ({ ...(prev || {}), full_message: resultMessage, options: [] }));
      setCustomActionInput('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to confirm action');
    } finally {
      setIsConfirmingAction(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col items-end gap-4">
      <AnimatePresence>
        {(metadata || error) && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="w-full max-w-[340px] rounded-[1.75rem] border border-white/10 bg-surface/90 p-5 shadow-[0_24px_54px_-12px_rgba(27,28,21,0.25)] backdrop-blur-2xl"
          >
            <div className="mb-3 flex items-start justify-between">
              {metadata ? (
                <Pill tone={metadata.route_type === 'medical_text' ? 'terracotta' : 'sage'}>
                  {metadata.primary_model?.split('/')[1] || metadata.primary_model}
                </Pill>
              ) : (
                <Pill tone="terracotta">Error</Pill>
              )}
              <button
                onClick={() => { setMetadata(null); setError(null); }}
                className="rounded-full bg-white/10 p-1.5 text-on-surface/50 transition-colors hover:text-on-surface"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            
            <div className="flex items-center gap-2 text-[0.95rem] text-on-surface/80">
              {!error ? <Volume2 className="h-4 w-4 text-primary" /> : null}
              <div className="flex flex-col">
                 <p className="font-bold text-[0.75rem] uppercase tracking-wider text-primary/60 mb-1">{status || (error ? 'Error' : 'Voice Assistant')}</p>
                 <p className="leading-7">{error || metadata?.full_message || 'Processing voice...'}</p>
              </div>
            </div>

            {metadata?.action_id && metadata.options && metadata.options.length > 0 && (
              <div className="mt-3 rounded-2xl border border-outline-variant/20 bg-surface-container-lowest p-3">
                <p className="mb-2 text-[0.72rem] font-semibold uppercase tracking-wide text-on-surface/50">Confirm Action</p>
                <div className="flex flex-wrap gap-2">
                  {metadata.options.map((option) => (
                    <button
                      key={`voice-${metadata.action_id}-${option.value}`}
                      onClick={() => handleConfirmVoiceAction(option.value)}
                      disabled={isConfirmingAction}
                      className="rounded-xl bg-primary-container px-3 py-2 text-left text-[0.82rem] text-on-primary-container disabled:opacity-60"
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
                {metadata.allow_custom_input && (
                  <div className="mt-3 flex items-center gap-2">
                    <input
                      type="text"
                      value={customActionInput}
                      onChange={(e) => setCustomActionInput(e.target.value)}
                      placeholder="Custom input"
                      className="input-shell h-10 flex-1"
                    />
                    <button
                      onClick={() => handleConfirmVoiceAction(undefined, true)}
                      disabled={isConfirmingAction}
                      className="rounded-xl bg-secondary-container px-3 py-2 text-[0.8rem] text-on-secondary-container disabled:opacity-60"
                    >
                      {isConfirmingAction ? 'Sending...' : 'Send'}
                    </button>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="relative">
        {isRecording && <span className="absolute -inset-2 animate-pulse rounded-full bg-terracotta-fixed/30" />}
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`relative flex h-16 w-16 items-center justify-center rounded-full text-white shadow-xl transition-all duration-300 ${
            isProcessing ? 'bg-surface-container-high text-on-surface/50' :
            isRecording ? 'bg-terracotta scale-105' : 'bg-gradient-to-br from-primary to-primary-container hover:scale-105'
          }`}
        >
          {isProcessing ? <Loader2 className="h-6 w-6 animate-spin text-primary" /> :
           isRecording ? <Square className="h-6 w-6 fill-current" /> : <Mic className="h-7 w-7" />}
        </button>
      </div>
    </div>
  );
};
