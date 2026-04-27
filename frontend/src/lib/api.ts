import shaunImage from '../assets/Doctor/Shaun.png';
import strangeImage from '../assets/Doctor/Strange.png';
import surgeonImage from '../assets/Doctor/Surgeon.png';
import patient1Image from '../assets/Patient/Patient1.png';
import patient2Image from '../assets/Patient/Patient2.png';
import patient3Image from '../assets/Patient/Patient3.png';
import patient4Image from '../assets/Patient/Patient4.png';
import coffeeImage from '../assets/Coffee.png';
import curdRiceImage from '../assets/Curd_rice.png';
import dairyProductsImage from '../assets/dairy_products.png';
import highSugarImage from '../assets/High_sugar_contents.png';
import jowarDosaImage from '../assets/Jowar_dosa.png';
import ragiDosaImage from '../assets/Ragi_dosa.png';
import spicyChickenImage from '../assets/Spicy_chicken.png';
import upmaImage from '../assets/upma.png';

export {
  shaunImage,
  strangeImage,
  surgeonImage,
  patient1Image,
  patient2Image,
  patient3Image,
  patient4Image,
  coffeeImage,
  curdRiceImage,
  dairyProductsImage,
  highSugarImage,
  jowarDosaImage,
  ragiDosaImage,
  spicyChickenImage,
  upmaImage,
};


export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';
export const DEMO_PATIENT_ID = Number(import.meta.env.VITE_DEMO_PATIENT_ID ?? '2');

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export interface WorkspacePayload {
  patient: {
    id: number;
    full_name: string;
    preferred_language: string;
    summary: string | null;
    date_of_birth: string | null;
  };
  conditions: Array<{
    id: number;
    name: string;
    condition_type: string;
    last_updated: string | null;
    notes: string | null;
  }>;
  prescriptions: Array<{
    id: number;
    medication_name: string;
    dosage: string | null;
    instructions: string | null;
    review_status: string;
    confidence_score: number;
    document_drive_file_url: string | null;
    created_at: string;
  }>;
  notifications: Array<{
    id: number;
    channel: string;
    message_type: string;
    body: string;
    delivery_status: string;
    created_at: string;
  }>;
  cases: Array<{
    id: number;
    case_type: string;
    status: string;
    summary: string;
    doctor_id: number | null;
    doctor_name: string | null;
    doctor_email: string | null;
    doctor_asana_gid: string | null;
    urgency: string | null;
    external_ticket_id: string | null;
    external_ticket_url: string | null;
    drive_file_url: string | null;
    calendar_event_url: string | null;
    pharmacy_search_summary: string | null;
    created_at: string;
  }>;
  memories: Array<{
    id: number;
    source_type: string;
    modality: string;
    embedding_model: string;
    summary_text: string | null;
    drive_file_url: string | null;
    created_at: string;
  }>;
  doctors: DoctorProfile[];
  checkin: {
    profile: Record<string, unknown> | null;
    conditions: Array<Record<string, unknown>>;
    routine_tasks: Array<{
      task_id: string;
      name: string;
      completed: boolean;
      due_on?: string | null;
      notes?: string | null;
      assignee_name?: string | null;
      assignee_gid?: string | null;
      permalink_url?: string | null;
    }>;
    message: string;
  };
  manifest: {
    patient_id: number;
    agent_manifest: Record<string, { primary_model: string; reason: string }>;
    trigger_manifest: Record<string, string>;
  };
}

export interface AlternativeResponse {
  patient_id: number;
  candidates: Array<{
    name: string;
    formulation_note: string;
    stock_status: string;
    safety_note: string;
  }>;
  escalation_required: boolean;
  safety_summary: string;
}

export interface DietSupportResponse {
  patient_id: number;
  conditions: Array<Record<string, unknown>>;
  diet_plan: {
    medication_name: string | null;
    meal_rules: string[];
    pharmacy_summary: string | null;
    plan_summary: string;
  };
  pharmacy_result: {
    provider: string;
    pharmacies: Array<Record<string, unknown>>;
  };
}

export interface RecipeIngredient {
  name: string;
  quantity: number;
  unit: string;
}

export interface DietRecipeSafetyNote {
  severity: 'info' | 'caution';
  message: string;
  related_to: string | null;
}

