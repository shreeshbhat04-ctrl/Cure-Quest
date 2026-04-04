import { motion } from 'motion/react';
import { HeartPulse, ShieldCheck, Sparkles, Stethoscope, TimerReset } from 'lucide-react';
import type { WorkspacePayload } from '../lib/api';
import { ErrorState, LoadingState } from '../components/States';
import { Pill, SectionShell, SoftCard } from '../components/ui';

export function DashboardScreen({
  workspace,
  loading,
  error,
  onRefresh,
}: {
  workspace: WorkspacePayload | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}) {
  if (loading && !workspace) return <LoadingState />;
  if (error && !workspace) return <ErrorState message={error} onRetry={onRefresh} />;
  if (!workspace) return <ErrorState message="No workspace loaded." onRetry={onRefresh} />;

  const { patient, conditions, checkin, manifest, prescriptions, cases } = workspace;
  const latestCase = cases[0];
  const latestPrescription = prescriptions[0];

  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -18 }} className="space-y-8">
      <SectionShell
        eyebrow="Dashboard"
        title={
          <>
            Good evening, <span className="text-primary italic">{patient.full_name.split(' ')[0]}</span>.
          </>
        }
        description={checkin.message}
      />

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <SoftCard className="relative overflow-hidden bg-[linear-gradient(135deg,rgba(83,100,49,0.98),rgba(135,154,97,0.96))] text-surface">
          <div className="absolute right-[-3rem] top-[-3rem] h-36 w-36 rounded-full bg-white/10 blur-2xl" />
          <div className="relative z-10 space-y-8">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="eyebrow text-surface/72">Sanctuary pulse</p>
                <h2 className="mt-3 font-serif text-[2rem] leading-tight tracking-[-0.025em] xl:text-[2.35rem]">Care is coordinated and visible.</h2>
              </div>
              <div className="rounded-full bg-white/14 p-3">
                <HeartPulse className="h-6 w-6" />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-[1.5rem] bg-white/10 px-5 py-4">
                <p className="eyebrow text-surface/70">Conditions</p>
                <p className="mt-3 text-[2rem] font-semibold">{conditions.length}</p>
              </div>
              <div className="rounded-[1.5rem] bg-white/10 px-5 py-4">
                <p className="eyebrow text-surface/70">Routines</p>
                <p className="mt-3 text-[2rem] font-semibold">{checkin.routine_tasks.length}</p>
              </div>
              <div className="rounded-[1.5rem] bg-white/10 px-5 py-4">
                <p className="eyebrow text-surface/70">Doctor cases</p>
                <p className="mt-3 text-[2rem] font-semibold">{cases.length}</p>
              </div>
            </div>
          </div>
        </SoftCard>

        <SoftCard className="bg-surface-container-low">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="eyebrow text-primary/65">Latest handoff</p>
              <h2 className="mt-3 font-serif text-[1.7rem] leading-tight">Doctor-ready context</h2>
            </div>
            <div className="rounded-full bg-primary-fixed/45 p-3 text-primary">
              <Stethoscope className="h-5 w-5" />
            </div>
          </div>

          <div className="mt-6 space-y-4">
            {latestCase ? (
              <>
                <Pill>{latestCase.status}</Pill>
                <p className="text-[0.98rem] leading-8 text-on-surface/72">{latestCase.summary}</p>
                <div className="flex flex-wrap gap-3 text-[0.95rem] text-on-surface/60">
                  {latestCase.external_ticket_url ? <a className="hover:text-primary" href={latestCase.external_ticket_url} target="_blank" rel="noreferrer">Asana case</a> : null}
                  {latestCase.calendar_event_url ? <a className="hover:text-primary" href={latestCase.calendar_event_url} target="_blank" rel="noreferrer">Follow-up event</a> : null}
                  {latestCase.drive_file_url ? <a className="hover:text-primary" href={latestCase.drive_file_url} target="_blank" rel="noreferrer">Supporting document</a> : null}
                </div>
              </>
            ) : (
              <p className="text-sm leading-7 text-on-surface/60">No live escalation case yet. The room is calm for now.</p>
            )}
          </div>
        </SoftCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <SoftCard>
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="eyebrow text-tertiary/75">Daily rhythm</p>
              <h2 className="mt-3 font-serif text-[1.7rem] leading-tight">Routine blossoms</h2>
            </div>
            <div className="rounded-full bg-tertiary-container/18 p-3 text-tertiary">
              <TimerReset className="h-5 w-5" />
            </div>
          </div>

          <div className="mt-6 space-y-4">
            {checkin.routine_tasks.slice(0, 4).map((task) => (
              <div key={task.task_id} className="soft-panel">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-[1rem] font-medium">{task.name}</p>
                    <p className="mt-1 text-[0.92rem] leading-7 text-on-surface/58">{task.notes || 'No extra notes attached to this rhythm yet.'}</p>
                  </div>
                  <Pill tone={task.completed ? 'sage' : 'terracotta'}>{task.completed ? 'Completed' : 'Open'}</Pill>
                </div>
              </div>
            ))}
          </div>
        </SoftCard>

        <SoftCard>
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="eyebrow text-primary/75">Agent fabric</p>
              <h2 className="mt-3 font-serif text-[1.7rem] leading-tight">Model choreography</h2>
            </div>
            <div className="rounded-full bg-primary-fixed/45 p-3 text-primary">
              <Sparkles className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-6 space-y-4">
            {Object.entries(manifest.agent_manifest).map(([agentKey, agent]) => (
              <div key={agentKey} className="soft-panel">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-[1rem] font-medium capitalize">{agentKey.replaceAll('_', ' ')}</p>
                  <Pill tone="sage">{agent.primary_model}</Pill>
                </div>
                <p className="mt-2 text-[0.92rem] leading-7 text-on-surface/58">{agent.reason}</p>
              </div>
            ))}
          </div>
        </SoftCard>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <SoftCard className="bg-surface-container-low">
          <div className="flex items-center gap-3 text-primary">
            <ShieldCheck className="h-5 w-5" />
            <h3 className="font-serif text-[1.35rem]">Chronic context</h3>
          </div>
          <div className="mt-5 flex flex-wrap gap-3">
            {conditions.map((condition) => (
              <span key={condition.id}>
                <Pill tone="sand">{condition.name}</Pill>
              </span>
            ))}
          </div>
        </SoftCard>

        <SoftCard className="bg-surface-container-low">
          <h3 className="font-serif text-[1.35rem] text-primary">Latest medication</h3>
          <p className="mt-3 text-[1.05rem]">{latestPrescription?.medication_name ?? 'No scanned prescription yet'}</p>
          <p className="mt-2 text-[0.92rem] leading-7 text-on-surface/60">{latestPrescription?.instructions ?? 'Upload a prescription to turn this into a live medication card.'}</p>
        </SoftCard>

        <SoftCard className="bg-surface-container-low">
          <h3 className="font-serif text-[1.35rem] text-primary">Response language</h3>
          <p className="mt-3 text-[1.05rem]">{patient.preferred_language.toUpperCase()}</p>
          <p className="mt-2 text-[0.92rem] leading-7 text-on-surface/60">The communication agent keeps the tone soft while switching between Gemini, MedGemma, and MedSigLIP where needed.</p>
        </SoftCard>
      </div>
    </motion.div>
  );
}
