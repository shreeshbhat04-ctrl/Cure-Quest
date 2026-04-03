from cure_quest.agents.intake import IntakeAgent
from cure_quest.api.models import ConditionInput, PatientIntakeRequest
from cure_quest.db.bootstrap import init_database
from cure_quest.db.session import SessionLocal


def main() -> None:
    init_database()
    payload = PatientIntakeRequest(
        full_name="Asha Rao",
        preferred_language="en",
        active_conditions=[
            ConditionInput(name="IBS", condition_type="chronic"),
            ConditionInput(name="Typhoid", condition_type="acute"),
        ],
    )
    with SessionLocal() as db:
        patient = IntakeAgent().intake_patient(db, payload)
        print("SEEDED_PATIENT_ID", patient.id)


if __name__ == "__main__":
    main()