export interface DietRecipe {
  recipe_id: string;
  title: string;
  description: string;
  default_servings: number;
  cook_time: string;
  meal_type: string | null;
  ingredients: RecipeIngredient[];
  instructions: string[];
  safety_notes: DietRecipeSafetyNote[];
  condition_fit: string[];
  medication_fit: string[];
  avoid_flags: string[];
  why_it_fits: string;
  dietary_pattern: string | null;
  cuisine_preference: string | null;
  image_url: string | null;
  image_status: 'ready' | 'pending' | 'unavailable';
  source: 'curated' | 'generated';
}

export interface GenerateDietRecipesPayload {
  patient_id: number;
  medication_name?: string | null;
  meal_type: string;
  available_ingredients: string[];
  avoid_ingredients: string[];
  cuisine_preference?: string | null;
  dietary_pattern?: string | null;
  max_cook_minutes?: number | null;
  servings: number;
  count: number;
}

export interface GenerateDietRecipesResponse {
  patient_id: number;
  conditions: Array<Record<string, unknown>>;
  medication_name: string | null;
  recipes: DietRecipe[];
  fallback_used: boolean;
  safety_summary: string;
}

export interface DrugLabelResponse {
  medication_name: string;
  found: boolean;
  label: Record<string, unknown> | null;
}

export interface EscalationResponse {
  case_id: number;
  external_ticket_id: string | null;
  status: string;
  external_ticket_url: string | null;
  doctor_id: number | null;
  doctor_name: string | null;
  doctor_email: string | null;
  doctor_asana_gid: string | null;
  urgency: string | null;
  drive_file_id: string | null;
  drive_file_url: string | null;
  calendar_event_id: string | null;
  calendar_event_url: string | null;
  pharmacy_search_summary: string | null;
}

export interface CalendarEventResponse {
  patient_id: number;
  event_id: string;
  html_link: string | null;
  escalation_case_id: number | null;
}

export interface DocumentUploadResponse {
  patient_id: number;
  file_id: string;
  file_name: string;
  web_view_link: string | null;
  prescription_id: number | null;
  image_category: string | null;
  doctor_name?: string | null;
  patient_name?: string | null;
  document_type?: string | null;
  disease_name?: string | null;
  capture_date?: string | null;
  drive_path?: string | null;
}

export interface DocumentUploadMetadata {
  doctor_name?: string;
  patient_name?: string;
  document_type?: string;
  disease_name?: string;
  capture_date?: string;
  image_category?: 'PRESCRIPTION' | 'SYMPTOM' | 'OTHER';
  prescription_id?: number | null;
}

export interface ConversationResponse {
  patient_id: number;
  message: string;
  route_type: string;
  primary_model: string;
  reason: string;
  audio_base64?: string;
  action_id?: number;
  intent?: string;
  question?: string;
  options?: ActionOption[];
  allow_custom_input?: boolean;
  preview?: string;
}

export interface ActionOption {
  label: string;
  value: string;
  doctor_id?: number;
  doctor_email?: string;
}

export interface ActionDraftResponse {
  action_id: number;
  intent: string;
  question: string;
  options: ActionOption[];
  allow_custom_input: boolean;
  preview?: string;
}

export interface ActionConfirmResponse {
  action_id: number;
  status: string;
  result: Record<string, unknown>;
}

export interface PendingAction {
  action_id: number;
  patient_id: number;
  action_type: string;
  status: string;
  options: ActionOption[];
  selected_option: Record<string, unknown> | null;
  result: Record<string, unknown> | null;
  created_at: string;
  confirmed_at?: string | null;
}

export interface HITLCondition {
  name: string;
  type: string;
  last_updated: string | null;
  notes: string | null;
}

export interface HITLMedication {
  name: string;
  dosage: string | null;
  instructions: string | null;
  review_status: string;
  days_on_medication: number | null;
  confidence_score: number;
}

export interface HITLComprehensionResponse {
  patient_id: number;
  patient: { name: string; dob: string | null; summary: string | null };
  conditions: HITLCondition[];
  medications: HITLMedication[];
  ai_analysis: string;
}

export interface Reminder {
  id: number;
  medication_name: string;
  reminder_time: string;
  created_at: string;
}

export interface DoctorProfile {
  id: number;
  full_name: string;
  specialty: string | null;
  email: string | null;
  phone: string | null;
  asana_user_gid: string | null;
  asana_workspace_gid: string | null;
  profile_image_key: string | null;
  is_default: boolean;
  relationship_type: string | null;
}

export interface DoctorTask {
  task_id: string;
  name: string;
  completed: boolean;
  due_on?: string | null;
  notes?: string | null;
  assignee_name?: string | null;
  assignee_gid?: string | null;
  permalink_url?: string | null;
}

