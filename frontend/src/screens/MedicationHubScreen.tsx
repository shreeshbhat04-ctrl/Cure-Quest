import React, { useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'motion/react';
import {
  CheckCircle2,
  ChefHat,
  CircleAlert,
  Clock3,
  FileSearch,
  ImageOff,
  Loader2,
  Microscope,
  PillBottle,
  ShieldAlert,
  Sparkles,
  Upload,
} from 'lucide-react';
import coffeeImage from '../../assests/Coffee.png';
import dairyProductsImage from '../../assests/dairy_products.png';
import highSugarImage from '../../assests/High_sugar_contents.png';
import spicyChickenImage from '../../assests/Spicy_chicken.png';
import {
  checkAlternatives,
  fetchDietRecipes,
  fetchDietSupport,
  fetchDrugLabel,
  generateDietRecipes,
  uploadDocumentFile,
  type AlternativeResponse,
  type DietRecipe,
  type DietSupportResponse,
  type DocumentUploadResponse,
  type DrugLabelResponse,
  type GenerateDietRecipesPayload,
  type RecipeIngredient,
  type WorkspacePayload,
} from '../lib/api';
import { EmptyState, LoadingState } from '../components/States';
import { Pill, SectionShell, SoftCard } from '../components/ui';

type RecipeViewState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'success'; recipes: DietRecipe[]; fallbackUsed: boolean; safetySummary: string };

const COUNTABLE_UNITS = new Set(['piece', 'pieces', 'clove', 'cloves', 'egg', 'eggs', 'leaf', 'leaves']);

const watchoutVisuals = [
  {
    title: 'Coffee spikes empty-stomach discomfort',
    detail: 'Have caffeine after food, especially on metformin mornings.',
    image: coffeeImage,
  },
  {
    title: 'Heavy dairy may need a gentler swap',
    detail: 'Use tolerated curd or a lighter portion when digestion is sensitive.',
    image: dairyProductsImage,
  },
  {
    title: 'High sugar add-ons break the steady plate',
    detail: 'Keep quick sweets small so the meal still feels balanced.',
    image: highSugarImage,
  },
  {
    title: 'Spicy proteins can turn a safe meal into a rough one',
    detail: 'Keep the protein, lower the heat, and let the meal stay usable.',
    image: spicyChickenImage,
  },
];

function parseIngredientList(value: string) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function clampServings(value: number) {
  return Math.max(1, Math.min(12, value));
}

function inferImageCategory(file: File, route: string): 'PRESCRIPTION' | 'SYMPTOM' | 'OTHER' {
  const lowerName = file.name.toLowerCase();
  if (lowerName.includes('prescription') || lowerName.includes('rx') || lowerName.includes('medicine')) {
    return 'PRESCRIPTION';
  }
  if (route === 'medical_image') {
    return 'SYMPTOM';
  }
  return 'OTHER';
}

function formatScaledIngredient(
  ingredient: RecipeIngredient,
  targetServings: number,
  defaultServings: number,
) {
  const scaleFactor = targetServings / defaultServings;
  const scaledQuantity = ingredient.quantity * scaleFactor;
  const normalizedUnit = ingredient.unit.toLowerCase();
  const roundedQuantity = COUNTABLE_UNITS.has(normalizedUnit)
    ? Math.max(1, Math.round(scaledQuantity))
    : Math.round(scaledQuantity * 10) / 10;

  return `${roundedQuantity} ${ingredient.unit} ${ingredient.name}`;
}

