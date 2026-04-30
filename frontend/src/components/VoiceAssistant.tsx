import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Mic, Square, Loader2, X, Volume2, Upload, Send, MessageSquare } from 'lucide-react';
import { confirmAction, API_BASE_URL, sendTextMessage, type ActionOption } from '../lib/api';
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
  const [isOpen, setIsOpen] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [metadata, setMetadata] = useState<Partial<AudioChunk> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState('');
  const [customActionInput, setCustomActionInput] = useState('');
  const [isConfirmingAction, setIsConfirmingAction] = useState(false);
  const [chatInput, setChatInput] = useState('');

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioQueueRef = useRef<string[]>([]);
  const isPlayingRef = useRef(false);
  const synthRef = useRef<SpeechSynthesis | null>(window.speechSynthesis);

  const speakHindi = (text: string) => {
    if (!synthRef.current) return;
    
    // Clear any pending speech
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Explicitly find a Hindi voice if available
    const voices = synthRef.current.getVoices();
    const hindiVoice = voices.find(v => v.lang.includes('hi-IN') || v.lang.includes('hi_IN'));
    
    if (hindiVoice) {
      utterance.voice = hindiVoice;
    }
    
    utterance.lang = 'hi-IN';
    utterance.rate = 0.85;
    utterance.pitch = 1.0;
    
    synthRef.current.speak(utterance);
    console.log('Speaking Hindi safety warning...');
  };

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
      const audio = new Audio(`data:audio/wav;base64,${nextChunk}`);
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

      const response = await fetch(`${API_BASE_URL}/orchestration/voice-route-stream`, {
        method: 'POST',
        body: formData,
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      let finalTranscript = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data: any = JSON.parse(line);
            if (data.type === 'metadata') {
              // Map full_message to message for consistency
              const mappedData = {
                ...data,
                message: data.full_message || data.message
              };
              setMetadata(mappedData);
              finalTranscript = data.transcript || '';
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
      
      // Trigger Hindi warning if the transcript mentions Aspirin/Fever
      const transcriptLower = finalTranscript.toLowerCase();
      if ((transcriptLower.includes('aspirin') || transcriptLower.includes('asprin')) && 
          (transcriptLower.includes('fever') || transcriptLower.includes('बुखार'))) {
        speakHindi('सावधान: एस्पिरिन (Aspirin) आपकी मिर्गी (Epilepsy) की दवाओं के साथ समस्या पैदा कर सकती है।');
      }
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
      if (metadata.action_id === -999) {
        const actionResult =
          selectedOption === 'email_shaun'
            ? 'Drafted an email to Dr. Shaun with risks + context. (Demo successfully routed!)'
            : selectedOption === 'asana_task'
              ? 'Created an Asana review task for Dr. Shaun. (Demo successfully escalated!)'
              : 'Started a doctor chat thread. (Demo successfully connected!)';
        setStatus('Action confirmed');
        setMetadata((prev) => ({ ...(prev || {}), full_message: actionResult, options: [] }));
        setCustomActionInput('');
        return;
      }
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

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const query = chatInput.trim();
    if (!query) return;

    setError(null);
    setMetadata(null);
    setIsProcessing(true);
    setStatus('Thinking...');

    try {
      const result = await sendTextMessage(patientId, query);
      
      setMetadata({
        type: 'metadata',
        transcript: query,
        message: result.message,
        route_type: result.route_type,
        primary_model: result.primary_model,
        action_id: result.action_id,
        options: result.options,
        allow_custom_input: result.allow_custom_input,
      });

      setStatus('Response received');

      // Special check: If the real LLM mentions Aspirin and Fever, still trigger the Hindi safety warning
      const lowerQuery = query.toLowerCase();
      const mentionsAspirin = lowerQuery.includes('aspirin') || lowerQuery.includes('asprin') || lowerQuery.includes('एस्पिरिन');
      const mentionsFever = lowerQuery.includes('fever') || lowerQuery.includes('बुखार');
      
      if (mentionsAspirin && mentionsFever) {
        speakHindi('सावधान: एस्पिरिन (Aspirin) आपकी मिर्गी (Epilepsy) की दवाओं के साथ समस्या पैदा कर सकती है। क्या मैं आपकी मदद डॉक्टर को अपडेट करने में कर सकता हूँ?');
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat failed');
    } finally {
      setIsProcessing(false);
      setChatInput('');
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col items-end gap-4">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="w-[450px] flex min-h-[500px] flex-col overflow-hidden rounded-[1.75rem] border border-white/10 bg-surface/95 shadow-[0_24px_54px_-12px_rgba(27,28,21,0.25)] backdrop-blur-2xl"
          >
            <div className="flex items-center justify-between border-b border-white/5 bg-surface-container-lowest/30 p-5">
              <h2 className="font-serif text-[1.2rem] font-bold text-primary">CureQuest Agent</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-full bg-white/5 p-2 text-on-surface/50 transition-colors hover:bg-white/10 hover:text-on-surface"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-5">
              {metadata || error ? (
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    {metadata ? (
                      <Pill tone={metadata.route_type === 'medical_text' ? 'terracotta' : 'sage'}>
                        {metadata.primary_model?.split('/')[1] || metadata.primary_model}
                      </Pill>
                    ) : (
                      <Pill tone="terracotta">Error</Pill>
                    )}
                  </div>

                  <div className="flex items-start gap-3 rounded-2xl bg-surface-container-lowest/50 p-4 text-[1rem] text-on-surface/80">
                    {!error ? <Volume2 className="mt-1 h-5 w-5 shrink-0 text-primary" /> : null}
                    <div className="flex flex-col">
                      <p className="mb-1 font-bold text-[0.8rem] uppercase tracking-wider text-primary/60">{status || (error ? 'Error' : 'Voice Assistant')}</p>
                      <p className="leading-relaxed">{error || metadata?.message || 'Processing voice...'}</p>
                    </div>
                  </div>

                  {metadata?.action_id && metadata.options && metadata.options.length > 0 && (
                    <div className="rounded-2xl border border-outline-variant/20 bg-surface-container-lowest p-4">
                      <p className="mb-3 text-[0.8rem] font-semibold uppercase tracking-wide text-on-surface/50">Confirm Action</p>
                      <div className="flex flex-wrap gap-2">
                        {metadata.options.map((option) => (
                          <button
                            key={`voice-${metadata.action_id}-${option.value}`}
                            onClick={() => handleConfirmVoiceAction(option.value)}
                            disabled={isConfirmingAction}
                            className="rounded-xl bg-primary-container px-4 py-2.5 text-left text-[0.9rem] text-on-primary-container transition-colors hover:bg-primary/20 disabled:opacity-60"
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                      {metadata.allow_custom_input && (
                        <div className="mt-4 flex items-center gap-2">
                          <input
                            type="text"
                            value={customActionInput}
                            onChange={(e) => setCustomActionInput(e.target.value)}
                            placeholder="Type a custom instruction..."
                            className="input-shell h-11 flex-1 text-[0.95rem]"
                          />
                          <button
                            onClick={() => handleConfirmVoiceAction(undefined, true)}
                            disabled={isConfirmingAction}
                            className="rounded-xl bg-secondary-container px-4 py-2.5 text-[0.9rem] font-medium text-on-secondary-container transition-colors hover:bg-secondary/20 disabled:opacity-60"
                          >
                            {isConfirmingAction ? 'Sending...' : 'Send'}
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex h-full flex-col items-center justify-center space-y-4 text-center opacity-50">
                  <MessageSquare className="h-12 w-12 text-primary" />
                  <p className="font-serif text-lg">How can I help you today?</p>
                  <p className="text-sm">Speak, chat, or upload a document.</p>
                </div>
              )}
            </div>

            {/* Bottom Bar: Upload, Chat, Voice */}
            <div className="border-t border-white/5 bg-surface-container-lowest/30 p-4">
              <form onSubmit={handleChatSubmit} className="flex items-center gap-2 rounded-2xl bg-surface-container-lowest p-2 shadow-inner">
                <button type="button" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-on-surface/50 transition-colors hover:bg-white/5 hover:text-primary">
                  <Upload className="h-5 w-5" />
                </button>
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask CureQuest Agent..."
                  className="h-10 flex-1 bg-transparent px-2 text-[0.95rem] text-on-surface outline-none placeholder:text-on-surface/30"
                />
                {chatInput.trim() ? (
                  <button type="submit" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-container text-primary transition-colors hover:bg-primary/20">
                    <Send className="h-5 w-5" />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={isProcessing}
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-all ${isProcessing ? 'bg-surface-container-high text-on-surface/50' :
                        isRecording ? 'bg-terracotta text-white animate-pulse' : 'bg-primary-container text-primary hover:bg-primary/20'
                      }`}
                  >
                    {isProcessing ? <Loader2 className="h-5 w-5 animate-spin" /> :
                      isRecording ? <Square className="h-5 w-5 fill-current" /> : <Mic className="h-5 w-5" />}
                  </button>
                )}
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="relative flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary-container text-white shadow-xl transition-all duration-300 hover:scale-105"
        >
          <MessageSquare className="h-7 w-7" />
        </button>
      )}
    </div>
  );
};
