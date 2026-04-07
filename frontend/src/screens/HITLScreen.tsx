import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import {
  Brain,
  Clock,
  HeartPulse,
  Loader2,
  PillBottle,
  Plus,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  Trash2,
  Bell,
} from 'lucide-react';
import {
  fetchHITLComprehension,
  fetchReminders,
  saveReminder,
  type HITLComprehensionResponse,
  type Reminder,
  type WorkspacePayload,
} from '../lib/api';
import { EmptyState, LoadingState } from '../components/States';
import { Pill, SectionShell, SoftCard } from '../components/ui';

export function HITLScreen({
  workspace,
  loading,
  patientId,
}: {
  workspace: WorkspacePayload | null;
  loading: boolean;
  onRefresh: () => void;
  patientId: number;
}) {
  // HITL comprehension state
  const [comprehension, setComprehension] = useState<HITLComprehensionResponse | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);

  // Reminder state
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loadingReminders, setLoadingReminders] = useState(false);
  const [showReminderForm, setShowReminderForm] = useState(false);
  const [reminderMed, setReminderMed] = useState('');
  const [reminderTime, setReminderTime] = useState('08:00');
  const [savingReminder, setSavingReminder] = useState(false);

  if (loading && !workspace) return <LoadingState />;
  if (!workspace) return <EmptyState title="No patient context yet" description="Log in or seed a patient before opening the HITL reviewer." />;

  const runComprehension = async () => {
    try {
      setLoadingReport(true);
      setReportError(null);
      const result = await fetchHITLComprehension(patientId);
      setComprehension(result);
    } catch (e) {
      setReportError(e instanceof Error ? e.message : 'Failed to generate report.');
    } finally {
      setLoadingReport(false);
    }
  };

  const loadReminders = async () => {
    try {
      setLoadingReminders(true);
      const result = await fetchReminders(patientId);
      setReminders(result.reminders);
    } catch {
      // silent
    } finally {
      setLoadingReminders(false);
    }
  };

  const handleSaveReminder = async () => {
    if (!reminderMed.trim() || !reminderTime) return;
    try {
      setSavingReminder(true);
      await saveReminder(patientId, reminderMed.trim(), reminderTime);
      setReminderMed('');
      setReminderTime('08:00');
      setShowReminderForm(false);
      await loadReminders();
    } catch {
      // silent
    } finally {
      setSavingReminder(false);
    }
  };

  // Load reminders on mount
  useEffect(() => {
    loadReminders();
  }, [patientId]);

  const medOptions = workspace.prescriptions.map((p) => p.medication_name);

  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -18 }} className="space-y-8">
      <SectionShell
        eyebrow="HITL Review"
        title={
          <>
            Intelligent <span className="text-primary italic">human-in-the-loop</span> patient comprehension.
          </>
        }
        description="An AI-generated comprehensive patient overview with medication durations, condition analysis, recommended actions, and the model's reasoning — all designed for transparent doctor handoff."
      />

      {/* Top Action Bar */}
      <div className="flex flex-wrap gap-4">
        <button
          onClick={runComprehension}
          disabled={loadingReport}
          className="river-stone-btn bg-gradient-to-br from-primary to-primary-container px-6 py-4 text-surface shadow-[0_12px_28px_-8px_rgba(83,100,49,0.4)]"
        >
          {loadingReport ? (
            <span className="flex items-center gap-2"><Loader2 className="h-4 w-4 animate-spin" /> Generating AI comprehension...</span>
          ) : (
            <span className="flex items-center gap-2"><Brain className="h-4 w-4" /> Generate HITL Report</span>
          )}
        </button>
      </div>

      {reportError && <p className="rounded-[1.25rem] bg-secondary-container/30 px-4 py-3 text-sm leading-7 text-secondary">{reportError}</p>}

      {/* Main Grid */}
      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        {/* Left: HITL Report */}
        <div className="space-y-6">
          {comprehension ? (
            <>
              {/* Patient Card */}
              <SoftCard>
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-primary/75">Patient profile</p>
                    <h2 className="mt-2 font-serif text-2xl">{comprehension.patient.name}</h2>
                  </div>
                  <div className="rounded-full bg-primary-fixed/45 p-3 text-primary">
                    <HeartPulse className="h-5 w-5" />
                  </div>
                </div>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <div className="soft-panel">
                    <p className="text-[0.78rem] uppercase tracking-[0.18em] text-on-surface/45">Date of Birth</p>
                    <p className="mt-1 font-medium">{comprehension.patient.dob || 'Not recorded'}</p>
                  </div>
                  <div className="soft-panel">
                    <p className="text-[0.78rem] uppercase tracking-[0.18em] text-on-surface/45">Clinical Summary</p>
                    <p className="mt-1 text-sm leading-7 text-on-surface/65">{comprehension.patient.summary || 'No summary'}</p>
                  </div>
                </div>
              </SoftCard>

              {/* Conditions */}
              <SoftCard>
                <div className="flex items-center gap-3 text-primary">
                  <ShieldCheck className="h-5 w-5" />
                  <h3 className="font-serif text-xl">Active Conditions</h3>
                </div>
                <div className="mt-4 space-y-3">
                  {comprehension.conditions.length > 0 ? comprehension.conditions.map((c, i) => (
                    <div key={i} className="soft-panel flex items-start justify-between gap-3">
                      <div>
                        <p className="font-medium">{c.name}</p>
                        <p className="mt-1 text-sm text-on-surface/55">{c.notes || 'No notes'}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <Pill tone={c.type === 'chronic' ? 'terracotta' : 'sage'}>{c.type}</Pill>
                        <p className="mt-1 text-[0.78rem] text-on-surface/40">{c.last_updated || 'Unknown'}</p>
                      </div>
                    </div>
                  )) : (
                    <p className="text-sm text-on-surface/55">No conditions recorded.</p>
                  )}
                </div>
              </SoftCard>

              {/* Medications with Duration */}
              <SoftCard>
                <div className="flex items-center gap-3 text-secondary">
                  <PillBottle className="h-5 w-5" />
                  <h3 className="font-serif text-xl">Medications & Duration</h3>
                </div>
                <div className="mt-4 space-y-3">
                  {comprehension.medications.length > 0 ? comprehension.medications.map((m, i) => (
                    <div key={i} className="soft-panel">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-medium text-[1.02rem]">{m.name}</p>
                        <Pill tone={m.review_status === 'approved' ? 'sage' : m.review_status === 'pending' ? 'sand' : 'terracotta'}>
                          {m.review_status}
                        </Pill>
                      </div>
                      <div className="mt-3 grid gap-2 md:grid-cols-3">
                        <div>
                          <p className="text-[0.72rem] uppercase tracking-[0.18em] text-on-surface/40">Dosage</p>
                          <p className="mt-0.5 text-sm">{m.dosage || '—'}</p>
                        </div>
                        <div>
                          <p className="text-[0.72rem] uppercase tracking-[0.18em] text-on-surface/40">Days on med</p>
                          <p className="mt-0.5 text-sm font-semibold text-primary">{m.days_on_medication ?? '—'}</p>
                        </div>
                        <div>
                          <p className="text-[0.72rem] uppercase tracking-[0.18em] text-on-surface/40">Confidence</p>
                          <p className="mt-0.5 text-sm">{(m.confidence_score * 100).toFixed(0)}%</p>
                        </div>
                      </div>
                      {m.instructions && (
                        <p className="mt-2 text-sm leading-7 text-on-surface/55 italic">"{m.instructions}"</p>
                      )}
                    </div>
                  )) : (
                    <p className="text-sm text-on-surface/55">No medications recorded.</p>
                  )}
                </div>
              </SoftCard>

              {/* AI Analysis */}
              <SoftCard className="relative overflow-hidden bg-[linear-gradient(135deg,rgba(83,100,49,0.04),rgba(213,235,170,0.12))]">
                <div className="flex items-center gap-3 text-primary">
                  <Sparkles className="h-5 w-5" />
                  <h3 className="font-serif text-xl">AI Analysis & Recommended Actions</h3>
                </div>
                <div className="mt-4 whitespace-pre-wrap text-[0.95rem] leading-8 text-on-surface/75">
                  {comprehension.ai_analysis}
                </div>
                <div className="mt-4">
                  <Pill tone="sage">Powered by Gemini 3.1 Flash</Pill>
                </div>
              </SoftCard>
            </>
          ) : (
            <SoftCard className="bg-surface-container-low">
              <div className="flex flex-col items-center gap-4 py-12 text-center">
                <div className="rounded-full bg-primary-fixed/35 p-5 text-primary">
                  <Stethoscope className="h-8 w-8" />
                </div>
                <div>
                  <h3 className="font-serif text-xl">No comprehension report generated yet</h3>
                  <p className="mt-2 text-sm leading-7 text-on-surface/55">
                    Click "Generate HITL Report" to create a comprehensive AI-powered patient review with conditions, medication durations, and recommended next steps.
                  </p>
                </div>
              </div>
            </SoftCard>
          )}
        </div>

        {/* Right: Medication Reminders */}
        <div className="space-y-6">
          <SoftCard>
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3 text-secondary">
                <Bell className="h-5 w-5" />
                <h3 className="font-serif text-xl">Medication Reminders</h3>
              </div>
              <button
                onClick={() => setShowReminderForm(!showReminderForm)}
                className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-container/40 text-secondary transition-colors hover:bg-secondary-container/60"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>

            {/* Add Reminder Form */}
            {showReminderForm && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 space-y-4 rounded-[1.5rem] bg-surface-container-low px-5 py-5"
              >
                <label className="space-y-2">
                  <span className="text-sm font-medium text-on-surface/60">Medication</span>
                  {medOptions.length > 0 ? (
                    <select
                      value={reminderMed}
                      onChange={(e) => setReminderMed(e.target.value)}
                      className="input-shell"
                    >
                      <option value="">Select medication...</option>
                      {medOptions.map((med) => (
                        <option key={med} value={med}>{med}</option>
                      ))}
                      <option value="__custom">Other (type below)</option>
                    </select>
                  ) : (
                    <input
                      value={reminderMed}
                      onChange={(e) => setReminderMed(e.target.value)}
                      placeholder="e.g. Metformin"
                      className="input-shell"
                    />
                  )}
                  {reminderMed === '__custom' && (
                    <input
                      value=""
                      onChange={(e) => setReminderMed(e.target.value)}
                      placeholder="Enter medication name"
                      className="input-shell mt-2"
                    />
                  )}
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-on-surface/60">Reminder Time</span>
                  <input
                    type="time"
                    value={reminderTime}
                    onChange={(e) => setReminderTime(e.target.value)}
                    className="input-shell"
                  />
                </label>

                <button
                  onClick={handleSaveReminder}
                  disabled={savingReminder || !reminderMed.trim() || reminderMed === '__custom'}
                  className="river-stone-btn w-full bg-gradient-to-br from-secondary to-secondary-container px-6 py-3 text-surface disabled:opacity-50"
                >
                  {savingReminder ? (
                    <span className="flex items-center justify-center gap-2"><Loader2 className="h-4 w-4 animate-spin" /> Saving...</span>
                  ) : (
                    <span className="flex items-center justify-center gap-2"><Clock className="h-4 w-4" /> Set Reminder</span>
                  )}
                </button>
              </motion.div>
            )}

            {/* Reminder List */}
            <div className="mt-5 space-y-3">
              {loadingReminders ? (
                <p className="text-sm text-on-surface/45">Loading reminders...</p>
              ) : reminders.length > 0 ? (
                reminders.map((r) => (
                  <div key={r.id} className="flex items-center justify-between gap-3 rounded-[1.25rem] bg-surface-container-low px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-container/30 text-secondary">
                        <Clock className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="text-[0.95rem] font-medium">{r.medication_name}</p>
                        <p className="text-[0.82rem] text-on-surface/50">
                          Every day at <span className="font-semibold text-secondary">{r.reminder_time}</span>
                        </p>
                      </div>
                    </div>
                    <Pill tone="sage">Active</Pill>
                  </div>
                ))
              ) : (
                <p className="text-sm leading-7 text-on-surface/55">No reminders set yet. Tap + to create your first medication reminder.</p>
              )}
            </div>
          </SoftCard>

          {/* Nurture Card */}
          <SoftCard className="bg-tertiary-container/18">
            <p className="mb-2 font-serif text-[1.1rem] text-tertiary">About HITL Reviews</p>
            <p className="text-[0.92rem] leading-7 text-on-surface/60">
              Human-in-the-Loop ensures that the AI's recommendations are always reviewed by a human before any clinical action is taken. The comprehensive report gives doctors full patient context, medication durations, and the model's reasoning for transparency and accountability.
            </p>
          </SoftCard>
        </div>
      </div>
    </motion.div>
  );
}
