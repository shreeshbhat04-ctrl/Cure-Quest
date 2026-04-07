import { useState } from 'react';
import { motion } from 'motion/react';
import { CalendarDays, MapPinned, Route, Stethoscope, Waves } from 'lucide-react';
import { createCalendarEvent, createEscalation, fetchDietSupport, type DietSupportResponse, type WorkspacePayload } from '../lib/api';
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
              {busyAction === 'maze' ? 'Mapping...' : 'Map support route'}
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

      {supportResult ? (
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <SoftCard>
            <div className="flex items-center gap-3 text-secondary">
              <Waves className="h-5 w-5" />
              <h3 className="font-serif text-2xl">Diet support</h3>
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

          <SoftCard>
            <div className="flex items-center gap-3 text-primary">
              <MapPinned className="h-5 w-5" />
              <h3 className="font-serif text-2xl">Nearby pharmacy set</h3>
            </div>
            <div className="mt-5 grid gap-4">
              {supportResult.pharmacy_result.pharmacies.length ? (
                supportResult.pharmacy_result.pharmacies.slice(0, 4).map((pharmacy, index) => (
                  <div key={`${String(pharmacy.name)}-${index}`} className="rounded-[1.5rem] bg-surface-container-low px-5 py-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-medium">{String(pharmacy.name ?? 'Unnamed pharmacy')}</p>
                        <p className="mt-1 text-sm leading-7 text-on-surface/60">{String(pharmacy.formatted_address ?? pharmacy.vicinity ?? 'Address unavailable')}</p>
                      </div>
                      <Pill>{String(pharmacy.business_status ?? 'available')}</Pill>
                    </div>
                  </div>
                ))
              ) : (
                <EmptyState title="No pharmacy results" description="Try another neighborhood or city query to draw a stronger route." />
              )}
            </div>

            {supportResult.pharmacy_result.pharmacies.length > 0 && locationQuery && (
              <div className="mt-5 h-[280px] w-full overflow-hidden rounded-[1.5rem] bg-surface-container shadow-inner">
                <iframe
                  title="Pharmacy Map"
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
        </div>
      ) : null}

      <div className="grid gap-6 md:grid-cols-3">
        <SoftCard className="bg-surface-container-low">
          <div className="flex items-center gap-3 text-primary">
            <CalendarDays className="h-5 w-5" />
            <h3 className="font-serif text-xl">Calendar-ready</h3>
          </div>
          <p className="mt-3 text-sm leading-7 text-on-surface/60">Follow-ups from this screen feed the same Google Calendar connection already used by the escalation flow.</p>
        </SoftCard>
        <SoftCard className="bg-surface-container-low">
          <h3 className="font-serif text-xl text-primary">Condition-aware</h3>
          <p className="mt-3 text-sm leading-7 text-on-surface/60">The diet and pharmacy suggestions stay grounded in the patient’s chronic condition memory before they turn into doctor-facing handoffs.</p>
        </SoftCard>
        <SoftCard className="bg-surface-container-low">
          <h3 className="font-serif text-xl text-primary">MCP-compatible</h3>
          <p className="mt-3 text-sm leading-7 text-on-surface/60">This screen is already using backend routes that can stay compatible when more of the logic moves behind MCP tools later.</p>
        </SoftCard>
      </div>
    </motion.div>
  );
}