export interface RemindersResponse {
  patient_id: number;
  reminders: Reminder[];
}

export interface GoogleAuthResponse {
  patient_id: number;
  name: string;
  email: string;
  google_connected: boolean;
}

export interface GoogleAuthStatus {
  patient_id: number;
  google_connected: boolean;
  email: string | null;
  services: { drive: boolean; calendar: boolean; gmail: boolean };
}

export interface GmailEmail {
  id: string;
  subject: string;
  from: string;
  date: string;
  snippet: string;
}
// Backend parity note (2026-04-26):
// All endpoints used by this migrated frontend are currently available in
// Cure-Quest backend routes. Missing mock endpoints in backend: none.

export async function fetchWorkspace(patientId: number): Promise<WorkspacePayload> {
  return request<WorkspacePayload>(`/demo/patient/${patientId}/workspace`);
}

export async function uploadDocumentFile(
  patientId: number,
  file: File,
  metadata?: DocumentUploadMetadata,
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('patient_id', String(patientId));
  formData.append('file', file);

  if (metadata?.prescription_id !== undefined && metadata.prescription_id !== null) {
    formData.append('prescription_id', String(metadata.prescription_id));
  }
  if (metadata?.doctor_name) {
    formData.append('doctor_name', metadata.doctor_name);
  }
  if (metadata?.patient_name) {
    formData.append('patient_name', metadata.patient_name);
  }
  if (metadata?.document_type) {
    formData.append('document_type', metadata.document_type);
  }
  if (metadata?.disease_name) {
    formData.append('disease_name', metadata.disease_name);
  }
  if (metadata?.capture_date) {
    formData.append('capture_date', metadata.capture_date);
  }
  if (metadata?.image_category) {
    formData.append('image_category', metadata.image_category);
  }

  const response = await fetch(`${API_BASE_URL}/documents/upload-file`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Upload failed with status ${response.status}`);
  }

  return response.json() as Promise<DocumentUploadResponse>;
}

export async function checkAlternatives(patientId: number, unavailableMedication: string): Promise<AlternativeResponse> {
  return request<AlternativeResponse>('/patient/check-alternatives', {
    method: 'POST',
    body: JSON.stringify({ patient_id: patientId, unavailable_medication: unavailableMedication }),
  });
}

export async function fetchDietSupport(patientId: number, medicationName: string, locationQuery: string): Promise<DietSupportResponse> {
  return request<DietSupportResponse>('/orchestration/diet-support', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      medication_name: medicationName,
      location_query: locationQuery,
    }),
  });
}

export async function fetchDietRecipes(
  patientId?: number,
  medicationName?: string | null,
  mealType?: string | null,
): Promise<{ recipes: DietRecipe[] }> {
  const params = new URLSearchParams();

  if (patientId !== undefined) {
    params.set('patient_id', String(patientId));
  }
  if (medicationName) {
    params.set('medication_name', medicationName);
  }
  if (mealType) {
    params.set('meal_type', mealType);
  }

  const query = params.toString();
  const endpoint = query ? `/diet/recipes?${query}` : '/diet/recipes';
  return request<{ recipes: DietRecipe[] }>(endpoint);
}

export async function generateDietRecipes(payload: GenerateDietRecipesPayload): Promise<GenerateDietRecipesResponse> {
  return request<GenerateDietRecipesResponse>('/diet/recipes/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchDrugLabel(medicationName: string): Promise<DrugLabelResponse> {
  return request<DrugLabelResponse>('/drug/label', {
    method: 'POST',
    body: JSON.stringify({ medication_name: medicationName }),
  });
}

export async function createEscalation(
  patientId: number,
  summary: string,
  pharmacyLocationQuery?: string,
  doctorId?: number | null,
  urgency: string = 'high',
): Promise<EscalationResponse> {
  return request<EscalationResponse>('/patient/escalate', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      case_type: 'doctor_review',
      summary,
      doctor_id: doctorId ?? null,
      urgency,
      create_calendar_event: true,
      calendar_summary: 'Doctor review follow-up',
      pharmacy_location_query: pharmacyLocationQuery || null,
    }),
  });
}

export async function fetchDoctors(patientId: number): Promise<DoctorProfile[]> {
  return request<DoctorProfile[]>(`/doctors?patient_id=${patientId}`);
}

export async function fetchDoctorTasks(doctorId: number): Promise<DoctorTask[]> {
  return request<DoctorTask[]>(`/doctor-workspace/${doctorId}/tasks`);
}

export async function createCalendarEvent(patientId: number, summary: string): Promise<CalendarEventResponse> {
  return request<CalendarEventResponse>('/calendar/events', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      summary,
      minutes_from_now: 45,
      duration_minutes: 30,
    }),
  });
}

export async function sendVoiceNote(patientId: number, audioBlob: Blob): Promise<ConversationResponse> {
  const formData = new FormData();
  formData.append('patient_id', String(patientId));
  formData.append('audio', audioBlob, 'voice.webm');

  const response = await fetch(`${API_BASE_URL}/orchestration/voice-route`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<ConversationResponse>;
}

export async function sendTextMessage(patientId: number, message: string): Promise<ConversationResponse> {
  return request<ConversationResponse>('/orchestration/conversation-route', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      message,
    }),
  });
}

export async function draftAction(patientId: number, intent: string, message: string): Promise<ActionDraftResponse> {
  return request<ActionDraftResponse>('/orchestration/action-draft', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      intent,
      message,
    }),
  });
}

export async function confirmAction(
  actionId: number,
  selectedOption?: string,
  customInput?: string,
): Promise<ActionConfirmResponse> {
  return request<ActionConfirmResponse>('/orchestration/action-confirm', {
    method: 'POST',
    body: JSON.stringify({
      action_id: actionId,
      selected_option: selectedOption ?? null,
      custom_input: customInput ?? null,
    }),
  });
}

export async function fetchPendingActions(patientId: number): Promise<PendingAction[]> {
  return request<PendingAction[]>(`/patients/${patientId}/pending-actions`);
}

export async function fetchHITLComprehension(patientId: number): Promise<HITLComprehensionResponse> {
  return request<HITLComprehensionResponse>('/orchestration/hitl-comprehension', {
    method: 'POST',
    body: JSON.stringify({ patient_id: patientId }),
  });
}

export async function fetchReminders(patientId: number): Promise<RemindersResponse> {
  return request<RemindersResponse>(`/patient/${patientId}/reminders`);
}

export async function saveReminder(patientId: number, medicationName: string, reminderTime: string): Promise<unknown> {
  const formData = new FormData();
  formData.append('patient_id', patientId.toString());
  formData.append('medication_name', medicationName);
  formData.append('reminder_time', reminderTime);

  const response = await fetch(`${API_BASE_URL}/patient/reminders`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Failed to save reminder');
  }

  return response.json();
}

export async function exchangeGoogleAuth(code: string): Promise<GoogleAuthResponse> {
  const formData = new FormData();
  formData.append('code', code);
  const response = await fetch(`${API_BASE_URL}/auth/google`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Google auth failed');
  }
  return response.json();
}

export async function checkGoogleAuthStatus(patientId: number): Promise<GoogleAuthStatus> {
  return request<GoogleAuthStatus>(`/auth/google/status/${patientId}`);
}

export async function fetchHealthEmails(patientId: number): Promise<{ patient_id: number; emails: GmailEmail[]; error?: string }> {
  return request<{ patient_id: number; emails: GmailEmail[]; error?: string }>(
    `/gmail/${patientId}/health-emails`
  );
}

export async function sendCareSummary(patientId: number, toEmail: string, subject: string, bodyHtml: string): Promise<unknown> {
  const formData = new FormData();
  formData.append('patient_id', patientId.toString());
  formData.append('to_email', toEmail);
  formData.append('subject', subject);
  formData.append('body_html', bodyHtml);

  const response = await fetch(`${API_BASE_URL}/gmail/send-care-summary`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Failed to send email');
  }
  return response.json();
}

export interface SymptomAnalysisResult {
  patient_id: number;
  severity: string;
  confidence: number;
  findings: string[];
  summary: string;
  model_used: string;
  diagnostic_image_base64: string | null;
}

export interface PrescriptionAnalysisResult {
  patient_id: number;
  medication_name: string;
  dosage: string | null;
  instructions: string | null;
  confidence: number;
  findings: string[];
  summary: string;
  model_used: string;
}

export async function analyzeSymptomImage(patientId: number, file: File): Promise<SymptomAnalysisResult> {
  const formData = new FormData();
  formData.append('patient_id', String(patientId));
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/caremaze/analyze-symptom`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Symptom analysis failed: ${text}`);
  }

  return response.json();
}

export async function analyzePrescriptionImage(patientId: number, file: File): Promise<PrescriptionAnalysisResult> {
  const formData = new FormData();
  formData.append('patient_id', String(patientId));
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/caremaze/analyze-prescription`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Prescription analysis failed: ${text}`);
  }

  return response.json();
}
