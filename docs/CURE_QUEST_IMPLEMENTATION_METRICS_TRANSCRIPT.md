# Cure-Quest Implementation Highlights and Metrics

## Implementation Highlights

- Adopted **MedGemma 4B** as the core clinical model with a **QLoRA adapter-first** strategy for fast delivery on constrained hardware.
- Defined a **3-agent specialization workflow**:
  - Pharmacovigilance (side effects / medication safety)
  - Dietetic (drug-food interactions)
  - Diagnostic (symptom deduction with image-grounding path)
- Prioritized **HITL escalation** through Asana MCP with confidence-gated review routing.
- Established a **14-day phased execution plan** spanning baseline evaluation, dataset preparation, adapter training, and integration.

## Quantified Metrics (Hypothetical / Planning Targets)

### Memory + Runtime Metrics

| Configuration | Estimated VRAM | Reduction vs FP16 |
|---|---:|---:|
| FP16 raw | 8.0 GB | baseline |
| INT8 | 4.0 GB | 50% |
| NF4 (target config) | 2.5 GB | 69% |
| NF4 + MedSigLIP | 4.1 GB | full multimodal stack estimate |
| NF4 + 3 adapters | 4.4 GB | full Cure-Quest stack estimate |

### Training Footprint Metrics

| Metric | Estimate |
|---|---:|
| Full fine-tune FP16 memory | ~64 GB |
| QLoRA rank=16 memory | ~6.5 GB |
| Trainable params | ~6.5M (~0.16%) |
| Memory reduction vs full fine-tune | ~90% |

### Inference Throughput (T4, projected)

| Configuration | Estimated Tokens/sec |
|---|---:|
| FP16 baseline | ~22 tok/s |
| INT8 | ~38 tok/s |
| NF4 + Unsloth | ~52 tok/s (~2.4×) |

### Feature Accuracy Targets (Phase baseline → post-adapter)

| Feature | Adapter | Baseline (zero-shot) | Post-adapter target |
|---|---|---|---|
| Side effect identification | Pharmacovigilance | ~45–55% exact match | >78% exact match, hallucination <8% |
| Diet recommendations | Dietetic | ~40% correct interaction flags | >75% correct flags, 0 false-safe outputs |
| Symptom deduction | Diagnostic | ~50% top-1 correct | >72% top-1, >90% top-3 |
| Image grounding | Diagnostic | Image weakly cited | Explicitly cited in >80% responses |
| HITL confidence gate | All adapters | No gate | logprob <0.7 triggers Asana task |

---

# Conversation Content (Speaker-Neutral)

## 1) Design review of the MedGemma optimization writeup

- The writeup was considered strong on:
  - GQA explanation
  - hardware footprint framing
  - dynamic adapter swapping strategy
  - distillation inheritance framing
- Gaps identified:
  - pruning claim was too broad
  - inter-agent communication protocol needed concrete specification
  - hallucination mitigation needed concrete mechanisms (grounding/constraints)
  - dataset quality caveats were needed
  - HITL confidence gating needed to be explicitly defined in output workflow

## 2) Timeline/workflow request (adapters vs distillation)

Given constraints (HF-token-only setup, Kaggle/Colab hardware, 1–2 week timeline), the recommended approach was:

- Skip full distillation for now
- Execute **QLoRA adapter training** directly

Initial 14-day workflow:

- **Phase 1 (Days 1–3):** baseline evaluation + dataset cleaning
- **Phase 2 (Days 4–6):** SFT conversion + train/val/test split
- **Phase 3 (Days 7–11):** train 3 domain adapters
- **Phase 4 (Days 12–14):** ADK integration + HITL connection

## 3) Local performance concern for MedSigLIP/MedGemma

Concern captured: local model usage should remain lightweight.

Response content:

- Combined estimate with concurrent residency was within T4 limits
- Critical guidance: use the **multimodal** MedGemma checkpoint (`google/medgemma-4b-it`)

## 4) Revised timeline with quantified feature goals

A revised 14-day plan was produced with explicit multimodal and quantification focus:

- Baseline: side-effect, diet, and image-query benchmark set
- Dataset construction per adapter with augmentation trigger criteria
- Sequential QLoRA adapter training across the 3 domains
- ADK + HITL integration and end-to-end demo

Feature targets were defined for:

- side-effect exact match and hallucination
- diet interaction flag correctness and false-safe avoidance
- diagnostic top-1/top-3 quality
- image-grounding citation behavior
- confidence-gated HITL escalation (`logprob < 0.7`)

## 5) Hypothetical reduction metrics

Captured planning estimates included:

- VRAM reduction from FP16 to INT8/NF4
- QLoRA memory reduction vs full fine-tuning
- projected inference speedup on T4 with NF4 + Unsloth

## 6) Clarification on sequential execution (not concurrent models)

Updated interpretation:

- MedSigLIP and MedGemma are used sequentially in the image path
- Effective peak memory was reframed accordingly
- SigLIP/vision encoder remains frozen for adapter-training workflows

## 7) Exact Phase 1 deliverables requested

Detailed deliverables and acceptance criteria were outlined for Days 1–3:

- Model load validation on target hardware
- Zero-shot benchmark logging for side-effect and diet tasks
- Image pipeline smoke validation
- Baseline scorecard metrics
- Indian Medicine + Drug-Food data audit outputs
- SFT volume planning and go/no-go gating rules

## 8) Transcript export request

A request was made to include the full conversation in markdown, including user inputs, followed by a continuation request.

This document now preserves the conversation **content** in a neutral format and keeps the implementation metrics together in `docs/`.
