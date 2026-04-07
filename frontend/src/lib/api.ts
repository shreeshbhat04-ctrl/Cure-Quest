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

export async function fetchWorkspace(patientId: number) {
  return request<WorkspacePayload>(`/demo/patient/${patientId}/workspace`);
}

export interface DocumentUploadResponse {
  patient_id: number;
  file_id: string;
  file_name: string;
  web_view_link: string | null;
  prescription_id: number | null;
  image_category: string | null;
}

export async function uploadDocumentFile(patientId: number, file: File) {
  const formData = new FormData();
  formData.append('patient_id', patientId.toString());
  formData.append('file', file);

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

export async function checkAlternatives(patientId: number, unavailableMedication: string) {
  return request<AlternativeResponse>('/patient/check-alternatives', {
    method: 'POST',
    body: JSON.stringify({ patient_id: patientId, unavailable_medication: unavailableMedication }),
  });
}

export async function fetchDietSupport(patientId: number, medicationName: string, locationQuery: string) {
  return request<DietSupportResponse>('/orchestration/diet-support', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      medication_name: medicationName,
      location_query: locationQuery,
    }),
  });
}

export async function fetchDrugLabel(medicationName: string) {
  return request<DrugLabelResponse>('/drug/label', {
    method: 'POST',
    body: JSON.stringify({ medication_name: medicationName }),
  });
}

export async function createEscalation(patientId: number, summary: string, pharmacyLocationQuery?: string) {
  return request<EscalationResponse>('/patient/escalate', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      case_type: 'doctor_review',
      summary,
      create_calendar_event: true,
      calendar_summary: 'Doctor review follow-up',
      pharmacy_location_query: pharmacyLocationQuery || null,
    }),
  });
}

export async function createCalendarEvent(patientId: number, summary: string) {
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

export interface ConversationResponse {
  patient_id: number;
  message: string;
  route_type: string;
  primary_model: string;
  reason: string;
  audio_base64?: string;
}

export async function sendVoiceNote(patientId: number, audioBlob: Blob) {
  const formData = new FormData();
  formData.append('patient_id', patientId.toString());
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

export async function sendTextMessage(patientId: number, message: string) {
  return request<ConversationResponse>('/orchestration/conversation-route', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      message,
    }),
  });
}

// --- HITL Comprehension ---

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

export async function fetchHITLComprehension(patientId: number) {
  return request<HITLComprehensionResponse>('/orchestration/hitl-comprehension', {
    method: 'POST',
    body: JSON.stringify({ patient_id: patientId }),
  });
}

// --- Reminders ---

export interface Reminder {
  id: number;
  medication_name: string;
  reminder_time: string;
  created_at: string;
}

export interface RemindersResponse {
  patient_id: number;
  reminders: Reminder[];
}

export async function fetchReminders(patientId: number) {
  return request<RemindersResponse>(`/patient/${patientId}/reminders`);
}

export async function saveReminder(patientId: number, medicationName: string, reminderTime: string) {
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
    throw new Error(text || `Failed to save reminder`);
  }

  return response.json();
}

// --- Google Auth ---

export interface GoogleAuthResponse {
  patient_id: number;
  name: string;
  email: string;
  google_connected: boolean;
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

export interface GoogleAuthStatus {
  patient_id: number;
  google_connected: boolean;
  email: string | null;
  services: { drive: boolean; calendar: boolean; gmail: boolean };
}

export async function checkGoogleAuthStatus(patientId: number) {
  return request<GoogleAuthStatus>(`/auth/google/status/${patientId}`);
}

// --- Gmail ---

export interface GmailEmail {
  id: string;
  subject: string;
  from: string;
  date: string;
  snippet: string;
}

export async function fetchHealthEmails(patientId: number) {
  return request<{ patient_id: number; emails: GmailEmail[]; error?: string }>(
    `/gmail/${patientId}/health-emails`
  );
}

export async function sendCareSummary(patientId: number, toEmail: string, subject: string, bodyHtml: string) {
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
