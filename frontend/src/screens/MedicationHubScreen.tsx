import React, { useMemo, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { FileSearch, Microscope, PillBottle, ShieldAlert, Upload, CheckCircle2, Loader2 } from 'lucide-react';
import {
  checkAlternatives,
  fetchDrugLabel,
  uploadDocumentFile,
  type AlternativeResponse,
  type DocumentUploadResponse,
  type DrugLabelResponse,
  type WorkspacePayload,
} from '../lib/api';
import { EmptyState, LoadingState } from '../components/States';
import { Pill, SectionShell, SoftCard } from '../components/ui';

export function MedicationHubScreen({
  workspace,
  loading,
  patientId,
}: {
  workspace: WorkspacePayload | null;
  loading: boolean;
  onRefresh: () => void;
  patientId: number;
}) {
  const seededMedication = workspace?.prescriptions[0]?.medication_name ?? 'Metformin';
  const [medicationName, setMedicationName] = useState(seededMedication);
  const [alternativeResult, setAlternativeResult] = useState<AlternativeResponse | null>(null);
  const [drugLabel, setDrugLabel] = useState<DrugLabelResponse | null>(null);
  const [busy, setBusy] = useState<'alternatives' | 'label' | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  // File upload state
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<DocumentUploadResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const latestPrescription = workspace?.prescriptions[0] ?? null;
  const triggerManifest = workspace?.manifest.trigger_manifest ?? {};

  const documentRouteSummary = useMemo(() => {
    const name = selectedFile?.name?.toLowerCase() ?? '';
    if (name.endsWith('.png') || name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.webp')) {
      return {
        route: 'medical_image',
        models: ['google/medsiglip-448', 'google/medgemma-1.5-4b-it'],
      };
    }
    return {
      route: 'document_or_text',
      models: ['google/medgemma-1.5-4b-it'],
    };
  }, [selectedFile]);

  if (loading && !workspace) return <LoadingState />;
  if (!workspace) return <EmptyState title="No medication context yet" description="Seed or create a patient before opening the medication hub." />;

  const runAlternativeCheck = async () => {
    try {
      setBusy('alternatives');
      setFeedback(null);
      const result = await checkAlternatives(patientId, medicationName);
      setAlternativeResult(result);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Unable to check alternatives.');
    } finally {
      setBusy(null);
    }
  };

  const runDrugLabelLookup = async () => {
    try {
      setBusy('label');
      setFeedback(null);
      const result = await fetchDrugLabel(medicationName);
      setDrugLabel(result);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Unable to fetch the drug label.');
    } finally {
      setBusy(null);
    }
  };

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setUploadResult(null);
    setUploadError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    try {
      setUploading(true);
      setUploadError(null);
      const result = await uploadDocumentFile(patientId, selectedFile);
      setUploadResult(result);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(file);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -18 }} className="space-y-8">
      <SectionShell
        eyebrow="Medication Hub"
        title={
          <>
            Resolve medication friction <span className="text-primary italic">before</span> it reaches the patient.
          </>
        }
        description="This screen brings together alternative checks, label intelligence, and document-routing visibility so the medication path feels intentional instead of reactive."
      />

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <SoftCard className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-primary/75">Medication query</p>
              <h2 className="mt-2 font-serif text-2xl">Alternative and label console</h2>
            </div>
            <div className="rounded-full bg-primary-fixed/45 p-3 text-primary">
              <PillBottle className="h-5 w-5" />
            </div>
          </div>

          <label className="space-y-2">
            <span className="text-sm font-medium text-on-surface/60">Medication name</span>
            <input value={medicationName} onChange={(e) => setMedicationName(e.target.value)} className="input-shell" />
          </label>

          <div className="flex flex-wrap gap-3">
            <button onClick={runAlternativeCheck} className="river-stone-btn bg-gradient-to-br from-primary to-primary-container px-6 py-4 text-surface">
              {busy === 'alternatives' ? 'Checking...' : 'Check alternatives'}
            </button>
            <button onClick={runDrugLabelLookup} className="river-stone-btn bg-surface-container-low px-6 py-4 text-on-surface/75 hover:bg-surface-container-high">
              {busy === 'label' ? 'Looking up...' : 'Fetch openFDA label'}
            </button>
          </div>

          {feedback ? <p className="rounded-[1.25rem] bg-surface-container-low px-4 py-3 text-sm leading-7 text-on-surface/70">{feedback}</p> : null}
        </SoftCard>

        <SoftCard className="bg-surface-container-low">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-tertiary/75">Current context</p>
              <h2 className="mt-2 font-serif text-2xl">Last prescription</h2>
            </div>
            <div className="rounded-full bg-tertiary-container/18 p-3 text-tertiary">
              <Microscope className="h-5 w-5" />
            </div>
          </div>
          {latestPrescription ? (
            <div className="mt-6 space-y-3">
              <Pill>{latestPrescription.review_status}</Pill>
              <p className="text-lg">{latestPrescription.medication_name}</p>
              <p className="text-sm leading-7 text-on-surface/60">{latestPrescription.instructions ?? 'No explicit instructions stored yet.'}</p>
              {latestPrescription.document_drive_file_url ? (
                <a href={latestPrescription.document_drive_file_url} target="_blank" rel="noreferrer" className="inline-block text-sm text-primary hover:underline">
                  Open attached Drive document
                </a>
              ) : null}
            </div>
          ) : (
            <p className="mt-6 text-sm leading-7 text-on-surface/60">There is no prescription record yet. Scan or upload one and this panel will hydrate itself.</p>
          )}
        </SoftCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <SoftCard>
          <div className="flex items-center gap-3 text-secondary">
            <ShieldAlert className="h-5 w-5" />
            <h3 className="font-serif text-2xl">Alternative results</h3>
          </div>
          {alternativeResult ? (
            <div className="mt-5 space-y-4">
              <div className="rounded-[1.4rem] bg-surface-container-low px-4 py-3 text-sm leading-7 text-on-surface/65">
                {alternativeResult.safety_summary}
              </div>
              {alternativeResult.escalation_required ? <Pill tone="terracotta">Doctor escalation recommended</Pill> : <Pill tone="sage">No escalation triggered</Pill>}
              <div className="grid gap-4">
                {alternativeResult.candidates.map((candidate) => (
                  <div key={candidate.name} className="rounded-[1.5rem] bg-surface-container-low px-5 py-4">
                    <div className="flex items-center justify-between gap-4">
                      <p className="font-medium">{candidate.name}</p>
                      <Pill tone={candidate.stock_status === 'in_stock' ? 'sage' : 'terracotta'}>{candidate.stock_status}</Pill>
                    </div>
                    <p className="mt-2 text-sm text-on-surface/60">{candidate.formulation_note}</p>
                    <p className="mt-1 text-sm text-secondary">{candidate.safety_note}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <EmptyState title="No alternative run yet" description="Check a medication and this area will turn into a safety-aware alternative workspace." />
          )}
        </SoftCard>

        {/* Document Upload Card */}
        <SoftCard>
          <div className="flex items-center gap-3 text-primary">
            <FileSearch className="h-5 w-5" />
            <h3 className="font-serif text-2xl">Upload document</h3>
          </div>
          <div className="mt-5 space-y-4">
            {/* Drop Zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`flex cursor-pointer flex-col items-center gap-3 rounded-[1.75rem] border-2 border-dashed px-6 py-10 transition-all duration-200 ${
                isDragOver
                  ? 'border-primary bg-primary-fixed/20'
                  : 'border-outline-variant/40 bg-surface-container-low hover:border-primary/40 hover:bg-surface-container-high/60'
              }`}
            >
              <Upload className={`h-8 w-8 ${isDragOver ? 'text-primary' : 'text-on-surface/35'}`} />
              <div className="text-center">
                <p className="text-[0.95rem] font-medium text-on-surface/70">
                  {selectedFile ? selectedFile.name : 'Drop a file here or click to browse'}
                </p>
                <p className="mt-1 text-[0.82rem] text-on-surface/40">
                  Prescriptions, lab reports, symptom photos
                </p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept="image/*,.pdf,.doc,.docx"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileSelect(file);
                }}
              />
            </div>

            {/* Selected File Preview */}
            {selectedFile && (
              <div className="space-y-3">
                <div className="rounded-[1.5rem] bg-surface-container-low px-5 py-4">
                  <p className="text-sm uppercase tracking-[0.18em] text-primary/65">Expected route</p>
                  <p className="mt-2 font-medium">{documentRouteSummary.route}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {documentRouteSummary.models.map((model) => (
                      <span key={model}>
                        <Pill>{model}</Pill>
                      </span>
                    ))}
                  </div>
                </div>
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="river-stone-btn w-full bg-gradient-to-br from-primary to-primary-container px-6 py-4 text-surface"
                >
                  {uploading ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" /> Uploading & classifying...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      <Upload className="h-4 w-4" /> Upload to Google Drive
                    </span>
                  )}
                </button>
              </div>
            )}

            {/* Upload Result */}
            {uploadResult && (
              <div className="rounded-[1.5rem] bg-primary-fixed/30 px-5 py-4">
                <div className="flex items-center gap-2 text-primary">
                  <CheckCircle2 className="h-5 w-5" />
                  <p className="font-medium">Uploaded successfully!</p>
                </div>
                <div className="mt-3 space-y-1 text-sm text-on-surface/65">
                  <p>File: {uploadResult.file_name}</p>
                  {uploadResult.image_category && <p>AI Category: <Pill tone="sage">{uploadResult.image_category}</Pill></p>}
                  {uploadResult.web_view_link && (
                    <a href={uploadResult.web_view_link} target="_blank" rel="noreferrer" className="mt-2 inline-block text-primary hover:underline">
                      Open in Google Drive →
                    </a>
                  )}
                </div>
              </div>
            )}

            {uploadError && (
              <p className="rounded-[1.25rem] bg-secondary-container/30 px-4 py-3 text-sm leading-7 text-secondary">{uploadError}</p>
            )}

            <div className="rounded-[1.5rem] bg-surface-container-low px-5 py-4">
              <p className="text-sm uppercase tracking-[0.18em] text-tertiary/70">Trigger memory</p>
              <p className="mt-2 text-sm leading-7 text-on-surface/60">
                {triggerManifest.medical_image_upload || 'Medical images should route through MedSigLIP first, then MedGemma.'}
              </p>
            </div>
          </div>
        </SoftCard>
      </div>

      {drugLabel ? (
        <SoftCard className="bg-surface-container-low">
          <h3 className="font-serif text-2xl text-primary">openFDA snapshot</h3>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="rounded-[1.5rem] bg-surface px-5 py-4">
              <p className="text-sm uppercase tracking-[0.18em] text-primary/65">Medication</p>
              <p className="mt-2 text-lg">{drugLabel.medication_name}</p>
            </div>
            <div className="rounded-[1.5rem] bg-surface px-5 py-4">
              <p className="text-sm uppercase tracking-[0.18em] text-primary/65">Label found</p>
              <p className="mt-2 text-lg">{drugLabel.found ? 'Yes' : 'No'}</p>
            </div>
          </div>
          <pre className="mt-5 overflow-x-auto rounded-[1.5rem] bg-surface px-5 py-4 text-xs leading-6 text-on-surface/70">
            {JSON.stringify(drugLabel.label, null, 2)}
          </pre>
        </SoftCard>
      ) : null}
    </motion.div>
  );
}
