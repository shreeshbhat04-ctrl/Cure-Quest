import { useRef, useState } from 'react';
import { motion } from 'motion/react';
import { CalendarDays, CheckCircle2, Loader2, MapPinned, Route, Sparkles, Stethoscope, Upload, Waves } from 'lucide-react';
import { analyzeSymptomImage, createCalendarEvent, createEscalation, fetchDietSupport, type DietSupportResponse, type WorkspacePayload } from '../lib/api';
import { EmptyState, LoadingState } from '../components/States';
import { Pill, SectionShell, SoftCard } from '../components/ui';

export function CareMazeScreen({
  workspace,
  loading,
  onRefresh,
  patientId,
}: {
  workspace: WorkspacePayload | null;
  loading: boolean;
  onRefresh: () => void;
  patientId: number;
}) {
  const [locationQuery, setLocationQuery] = useState('Koramangala Bangalore');
  const [medicationName, setMedicationName] = useState('Metformin');
  const [supportResult, setSupportResult] = useState<DietSupportResponse | null>(null);
  const [busyAction, setBusyAction] = useState<'maze' | 'calendar' | 'escalate' | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [aiResult, setAiResult] = useState<{ severity: string; confidence: number; findings: string[]; summary: string; model_used?: string } | null>(null);

  if (loading && !workspace) return <LoadingState />;
  if (!workspace) return <EmptyState title="No workspace yet" description="Create or seed a patient profile before opening the care maze." />;

  const runMaze = async () => {
    try {
      setBusyAction('maze');
      setFeedback(null);
      const result = await fetchDietSupport(patientId, medicationName, locationQuery);
      setSupportResult(result);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Unable to map the care maze right now.');
    } finally {
      setBusyAction(null);
    }
  };

  const scheduleFollowUp = async () => {
    try {
      setBusyAction('calendar');
      const result = await createCalendarEvent(patientId, 'Care Maze follow-up');
      setFeedback(result.html_link ? 'Calendar follow-up created successfully.' : 'Calendar event created.');
      await onRefresh();
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Unable to create the follow-up event.');
    } finally {
      setBusyAction(null);
    }
  };

  const createDoctorHandoff = async () => {
    try {
      setBusyAction('escalate');
      const result = await createEscalation(
        patientId,
        `Care Maze review requested for ${medicationName} around ${locationQuery}.`,
        locationQuery,
      );
      setFeedback(result.external_ticket_url ? 'Doctor handoff created and sent to Asana.' : 'Escalation case created.');
      await onRefresh();
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Unable to create the doctor handoff.');
    } finally {
      setBusyAction(null);
    }
  };

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setAiResult(null);
    if (file.type.startsWith('image/')) {
      setPreviewUrl(URL.createObjectURL(file));
    } else {
      setPreviewUrl(null);
    }
    // Call the real backend for AI analysis
    setAnalyzing(true);
    try {
      const result = await analyzeSymptomImage(patientId, file);
      setAiResult({
        severity: result.severity,
        confidence: result.confidence,
        findings: result.findings,
        summary: result.summary,
        model_used: result.model_used,
      });
    } catch (error) {
      setAiResult({
        severity: 'Inconclusive',
        confidence: 0,
        findings: [error instanceof Error ? error.message : 'Analysis failed – please try again.'],
        summary: 'The image could not be analysed at this time. Please check your connection and try again.',
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(file);
  };

  const latestCase = workspace.cases[0];

  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -18 }} className="space-y-8">
      <SectionShell
        eyebrow="Care Maze"
        title={
          <>
            Navigate the <span className="text-secondary italic">gaps</span> before they become friction.
          </>
        }
        description="This view connects nearby pharmacies, dietary support, follow-up scheduling, and doctor escalation into one route instead of scattered admin work."
      />

      <div className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        <SoftCard className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-secondary/75">Route planner</p>
              <h2 className="mt-2 font-serif text-2xl">Pharmacy and support mesh</h2>
            </div>
            <div className="rounded-full bg-secondary-container/30 p-3 text-secondary">
              <Route className="h-5 w-5" />
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm font-medium text-on-surface/60">Medication focus</span>
              <input value={medicationName} onChange={(e) => setMedicationName(e.target.value)} className="input-shell" />
            </label>
            <label className="space-y-2">
              <span className="text-sm font-medium text-on-surface/60">Pharmacy location</span>
              <input value={locationQuery} onChange={(e) => setLocationQuery(e.target.value)} className="input-shell" />
            </label>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={runMaze} className="river-stone-btn bg-gradient-to-br from-primary to-primary-container px-6 py-4 text-surface">
              {busyAction === 'maze' ? 'Asking Agent...' : 'Ask Agent to Map Route'}
            </button>
            <button onClick={scheduleFollowUp} className="river-stone-btn bg-surface-container-low px-6 py-4 text-on-surface/75 hover:bg-surface-container-high">
              {busyAction === 'calendar' ? 'Scheduling...' : 'Create follow-up'}
            </button>
            <button onClick={createDoctorHandoff} className="river-stone-btn bg-secondary-container px-6 py-4 text-on-secondary-container">
              {busyAction === 'escalate' ? 'Sending...' : 'Send doctor handoff'}
            </button>
          </div>

          {feedback ? <p className="rounded-[1.25rem] bg-surface-container-low px-4 py-3 text-sm leading-7 text-on-surface/70">{feedback}</p> : null}
        </SoftCard>

        <SoftCard className="bg-surface-container-low">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-tertiary/75">Live coordination</p>
              <h2 className="mt-2 font-serif text-2xl">Latest care handoff</h2>
            </div>
            <div className="rounded-full bg-tertiary-container/18 p-3 text-tertiary">
              <Stethoscope className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-6 space-y-4">
            {latestCase ? (
              <>
                <Pill tone="terracotta">{latestCase.status}</Pill>
                <p className="text-sm leading-7 text-on-surface/68">{latestCase.summary}</p>
                <div className="space-y-2 text-sm text-on-surface/55">
                  {latestCase.pharmacy_search_summary ? <p><span className="font-medium text-on-surface/70">Nearby pharmacies:</span> {latestCase.pharmacy_search_summary}</p> : null}
                  {latestCase.external_ticket_url ? <a href={latestCase.external_ticket_url} target="_blank" rel="noreferrer" className="block hover:text-primary">Open Asana case</a> : null}
                  {latestCase.calendar_event_url ? <a href={latestCase.calendar_event_url} target="_blank" rel="noreferrer" className="block hover:text-primary">Open follow-up in Calendar</a> : null}
                </div>
              </>
            ) : (
              <p className="text-sm leading-7 text-on-surface/60">No live handoff yet. Use the actions on the left to create one from this screen.</p>
            )}
          </div>
        </SoftCard>
      </div>

      {/* Upload Files & AI Analysis Section */}
      <SoftCard className="space-y-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-primary/75">Symptom intelligence</p>
            <h2 className="mt-2 font-serif text-2xl">Upload files & AI analysis</h2>
          </div>
          <div className="rounded-full bg-primary-fixed/45 p-3 text-primary">
            <Sparkles className="h-5 w-5" />
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Left: Upload & Preview */}
          <div className="space-y-4">
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`flex cursor-pointer flex-col items-center gap-3 rounded-[1.75rem] border-2 border-dashed px-6 py-10 transition-all duration-200 ${isDragOver
                  ? 'border-primary bg-primary-fixed/20'
                  : 'border-outline-variant/40 bg-surface-container-low hover:border-primary/40 hover:bg-surface-container-high/60'
                }`}
            >
              <Upload className={`h-8 w-8 ${isDragOver ? 'text-primary' : 'text-on-surface/35'}`} />
              <div className="text-center">
                <p className="text-[0.95rem] font-medium text-on-surface/70">
                  {selectedFile ? selectedFile.name : 'Drop a symptom image or file here'}
                </p>
                <p className="mt-1 text-[0.82rem] text-on-surface/40">
                  Symptom photos, skin conditions, lab reports
                </p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept="image/*,.pdf"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileSelect(file);
                }}
              />
            </div>

            {previewUrl && (
              <div className="overflow-hidden rounded-[1.5rem] border border-outline-variant/30 bg-surface-container-low">
                <img src={previewUrl} alt="Uploaded symptom" className="h-64 w-full object-contain bg-surface" />
                <div className="px-5 py-3 text-sm text-on-surface/60">
                  <p className="font-medium text-on-surface/80">{selectedFile?.name}</p>
                  <p>{selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB` : ''}</p>
                </div>
              </div>
            )}
          </div>

          {/* Right: AI Analysis Results */}
          <div className="space-y-4">
            {analyzing ? (
              <div className="flex flex-col items-center justify-center gap-4 rounded-[1.75rem] bg-surface-container-low px-6 py-16">
                <Loader2 className="h-10 w-10 animate-spin text-primary" />
                <p className="text-sm font-medium text-on-surface/65">Analyzing with Gemini Vision...</p>
                <div className="flex flex-wrap justify-center gap-2">
                  <Pill>gemini-2.0-flash</Pill>
                  <Pill tone="sand">Cure-Quest AI</Pill>
                </div>
              </div>
            ) : aiResult ? (
              <div className="space-y-4">
                <div className="rounded-[1.5rem] bg-primary-fixed/25 px-5 py-5">
                  <div className="flex items-center gap-2 text-primary mb-3">
                    <CheckCircle2 className="h-5 w-5" />
                    <p className="font-medium">AI Analysis Complete</p>
                  </div>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="rounded-xl bg-surface px-4 py-2 text-center">
                      <p className="text-xs text-on-surface/50">Severity</p>
                      <p className="text-lg font-serif font-semibold text-secondary">{aiResult.severity}</p>
                    </div>
                    <div className="rounded-xl bg-surface px-4 py-2 text-center">
                      <p className="text-xs text-on-surface/50">Confidence</p>
                      <p className="text-lg font-serif font-semibold text-primary">{aiResult.confidence}%</p>
                    </div>
                  </div>
                  <p className="text-sm leading-7 text-on-surface/68">{aiResult.summary}</p>
                </div>

                <div className="rounded-[1.5rem] bg-surface-container-low px-5 py-4 space-y-3">
                  <p className="text-sm uppercase tracking-[0.18em] text-secondary/70">Key findings</p>
                  {aiResult.findings.map((finding, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-secondary" />
                      <p className="text-sm leading-7 text-on-surface/68">{finding}</p>
                    </div>
                  ))}
                </div>

                <div className="flex flex-wrap gap-2">
                  <Pill tone="sage">{aiResult.model_used || 'Gemini Vision'}</Pill>
                  <Pill>AI-powered analysis</Pill>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center gap-3 rounded-[1.75rem] bg-surface-container-low px-6 py-16 text-center">
                <Sparkles className="h-10 w-10 text-on-surface/25" />
                <p className="text-sm font-medium text-on-surface/55">Upload a symptom image to trigger AI analysis</p>
                <p className="text-xs text-on-surface/40 max-w-xs">Images are sent to Gemini Vision for analysis, returning severity rating, findings, and a clinical summary.</p>
              </div>
            )}
          </div>
        </div>
      </SoftCard>

      {supportResult ? (
        <div className="space-y-6">
          <SoftCard className="flex flex-col items-center text-center">
            <div className="flex items-center justify-center gap-3 text-primary mb-4">
              <MapPinned className="h-6 w-6" />
              <h3 className="font-serif text-3xl">Agent Map Route</h3>
            </div>
            <p className="text-on-surface/70 max-w-xl">
              I found the best route for pharmacies near <strong>{locationQuery}</strong> based on the current context. You can interact with the live map below.
            </p>
            {locationQuery && (
              <div className="mt-6 h-[450px] w-full max-w-4xl overflow-hidden rounded-[1.5rem] bg-surface-container shadow-lg border border-primary/10">
                <iframe
                  title="Agent Pharmacy Map"
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  loading="lazy"
                  allowFullScreen
                  referrerPolicy="no-referrer-when-downgrade"
                  src={`https://maps.google.com/maps?q=${encodeURIComponent('pharmacies near ' + locationQuery)}&z=14&ie=UTF8&iwloc=&output=embed`}
                />
              </div>
            )}
          </SoftCard>

          <SoftCard>
            <div className="flex items-center gap-3 text-secondary">
              <Waves className="h-5 w-5" />
              <h3 className="font-serif text-2xl">Associated Diet Support</h3>
            </div>
            <p className="mt-3 text-sm leading-7 text-on-surface/65">{supportResult.diet_plan.plan_summary}</p>
            <div className="mt-5 space-y-3">
              {supportResult.diet_plan.meal_rules.map((rule) => (
                <div key={rule} className="rounded-[1.4rem] bg-surface-container-low px-4 py-3 text-sm leading-7 text-on-surface/70">
                  {rule}
                </div>
              ))}
            </div>
          </SoftCard>
        </div>
      ) : null}

    </motion.div>
  );
}