function buildRecipePayload(
  patientId: number,
  medicationName: string,
  generatorValues: {
    mealType: string;
    availableIngredients: string;
    avoidIngredients: string;
    dietaryPattern: string;
    cuisinePreference: string;
    maxCookMinutes: string;
    servings: number;
  },
): GenerateDietRecipesPayload {
  const maxCookMinutes = Number(generatorValues.maxCookMinutes);

  return {
    patient_id: patientId,
    medication_name: medicationName || null,
    meal_type: generatorValues.mealType,
    available_ingredients: parseIngredientList(generatorValues.availableIngredients),
    avoid_ingredients: parseIngredientList(generatorValues.avoidIngredients),
    dietary_pattern: generatorValues.dietaryPattern || null,
    cuisine_preference: generatorValues.cuisinePreference || null,
    max_cook_minutes: Number.isFinite(maxCookMinutes) && maxCookMinutes > 0 ? maxCookMinutes : null,
    servings: clampServings(generatorValues.servings),
    count: 3,
  };
}

function RecipeCard({
  recipe,
  selected,
  onSelect,
  label,
}: {
  recipe: DietRecipe;
  selected: boolean;
  onSelect: (recipe: DietRecipe) => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelect(recipe)}
      className={`group overflow-hidden rounded-[1.8rem] border text-left transition-[transform,border-color,box-shadow] duration-200 ease-out active:scale-[0.98] ${
        selected
          ? 'border-primary/45 bg-surface shadow-[0_16px_40px_-20px_rgba(83,100,49,0.35)]'
          : 'border-outline-variant/35 bg-surface-container-low hover:border-primary/25 hover:shadow-[0_14px_30px_-18px_rgba(27,28,21,0.2)]'
      }`}
    >
      <div className="relative h-44 overflow-hidden bg-surface-container-high">
        {recipe.image_url ? (
          <img
            src={recipe.image_url}
            alt={recipe.title}
            className="h-full w-full object-cover transition-transform duration-300 ease-out group-hover:scale-[1.03]"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-on-surface/30">
            <ImageOff className="h-8 w-8" />
          </div>
        )}
        <div className="absolute inset-x-0 top-0 flex items-center justify-between p-4">
          <Pill tone={recipe.source === 'generated' ? 'sage' : 'sand'}>{label}</Pill>
          {recipe.safety_notes.some((note) => note.severity === 'caution') ? (
            <span className="rounded-full bg-secondary-container/85 px-3 py-1 text-xs font-medium text-secondary">
              caution
            </span>
          ) : null}
        </div>
      </div>

      <div className="space-y-4 p-5">
        <div className="space-y-2">
          <div className="flex items-start justify-between gap-4">
            <h4 className="font-serif text-[1.35rem] leading-7">{recipe.title}</h4>
            <span className="shrink-0 text-sm text-on-surface/45">{recipe.default_servings} servings</span>
          </div>
          <p className="text-sm leading-7 text-on-surface/62">{recipe.description}</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <span className="inline-flex items-center gap-2 rounded-full bg-surface px-3 py-1.5 text-xs text-on-surface/55">
            <Clock3 className="h-3.5 w-3.5" />
            {recipe.cook_time}
          </span>
          {recipe.meal_type ? <Pill>{recipe.meal_type}</Pill> : null}
          {recipe.dietary_pattern ? <Pill tone="sand">{recipe.dietary_pattern}</Pill> : null}
        </div>

        <p className="text-sm leading-7 text-primary">{recipe.why_it_fits}</p>
      </div>
    </button>
  );
}

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
  const [medicationName, setMedicationName] = useState('Metformin');
  const [selectedPrescriptionId, setSelectedPrescriptionId] = useState<number | null>(null);
  const [alternativeResult, setAlternativeResult] = useState<AlternativeResponse | null>(null);
  const [drugLabel, setDrugLabel] = useState<DrugLabelResponse | null>(null);
  const [busy, setBusy] = useState<'alternatives' | 'label' | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [dietSupport, setDietSupport] = useState<DietSupportResponse | null>(null);
  const [dietSupportError, setDietSupportError] = useState<string | null>(null);
  const [dietSupportLoading, setDietSupportLoading] = useState(false);
  const [curatedRecipes, setCuratedRecipes] = useState<DietRecipe[]>([]);
  const [curatedLoading, setCuratedLoading] = useState(false);
  const [curatedError, setCuratedError] = useState<string | null>(null);
  const [generatedState, setGeneratedState] = useState<RecipeViewState>({ status: 'idle' });
  const [selectedRecipe, setSelectedRecipe] = useState<DietRecipe | null>(null);
  const [selectedServings, setSelectedServings] = useState(2);
  const [generatorValues, setGeneratorValues] = useState({
    mealType: 'breakfast',
    availableIngredients: 'rava, carrot, beans, curd, cucumber',
    avoidIngredients: 'grapefruit, extra chilli',
    dietaryPattern: 'vegetarian',
    cuisinePreference: 'South Indian',
    maxCookMinutes: '25',
    servings: 2,
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<DocumentUploadResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const prescriptions = workspace?.prescriptions ?? [];
  const latestPrescription =
    prescriptions.find((prescription) => prescription.id === selectedPrescriptionId) ??
    prescriptions[0] ??
    null;
  const triggerManifest = workspace?.manifest.trigger_manifest ?? {};

  useEffect(() => {
    if (!prescriptions.length) {
      setSelectedPrescriptionId(null);
      return;
    }

    setSelectedPrescriptionId((currentId) => {
      if (currentId && prescriptions.some((prescription) => prescription.id === currentId)) {
        return currentId;
      }
      return prescriptions[0].id;
    });
  }, [prescriptions]);

  useEffect(() => {
    if (!latestPrescription?.medication_name) return;
    setMedicationName(latestPrescription.medication_name);
  }, [latestPrescription?.id, latestPrescription?.medication_name]);

  useEffect(() => {
    let active = true;

    const loadCuratedRecipes = async () => {
      try {
        setCuratedLoading(true);
        setCuratedError(null);
        const result = await fetchDietRecipes();
        if (!active) return;
        setCuratedRecipes(result.recipes);
        setSelectedRecipe((current) => current ?? result.recipes[0] ?? null);
      } catch (error) {
        if (!active) return;
        setCuratedError(error instanceof Error ? error.message : 'Unable to load curated recipes.');
      } finally {
        if (active) setCuratedLoading(false);
      }
    };

    void loadCuratedRecipes();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!workspace || !medicationName.trim()) return;
    let active = true;

    const loadDietSupport = async () => {
      try {
        setDietSupportLoading(true);
        setDietSupportError(null);
        const result = await fetchDietSupport(patientId, medicationName, 'Medication Hub');
        if (!active) return;
        setDietSupport(result);
      } catch (error) {
        if (!active) return;
        setDietSupportError(error instanceof Error ? error.message : 'Unable to build diet support.');
      } finally {
        if (active) setDietSupportLoading(false);
      }
    };

    void loadDietSupport();

    return () => {
      active = false;
    };
  }, [workspace, patientId, medicationName]);

  useEffect(() => {
    if (!selectedRecipe) return;
    setSelectedServings(selectedRecipe.default_servings);
  }, [selectedRecipe]);

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

  const scaledIngredients = useMemo(() => {
    if (!selectedRecipe) return [];
    return selectedRecipe.ingredients.map((ingredient) =>
      formatScaledIngredient(ingredient, selectedServings, selectedRecipe.default_servings),
    );
  }, [selectedRecipe, selectedServings]);

  const patientConditions = useMemo(
    () => workspace?.conditions.map((condition) => condition.name) ?? [],
    [workspace?.conditions],
  );

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
      const doctorProfiles = ['Dr. Stephen Strange', 'Dr. Shaun Murphy', 'Dr. Aris Thorne'];
      const doctorName = doctorProfiles[Math.abs(patientId) % doctorProfiles.length];
      const patientName = workspace.patient.full_name;
      const diseaseName = workspace.conditions[0]?.name ?? medicationName ?? 'general-condition';
      const captureDate = new Date().toISOString().slice(0, 10);
      const imageCategory = inferImageCategory(selectedFile, documentRouteSummary.route);

      const result = await uploadDocumentFile(patientId, selectedFile, {
        prescription_id: imageCategory === 'PRESCRIPTION' ? selectedPrescriptionId : null,
        doctor_name: doctorName,
        patient_name: patientName,
        disease_name: diseaseName,
        capture_date: captureDate,
        image_category: imageCategory,
      });
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

  const handleRecipeGenerate = async () => {
    try {
      setGeneratedState({ status: 'loading' });
      const result = await generateDietRecipes(buildRecipePayload(patientId, medicationName, generatorValues));
      setGeneratedState({
        status: 'success',
        recipes: result.recipes,
        fallbackUsed: result.fallback_used,
        safetySummary: result.safety_summary,
      });
      setSelectedRecipe(result.recipes[0] ?? null);
    } catch (error) {
      setGeneratedState({
        status: 'error',
        message: error instanceof Error ? error.message : 'Unable to generate recipes right now.',
      });
    }
  };

  const hasGeneratedRecipes = generatedState.status === 'success' && generatedState.recipes.length > 0;

  return (
    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -18 }} className="space-y-8">
      <SectionShell
        eyebrow="Medication Hub"
        title={
          <>
            Resolve medication friction <span className="text-primary italic">before</span> it reaches the patient.
          </>
        }
        description="This screen brings together alternative checks, label intelligence, document-routing visibility, and a new recipe support studio so the medication path feels intentional instead of reactive."
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
              {prescriptions.length > 1 ? (
                <label className="block space-y-2">
                  <span className="text-sm font-medium text-on-surface/60">Prescription record</span>
                  <select
                    value={selectedPrescriptionId ?? latestPrescription.id}
                    onChange={(event) => setSelectedPrescriptionId(Number(event.target.value))}
                    className="input-shell appearance-none"
                  >
                    {prescriptions.map((prescription) => (
                      <option key={prescription.id} value={prescription.id}>
                        {prescription.medication_name} · {new Date(prescription.created_at).toLocaleDateString()}
                      </option>
                    ))}
                  </select>
                </label>
              ) : null}
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

        <SoftCard>
          <div className="flex items-center gap-3 text-primary">
            <FileSearch className="h-5 w-5" />
            <h3 className="font-serif text-2xl">Drug label intelligence</h3>
          </div>
          {drugLabel ? (
            <div className="mt-5 space-y-4">
              <div className="rounded-[1.4rem] bg-surface-container-low px-4 py-3">
                <p className="text-sm uppercase tracking-[0.18em] text-primary/65">openFDA result</p>
                <p className="mt-2 font-medium">{drugLabel.medication_name}</p>
                <Pill tone={drugLabel.found ? 'sage' : 'terracotta'}>{drugLabel.found ? 'Label found' : 'Not found'}</Pill>
              </div>
              {drugLabel.label ? (
                <div className="max-h-60 overflow-y-auto rounded-[1.5rem] bg-surface-container-low px-5 py-4 text-sm leading-7 text-on-surface/65">
                  <pre className="whitespace-pre-wrap font-sans">{JSON.stringify(drugLabel.label, null, 2)}</pre>
                </div>
              ) : null}
            </div>
          ) : (
            <EmptyState title="No drug label fetched yet" description="Use the 'Fetch openFDA label' button above to look up a medication's safety information." />
          )}
          <div className="mt-5 rounded-[1.5rem] bg-surface-container-low px-5 py-4">
            <p className="text-sm uppercase tracking-[0.18em] text-tertiary/70">Trigger memory</p>
            <p className="mt-2 text-sm leading-7 text-on-surface/60">
              {triggerManifest.medical_image_upload || 'Medical images should route through MedSigLIP first, then MedGemma.'}
            </p>
          </div>
        </SoftCard>
      </div>

      <section className="space-y-6">
        <SectionShell
          eyebrow="Diet Support"
          title={
            <>
              Turn medication guidance into a <span className="text-secondary italic">usable kitchen plan</span>.
            </>
          }
          description="The static demo now places recipe support inside Medication Hub: a compact safety summary, generator controls, generated ideas, fallback recipes, and a full detail panel with scalable ingredients."
        >
          <div className="flex flex-wrap gap-2">
            <Pill>{medicationName || 'Medication-aware'}</Pill>
            {patientConditions.map((condition) => (
              <Pill key={condition} tone="sand">{condition}</Pill>
            ))}
          </div>
        </SectionShell>

        <div className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
          <div className="space-y-6">
            <SoftCard className="overflow-hidden bg-[linear-gradient(135deg,rgba(213,235,170,0.26),rgba(252,250,238,0.92))]">
              <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                <div className="space-y-5">
                  <div className="flex items-center gap-3 text-primary">
                    <ChefHat className="h-5 w-5" />
                    <h3 className="font-serif text-2xl">Diet safety summary</h3>
                  </div>

                  {dietSupportLoading ? (
                    <div className="rounded-[1.5rem] bg-surface/70 px-5 py-6 text-sm text-on-surface/55">Refreshing medication-aware meal guidance...</div>
                  ) : dietSupportError ? (
                    <div className="rounded-[1.5rem] bg-secondary-container/30 px-5 py-4 text-sm leading-7 text-secondary">{dietSupportError}</div>
                  ) : dietSupport ? (
                    <div className="space-y-4">
                      <div className="rounded-[1.5rem] bg-surface/80 px-5 py-5">
                        <p className="text-sm uppercase tracking-[0.18em] text-primary/70">Summary</p>
                        <p className="mt-3 text-sm leading-7 text-on-surface/68">{dietSupport.diet_plan.plan_summary}</p>
                      </div>
                      <div className="grid gap-3 sm:grid-cols-3">
                        {dietSupport.diet_plan.meal_rules.map((rule) => (
                          <div key={rule} className="rounded-[1.4rem] bg-surface/80 px-4 py-4 text-sm leading-7 text-on-surface/68">
                            {rule}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-secondary">
                    <CircleAlert className="h-4 w-4" />
                    <p className="text-sm font-medium">Foods to watch with this plan</p>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
                    {watchoutVisuals.map((item) => (
                      <div key={item.title} className="flex gap-3 rounded-[1.45rem] bg-surface/78 p-3">
                        <img src={item.image} alt={item.title} className="h-20 w-20 rounded-[1.1rem] object-cover" />
                        <div>
                          <p className="text-sm font-medium leading-6">{item.title}</p>
                          <p className="mt-1 text-xs leading-6 text-on-surface/58">{item.detail}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </SoftCard>

            <SoftCard className="space-y-5">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-secondary/75">Recipe generator</p>
                  <h3 className="mt-2 font-serif text-2xl">Build a safer meal path</h3>
                </div>
                <div className="rounded-full bg-secondary-container/30 p-3 text-secondary">
                  <Sparkles className="h-5 w-5" />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <label className="space-y-2">
                  <span className="text-sm font-medium text-on-surface/60">Meal type</span>
                  <select
                    value={generatorValues.mealType}
                    onChange={(e) => setGeneratorValues((current) => ({ ...current, mealType: e.target.value }))}
                    className="input-shell appearance-none"
                  >
                    <option value="any">Any</option>
                    <option value="breakfast">Breakfast</option>
                    <option value="lunch">Lunch</option>
                    <option value="dinner">Dinner</option>
                    <option value="snack">Snack</option>
                  </select>
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-on-surface/60">Dietary pattern</span>
                  <select
                    value={generatorValues.dietaryPattern}
                    onChange={(e) => setGeneratorValues((current) => ({ ...current, dietaryPattern: e.target.value }))}
                    className="input-shell appearance-none"
                  >
                    <option value="vegetarian">Vegetarian</option>
                    <option value="balanced">Balanced</option>
                    <option value="high-protein">High protein</option>
                    <option value="low-spice">Low spice</option>
                  </select>
                </label>

                <label className="space-y-2 md:col-span-2">
                  <span className="text-sm font-medium text-on-surface/60">Available ingredients</span>
                  <input
                    value={generatorValues.availableIngredients}
                    onChange={(e) => setGeneratorValues((current) => ({ ...current, availableIngredients: e.target.value }))}
                    className="input-shell"
                    placeholder="rava, cucumber, curd, beans"
                  />
                </label>

                <label className="space-y-2 md:col-span-2">
                  <span className="text-sm font-medium text-on-surface/60">Avoid ingredients</span>
                  <input
                    value={generatorValues.avoidIngredients}
                    onChange={(e) => setGeneratorValues((current) => ({ ...current, avoidIngredients: e.target.value }))}
                    className="input-shell"
                    placeholder="grapefruit, extra chilli"
                  />
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-on-surface/60">Cuisine preference</span>
                  <select
                    value={generatorValues.cuisinePreference}
                    onChange={(e) => setGeneratorValues((current) => ({ ...current, cuisinePreference: e.target.value }))}
                    className="input-shell appearance-none"
                  >
                    <option value="Any">Any</option>
                    <option value="South Indian">South Indian</option>
                    <option value="North Indian">North Indian</option>
                    <option value="Chinese">Chinese</option>
                    <option value="Italian">Italian</option>
                    <option value="Continental">Continental</option>
                  </select>
                </label>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-on-surface/60">Max cook minutes</span>
                  <input
                    type="number"
                    min={10}
                    max={60}
                    value={generatorValues.maxCookMinutes}
                    onChange={(e) => setGeneratorValues((current) => ({ ...current, maxCookMinutes: e.target.value }))}
                    className="input-shell"
                  />
                </label>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-4 rounded-[1.5rem] bg-surface-container-low px-5 py-4">
                <div>
                  <p className="text-sm font-medium text-on-surface/65">Servings</p>
                  <p className="text-xs text-on-surface/45">Scaled in the detail panel after you choose a recipe.</p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setGeneratorValues((current) => ({ ...current, servings: clampServings(current.servings - 1) }))}
                    className="river-stone-btn h-10 w-10 bg-surface text-on-surface/70"
                  >
                    -
                  </button>
                  <span className="min-w-8 text-center text-lg font-medium">{generatorValues.servings}</span>
                  <button
                    type="button"
                    onClick={() => setGeneratorValues((current) => ({ ...current, servings: clampServings(current.servings + 1) }))}
                    className="river-stone-btn h-10 w-10 bg-surface text-on-surface/70"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={handleRecipeGenerate}
                  className="river-stone-btn bg-gradient-to-br from-secondary to-secondary-container px-6 py-4 text-on-secondary-container"
                >
                  {generatedState.status === 'loading' ? 'Generating...' : 'Generate recipes'}
                </button>
                <div className="rounded-[1.5rem] bg-surface-container-low px-4 py-3 text-sm text-on-surface/58">
                  Up to 3 medication-aware recipes with ingredients, instructions, and visible safety notes.
                </div>
              </div>
            </SoftCard>

            <SoftCard className="space-y-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-primary/75">Generated recipes</p>
                  <h3 className="mt-2 font-serif text-2xl">Recipe suggestions first</h3>
                </div>
                {generatedState.status === 'success' && generatedState.fallbackUsed ? <Pill tone="terracotta">Fallback used</Pill> : null}
              </div>

              {generatedState.status === 'idle' ? (
                <div className="rounded-[1.5rem] bg-surface-container-low px-5 py-6 text-sm leading-7 text-on-surface/60">
                  Start with the controls above and this area will show up to three generated recipe ideas before the curated library.
                </div>
              ) : null}

              {generatedState.status === 'loading' ? (
                <div className="rounded-[1.5rem] bg-surface-container-low px-5 py-6 text-sm leading-7 text-on-surface/60">
                  Generating a medication-aware set of recipes with structured ingredients and safety notes...
                </div>
              ) : null}

              {generatedState.status === 'error' ? (
                <div className="rounded-[1.5rem] bg-secondary-container/25 px-5 py-5 text-sm leading-7 text-secondary">{generatedState.message}</div>
              ) : null}

              {generatedState.status === 'success' ? (
                <div className="space-y-4">
                  <div className="rounded-[1.5rem] bg-primary-fixed/22 px-5 py-4 text-sm leading-7 text-on-surface/68">
                    {generatedState.safetySummary}
                  </div>
                  <div className="grid gap-4 lg:grid-cols-2">
                    {generatedState.recipes.map((recipe) => (
                      <RecipeCard
                        key={recipe.recipe_id}
                        recipe={recipe}
                        selected={selectedRecipe?.recipe_id === recipe.recipe_id}
                        onSelect={setSelectedRecipe}
                        label={generatedState.fallbackUsed ? 'fallback' : 'generated'}
                      />
                    ))}
                  </div>
                </div>
              ) : null}
            </SoftCard>

            <SoftCard className="space-y-5 bg-surface-container-low">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-tertiary/75">Curated recipes</p>
                  <h3 className="mt-2 font-serif text-2xl">Always-available fallback library</h3>
                </div>
                <Pill tone="sand">{curatedRecipes.length || 0} recipes</Pill>
              </div>

              {curatedLoading ? (
                <div className="rounded-[1.5rem] bg-surface px-5 py-6 text-sm text-on-surface/58">Loading curated recipes...</div>
              ) : curatedError ? (
                <div className="rounded-[1.5rem] bg-secondary-container/25 px-5 py-5 text-sm leading-7 text-secondary">{curatedError}</div>
              ) : (
                <div className="grid gap-4 lg:grid-cols-2">
                  {curatedRecipes.map((recipe) => (
                    <RecipeCard
                      key={recipe.recipe_id}
                      recipe={recipe}
                      selected={!hasGeneratedRecipes && selectedRecipe?.recipe_id === recipe.recipe_id}
                      onSelect={setSelectedRecipe}
                      label="curated"
                    />
                  ))}
                </div>
              )}
            </SoftCard>
          </div>

          <div className="space-y-6">
            <SoftCard className="sticky top-6 space-y-5 bg-[linear-gradient(180deg,rgba(252,250,238,0.98),rgba(246,244,232,0.96))]">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-primary/75">Recipe detail</p>
                  <h3 className="mt-2 font-serif text-2xl">Inspect and scale</h3>
                </div>
                {selectedRecipe ? <Pill tone={selectedRecipe.source === 'generated' ? 'sage' : 'sand'}>{selectedRecipe.source}</Pill> : null}
              </div>

              {selectedRecipe ? (
                <div className="space-y-5">
                  <div className="overflow-hidden rounded-[1.8rem] bg-surface-container-high">
                    {selectedRecipe.image_url ? (
                      <img src={selectedRecipe.image_url} alt={selectedRecipe.title} className="h-64 w-full object-cover" />
                    ) : (
                      <div className="flex h-64 items-center justify-center text-on-surface/30">
                        <ImageOff className="h-10 w-10" />
                      </div>
                    )}
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h4 className="font-serif text-[1.9rem] leading-10">{selectedRecipe.title}</h4>
                        <p className="mt-2 text-sm leading-7 text-on-surface/62">{selectedRecipe.description}</p>
                      </div>
                      <span className="shrink-0 rounded-full bg-surface px-3 py-1.5 text-sm text-on-surface/50">
                        {selectedRecipe.cook_time}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {selectedRecipe.meal_type ? <Pill>{selectedRecipe.meal_type}</Pill> : null}
                      {selectedRecipe.dietary_pattern ? <Pill tone="sand">{selectedRecipe.dietary_pattern}</Pill> : null}
                      {selectedRecipe.cuisine_preference ? <Pill tone="sage">{selectedRecipe.cuisine_preference}</Pill> : null}
                    </div>
                  </div>

                  <div className="rounded-[1.55rem] bg-primary-fixed/22 px-5 py-4">
                    <p className="text-sm uppercase tracking-[0.18em] text-primary/70">Why this recipe</p>
                    <p className="mt-2 text-sm leading-7 text-on-surface/68">{selectedRecipe.why_it_fits}</p>
                  </div>

                  <div className="flex items-center justify-between gap-4 rounded-[1.55rem] bg-surface px-5 py-4">
                    <div>
                      <p className="text-sm font-medium text-on-surface/68">Servings</p>
                      <p className="text-xs text-on-surface/45">Default: {selectedRecipe.default_servings}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <button
                        type="button"
                        onClick={() => setSelectedServings((current) => clampServings(current - 1))}
                        className="river-stone-btn h-10 w-10 bg-surface-container-low text-on-surface/70"
                      >
                        -
                      </button>
                      <span className="min-w-8 text-center text-lg font-medium">{selectedServings}</span>
                      <button
                        type="button"
                        onClick={() => setSelectedServings((current) => clampServings(current + 1))}
                        className="river-stone-btn h-10 w-10 bg-surface-container-low text-on-surface/70"
                      >
                        +
                      </button>
                    </div>
                  </div>

                  <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
                    <div className="space-y-3 rounded-[1.55rem] bg-surface px-5 py-5">
                      <p className="text-sm uppercase tracking-[0.18em] text-primary/70">Scaled ingredients</p>
                      <ul className="space-y-3 text-sm leading-7 text-on-surface/68">
                        {scaledIngredients.map((ingredient) => (
                          <li key={ingredient} className="rounded-[1rem] bg-surface-container-low px-3 py-2">
                            {ingredient}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="space-y-3 rounded-[1.55rem] bg-surface px-5 py-5">
                      <p className="text-sm uppercase tracking-[0.18em] text-primary/70">Instructions</p>
                      <ol className="space-y-3 text-sm leading-7 text-on-surface/68">
                        {selectedRecipe.instructions.map((step, index) => (
                          <li key={step} className="rounded-[1rem] bg-surface-container-low px-3 py-2">
                            <span className="font-medium text-primary">{index + 1}.</span> {step}
                          </li>
                        ))}
                      </ol>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <p className="text-sm uppercase tracking-[0.18em] text-secondary/70">Safety notes</p>
                    <div className="space-y-3">
                      {selectedRecipe.safety_notes.map((note) => (
                        <div
                          key={`${note.message}-${note.related_to ?? 'general'}`}
                          className={`rounded-[1.35rem] px-4 py-3 text-sm leading-7 ${
                            note.severity === 'caution'
                              ? 'bg-secondary-container/28 text-secondary'
                              : 'bg-surface text-on-surface/68'
                          }`}
                        >
                          {note.message}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-[1.35rem] bg-surface px-4 py-4">
                      <p className="text-sm uppercase tracking-[0.18em] text-primary/70">Condition fit</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {selectedRecipe.condition_fit.map((item) => (
                          <Pill key={item}>{item}</Pill>
                        ))}
                      </div>
                    </div>
                    <div className="rounded-[1.35rem] bg-surface px-4 py-4">
                      <p className="text-sm uppercase tracking-[0.18em] text-primary/70">Medication fit</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {selectedRecipe.medication_fit.map((item) => (
                          <Pill key={item} tone="sand">{item}</Pill>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <EmptyState title="Pick a recipe" description="Choose a generated or curated recipe card to inspect ingredients, safety notes, and serving scaling." />
              )}
            </SoftCard>
          </div>
        </div>
      </section>

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
