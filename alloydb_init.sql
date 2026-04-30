-- AlloyDB (PostgreSQL) Migration Script
-- Generated from cure_quest.db

BEGIN;

CREATE TABLE chat_messages (
	id SERIAL PRIMARY KEY, 
	thread_id INTEGER NOT NULL, 
	sender_role VARCHAR(40) NOT NULL, 
	sender_display_name VARCHAR(255) NOT NULL, 
	body TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(thread_id) REFERENCES chat_threads (id)
);
CREATE TABLE chat_threads (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	doctor_id INTEGER NOT NULL, 
	subject VARCHAR(500) NOT NULL, 
	status VARCHAR(40) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(patient_id) REFERENCES patients (id), 
	FOREIGN KEY(doctor_id) REFERENCES doctors (id)
);
CREATE TABLE chronic_conditions (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	condition_type VARCHAR(32) NOT NULL, 
	last_updated DATE, 
	notes TEXT, 
	FOREIGN KEY(patient_id) REFERENCES patients (id)
);
INSERT INTO "chronic_conditions" VALUES(1,2,'Atopic Eczema','chronic','2026-04-29','Moderate-severe atopic dermatitis. Recurrent flares on forearms, neck, and behind knees. Triggered by stress and weather changes. Currently managed with topical corticosteroids and emollients.');
INSERT INTO "chronic_conditions" VALUES(2,2,'Focal Epilepsy','chronic','2026-04-29','Focal onset seizures diagnosed at age 19. Last seizure 4 months ago. Well-controlled on Levetiracetam. EEG shows occasional focal epileptiform discharges in the left temporal lobe. No surgical intervention planned at this time.');
CREATE TABLE doctors (
	id SERIAL PRIMARY KEY, 
	full_name VARCHAR(255) NOT NULL, 
	specialty VARCHAR(255), 
	email VARCHAR(255), 
	phone VARCHAR(50), 
	asana_user_gid VARCHAR(255), 
	asana_workspace_gid VARCHAR(255), 
	profile_image_key VARCHAR(100), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
INSERT INTO "doctors" VALUES(1,'Dr surgeon','Gynacologist','sreeshhb@gmail.com',NULL,'1214276322986923','1213916290149152','surgeon','2026-04-28 19:22:38.395192');
CREATE TABLE escalation_cases (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	case_type VARCHAR(50) NOT NULL, 
	status VARCHAR(50) NOT NULL, 
	summary TEXT NOT NULL, 
	doctor_id INTEGER, 
	doctor_name VARCHAR(255), 
	doctor_email VARCHAR(255), 
	doctor_asana_gid VARCHAR(255), 
	urgency VARCHAR(50), 
	external_ticket_id VARCHAR(255), 
	external_ticket_url TEXT, 
	drive_file_id VARCHAR(255), 
	drive_file_url TEXT, 
	calendar_event_id VARCHAR(255), 
	calendar_event_url TEXT, 
	pharmacy_search_summary TEXT, 
	drive_path TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(patient_id) REFERENCES patients (id), 
	FOREIGN KEY(doctor_id) REFERENCES doctors (id)
);
CREATE TABLE medical_memories (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	source_type VARCHAR(50) NOT NULL, 
	source_reference VARCHAR(255), 
	modality VARCHAR(32) NOT NULL, 
	embedding_model VARCHAR(128) NOT NULL, 
	embedding_vector TEXT NOT NULL, 
	summary_text TEXT, 
	drive_file_id VARCHAR(255), 
	drive_file_url TEXT, 
	drive_path TEXT, 
	metadata_json TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(patient_id) REFERENCES patients (id)
);
CREATE TABLE medication_events (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	event_type VARCHAR(50) NOT NULL, 
	medication_name VARCHAR(255), 
	details TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(patient_id) REFERENCES patients (id)
);
CREATE TABLE notifications (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	channel VARCHAR(50) NOT NULL, 
	message_type VARCHAR(50) NOT NULL, 
	body TEXT NOT NULL, 
	delivery_status VARCHAR(50) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(patient_id) REFERENCES patients (id)
);
CREATE TABLE patient_condition_snapshots (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	snapshot_type VARCHAR(80) NOT NULL, 
	summary TEXT NOT NULL, 
	profile_json TEXT, 
	conditions_json TEXT, 
	prescriptions_json TEXT, 
	vitals_json TEXT, 
	source_event_type VARCHAR(80), 
	source_event_id VARCHAR(80), 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(patient_id) REFERENCES patients (id)
);
CREATE TABLE patient_doctor_map (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	doctor_id INTEGER NOT NULL, 
	relationship_type VARCHAR(50) NOT NULL, 
	is_default BOOLEAN NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(patient_id) REFERENCES patients (id), 
	FOREIGN KEY(doctor_id) REFERENCES doctors (id)
);
INSERT INTO "patient_doctor_map" VALUES(1,2,1,'primary',1,'Default doctor for Asana Care Approvals routing.','2026-04-28 19:22:38.400884');
CREATE TABLE patient_profile_details (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	height_cm FLOAT, 
	weight_kg FLOAT, 
	blood_group VARCHAR(20), 
	allergies_json TEXT, 
	emergency_contact_name VARCHAR(255), 
	emergency_contact_phone VARCHAR(50), 
	primary_language VARCHAR(50), 
	notes TEXT, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	UNIQUE (patient_id), 
	FOREIGN KEY(patient_id) REFERENCES patients (id)
);
CREATE TABLE patient_vitals (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	blood_pressure VARCHAR(50), 
	heart_rate_bpm INTEGER, 
	blood_glucose_mg_dl FLOAT, 
	temperature_c FLOAT, 
	weight_kg FLOAT, 
	source VARCHAR(80), 
	recorded_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(patient_id) REFERENCES patients (id)
);
CREATE TABLE patients (
	id SERIAL PRIMARY KEY, 
	full_name VARCHAR(255) NOT NULL, 
	preferred_language VARCHAR(50) NOT NULL, 
	date_of_birth DATE, 
	summary TEXT, 
	google_email VARCHAR(255), 
	google_access_token TEXT, 
	google_refresh_token TEXT, 
	google_token_expiry TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
INSERT INTO "patients" VALUES(2,'Shreesha','en','2002-04-04','22-year-old male managing chronic atopic eczema (moderate-severe, flare-prone on forearms and neck) and focal epilepsy (diagnosed age 19, currently controlled with anti-epileptic medication). Requires monitoring for drug interactions between dermatological corticosteroids and neurological treatments. Patient is tech-savvy and prefers digital communication for care coordination.','shreeshbhat04@gmail.com',NULL,NULL,NULL,'2026-04-28 19:22:38.380954');
CREATE TABLE pending_actions (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	action_type VARCHAR(80) NOT NULL, 
	status VARCHAR(40) NOT NULL, 
	draft_payload_json TEXT, 
	options_json TEXT, 
	selected_option_json TEXT, 
	result_json TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	confirmed_at TIMESTAMP WITH TIME ZONE, 
	FOREIGN KEY(patient_id) REFERENCES patients (id)
);
CREATE TABLE prescriptions (
	id SERIAL PRIMARY KEY, 
	patient_id INTEGER NOT NULL, 
	source_reference VARCHAR(255), 
	raw_text TEXT, 
	medication_name VARCHAR(255) NOT NULL, 
	dosage VARCHAR(100), 
	instructions TEXT, 
	confidence_score FLOAT NOT NULL, 
	review_status VARCHAR(50) NOT NULL, 
	document_drive_file_id VARCHAR(255), 
	document_drive_file_url TEXT, 
	drive_path TEXT, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	FOREIGN KEY(patient_id) REFERENCES patients (id)
);
INSERT INTO "prescriptions" VALUES(1,2,'eczema_prescription_scan.jpg','Apply Clobetasol Propionate 0.05% cream to affected areas twice daily for 14 days. Taper to once daily for 7 days. Use emollient liberally between applications.','Clobetasol Propionate 0.05% Cream','Apply twice daily (tapering)','Apply thin layer to eczema flare areas on forearms and neck. Avoid face and groin. Use emollient 30 min before corticosteroid. Review after 3 weeks.',0.92,'approved','1aQG7xEbVDFFkZOMrOTYsihooP51Yv_UY','https://drive.google.com/drive/folders/1aQG7xEbVDFFkZOMrOTYsihooP51Yv_UY',NULL,'2026-04-14 19:22:38.391756');
INSERT INTO "prescriptions" VALUES(2,2,'epilepsy_prescription_scan.jpg','Divalproex 500mg tablets. Take one tablet twice daily (morning and evening). Do not stop abruptly — taper under medical supervision.','Divalproex 500mg','500mg twice daily','Take with food to reduce GI side effects. Do not discontinue abruptly. Report mood changes, unusual bruising, or increased seizure frequency immediately.',0.95,'approved',NULL,NULL,NULL,'2026-03-29 19:22:38.391878');

COMMIT;
