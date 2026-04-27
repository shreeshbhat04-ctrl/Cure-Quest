"""Vision Agent – auto-classifies and analyses uploaded medical images.

Uses the GeminiVisionService fallback chain (ImageClassifier → Gemini auto-detect)
and communicates results to Recipe Agent and Comms Agent via A2A AgentTool protocol.
Uploaded images are saved to Google Drive via the existing hierarchical adapter.
"""

from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from cure_quest.config import get_settings
from cure_quest.adk.recipe_agent import recipe_agent

settings = get_settings()


class VisionInput(BaseModel):
    image_description: str = Field(
        default="",
        description="Text description of the uploaded image, or the user's question about it.",
    )
    file_path: str = Field(
        default="",
        description="Local file path to the uploaded image (used for classification and Drive upload).",
    )
    patient_id: str = Field(
        default="",
        description="Patient identifier for hierarchical Drive folder routing.",
    )
    mime_type: str = Field(
        default="image/jpeg",
        description="MIME type of the uploaded image (image/jpeg, image/png, etc.).",
    )


vision_agent = LlmAgent(
    model=settings.adk_model,
    name="cure_quest_vision_agent",
    description=(
        "Analyses uploaded medical images (prescriptions, symptom photos, lab reports) "
        "using auto-classification with fallback. Saves to Drive and delegates to "
        "downstream agents (Recipe, Comms) via A2A."
    ),
    instruction=(
        "You are the Cure-Quest Vision Agent. Your role is to process uploaded medical images.\n\n"
        "WORKFLOW:\n"
        "1. CLASSIFY: When you receive an image, auto-classify it as PRESCRIPTION, SYMPTOM, or OTHER.\n"
        "   - Use the ImageClassifierService first (Gemini multimodal one-word classification).\n"
        "   - If that returns OTHER or fails, fall back to Gemini auto-detect (unified prompt).\n"
        "   - No user input about image type is required.\n\n"
        "2. ANALYZE: Based on classification:\n"
        "   - PRESCRIPTION → extract medication_name, dosage, instructions, findings.\n"
        "   - SYMPTOM → determine severity (Mild/Moderate/Severe/Critical), findings, summary.\n"
        "   - OTHER/AUTO → let the model decide the type and fill relevant fields.\n\n"
        "3. PHYSICAL ASSESSMENT: For medication packaging, perform a detailed physical inspection.\n"
        "   - Count the number of tablets present vs. consumed in blister packs.\n"
        "   - Estimate the percentage of ointment left in tubes.\n"
        "   - Identify container types (Blister Pack, Tube, Bottle, etc.) and their usage state.\n\n"
        "4. SAVE TO DRIVE: Upload the image to Google Drive using the hierarchical folder structure:\n"
        "   CureQuest/Doctor-{name}/Patient-{name}/{Category}/\n"
        "   where Category is Prescriptions, Symptoms, or Other.\n\n"
        "5. DELEGATE:\n"
        "   - If the analysis shows diet_relevant=true OR the prescription contains\n"
        "     diet-sensitive medications (Warfarin, Metformin, blood thinners, etc.),\n"
        "     delegate to **cure_quest_recipe_agent** for safe meal planning.\n"
        "   - Always provide a patient-friendly summary of your findings.\n"
        "   - If severity is Severe or Critical, flag for clinician escalation.\n\n"
        "6. RESPOND: Return a clear, structured summary including:\n"
        "   - What type of image was detected\n"
        "   - Key findings (including physical state tally like tablets consumed/present)\n"
        "   - Drive upload status\n"
        "   - Any downstream agent actions taken\n"
    ),
    input_schema=VisionInput,
    tools=[
        AgentTool(agent=recipe_agent),
    ],
)
