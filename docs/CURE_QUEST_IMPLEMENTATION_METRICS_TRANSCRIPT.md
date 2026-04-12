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

# Cure-Quest Conversation Transcript

## Shreesha

> *(Shared document: "Optimization, Distillation, and Multi-Agent Adaptation of MedGemma for the Cure-Quest Clinical Architecture")*
>
> thoughts?

## Claude

This is a solid technical writeup — well-structured, covers the right territory, and the MedGemma + QLoRA + LoRAX stack is genuinely the right call for constrained hardware. A few honest thoughts:

**What's strong:**

The GQA explanation is accurate and relevant. The hardware footprint table is practically useful. The LoRAX dynamic adapter swapping section is the most insightful part — that's a real solution to the multi-model-on-single-GPU problem that most people overlook. The distillation inheritance argument (4B student getting 27B teacher's reasoning via KL divergence) is correctly framed.

**Where it's weak or overclaims:**

The pruning dismissal is too sweeping. Saying structured pruning "often leads to severe and catastrophic degradation" is an overstatement — SparseGPT and Wanda show you can prune 50%+ of weights with minimal perplexity loss on modern architectures.

The three-agent split (Pharmacovigilance / Dietetic / Diagnostic) is described cleanly but the actual inter-agent communication protocol is hand-waved. "Passing contextual variables and intermediate deductions" — how? Shared memory buffer? Structured JSON schema? This is where Cure-Quest's actual ADK implementation would need to be concrete.

The hallucination mitigation section is generic. For a medical system specifically, you'd want to name RAG-with-citation-grounding or constrained decoding as concrete mechanisms, not just monitoring.

The dataset analysis section treats the Kaggle Indian Medicine dataset as production-grade clinical data, which it isn't.

**One missing piece:**

No mention of HITL integration at the model output layer. For Cure-Quest specifically, since you're using Asana MCP for doctor approval workflows, there should be a section on how model confidence scores or uncertainty estimates gate when a human review is triggered vs. when output goes direct.

Overall it reads like a strong literature-informed design doc, but the gaps between described components and actual implementation are where the real engineering work lives.

## Shreesha

yeh can u give me the timeline and workflow on developing adapter or distillation for my project

## Claude

*(Asked clarifying questions — current ML state, target hardware, deadline)*

**Answers received:**
- ML state: MedGemma running via HF token only
- Target hardware: Kaggle (T4/P100) and Google Colab
- Deadline: 1–2 weeks

**Recommendation: skip full distillation, go straight to QLoRA adapters.**

Distillation needs a 27B teacher running in parallel — that's a separate GPU job you don't have time or hardware budget for. The 4B model already inherits the 27B's distilled knowledge.

**4-Phase Timeline (14 days):**

**Phase 1 — Baseline & data prep (Days 1–3)**
- Run MedGemma 4B zero-shot on ~50 sample queries per domain
- Score outputs manually — this is your baseline floor
- Clean Indian Medicine CSV and Drug-Food CSV

**Phase 2 — Dataset conversion & SFT format (Days 4–6)**
- CSV row → Gemma chat template format
- Target: ~3–5K examples per agent
- 80/10/10 train/val/test split, save as .jsonl

**Phase 3 — QLoRA training per agent (Days 7–11)**
- Load MedGemma 4B in NF4 via BitsAndBytes + Unsloth
- LoRA config: rank=16, alpha=32, target q/k/v/o_proj
- Train 3 separate adapters, ~1–2 epochs each
- Save each adapter (~80–120 MB)

**Phase 4 — Integration & HITL hookup (Days 12–14)**
- Wire adapters into ADK via PEFT
- Hook Asana MCP HITL for low-confidence outputs

## Shreesha

yeh main point issue is that like medsigslip running locally should not be drag so is the current plan take in to consideration about that

## Claude

*(Asked clarifying questions — what the concern was, and centrality of image input)*

**Answers received:**
- Concern: MedSigLIP runs cheaply locally — want same for MedGemma
- Image input: core feature — users upload medical images

**Core answer:** MedSigLIP at ~1.6 GB and MedGemma 4B NF4 at ~2.8 GB together sit at ~4.4 GB on the T4 — leaving over 11 GB free. Both are permanently resident, no swapping needed.

**VRAM Budget on T4 (16 GB total):**
- MedSigLIP: ~1.6 GB (400M params, FP16)
- MedGemma 4B NF4: ~2.8 GB
- Remaining: ~11.6 GB free

**Critical note:** Load the full multimodal checkpoint (`google/medgemma-4b-it`), NOT the text-only variant. If you train on text-only and bolt vision on later, adapter weights won't generalize to image-conditioned inputs.

## Shreesha

so keeping this in mind and the core essential features such as diet, side effects, everything i really want to quantify it. So redraw the timeline and workflow

## Claude

**Revised 14-day timeline with multimodal integration and per-feature quantification:**

**Phase 1 — Multimodal baseline & data audit (Days 1–3)**
- Day 1: Load `medgemma-4b-it` (multimodal). Zero-shot: 20 diet, 20 side-effect, 5 image queries
- Day 2: Score outputs. Audit Indian Medicine CSV
- Day 3: Audit Drug-Food CSV. These numbers set SFT target volume per adapter

**Phase 2 — SFT dataset construction, all 3 agents (Days 4–6)**
- Day 4: Pharmacovigilance dataset — target 3–4K rows
- Day 5: Dietetic dataset + synthetic augmentation via MedGemma 27B HF API. Diagnostic dataset with image caption fields
- Day 6: 80/10/10 split all three .jsonl files, validate token length (<2048 tok)

**Phase 3 — QLoRA training, 3 adapters sequentially (Days 7–11)**
- Days 7–8: Pharmacovigilance adapter — 2 epochs, lr=2e-4, batch=4
- Day 9: Dietetic adapter
- Day 10: Diagnostic adapter — include image-text paired examples
- Day 11: Eval all 3 vs baseline. Save adapter files

**Phase 4 — ADK integration, HITL hookup, demo prep (Days 12–14)**
- Day 12: Wire adapters into ADK via PEFT
- Day 13: Asana MCP HITL — logprob <0.7 → doctor review task
- Day 14: End-to-end demo — image upload → MedSigLIP → diagnostic adapter → HITL if flagged

**Per-feature quantification targets:**

| Feature | Adapter | Zero-shot baseline | Post-adapter target |
|---|---|---|---|
| Side effect identification | Pharmacovigilance | ~45–55% exact match | >78% exact match, hallucination <8% |
| Diet recommendations | Dietetic | ~40% correct interaction flags | >75% correct flags, 0 false-safe outputs |
| Symptom deduction | Diagnostic | ~50% top-1 correct | >72% top-1, >90% top-3 correct |
| Image grounding | Diagnostic | Image ignored/weakly cited | Explicitly cited in >80% of responses |
| HITL confidence gate | All 3 | No gate | logprob <0.7 → Asana task fired |

## Shreesha

okay so how much reduction in running the model hypothetically

## Claude

**VRAM reduction:**

| Config | VRAM | Reduction |
|---|---|---|
| FP16 raw | 8.0 GB | baseline |
| INT8 | 4.0 GB | 50% |
| NF4 (your config) | 2.5 GB | 69% |
| NF4 + MedSigLIP | 4.1 GB | full multimodal stack |
| NF4 + 3 adapters | 4.4 GB | full Cure-Quest stack |

**Training memory:**

| Config | Memory |
|---|---|
| Full fine-tune FP16 | ~64 GB |
| QLoRA rank=16 | ~6.5 GB |
| Trainable params | ~6.5M (0.16% of model) |
| Training reduction | ~90% vs full fine-tune |

**Inference speed on T4:**

| Config | Tokens/sec |
|---|---|
| FP16 baseline | ~22 tok/s |
| INT8 | ~38 tok/s |
| NF4 + Unsloth | ~52 tok/s (~2.4× faster) |

## Shreesha

dont need to take into consideration running two models concurrently now but okay good one

## Claude

Got it — MedSigLIP and MedGemma are sequential, not concurrent.

**Sequential pipeline:**
```
image → MedSigLIP encode (1.6 GB peak, ~50ms) → embedding → MedGemma NF4 decode (2.5 GB peak, ~200–400ms)
```

True peak VRAM is ~2.5 GB, not 4.1 GB — the 4.1 GB figure was a conservative concurrent-load estimate. MedSigLIP stays frozen so you don't even load it during QLoRA training — only at inference time for the diagnostic agent path. Effective working VRAM budget: under 4 GB at any point, ~12 GB free for KV cache and long context.

## Shreesha

What are the exact deliverables for Phase 1 of Cure-Quest?

## Claude

**Phase 1 deliverables with acceptance criteria:**

### Day 1 — Model load + zero-shot eval

1. **Load `google/medgemma-4b-it` via HF token**
   - Done when: loads without OOM on Kaggle P100
   - Verify: `model.config.model_type == gemma3`
   - Must be multimodal checkpoint, not text-only

2. **Run 20 side-effect queries zero-shot**
   - Done when: logged in CSV with columns: query, response, correct_drug, model_identified_drug, exact_match (0/1), hallucination_flag (0/1)

3. **Run 20 diet/interaction queries zero-shot**
   - Same CSV structure
   - Flag false-safe outputs — model says "no interaction" but ground truth says otherwise. These are the critical failures.

4. **Run 5 image inputs through MedSigLIP → MedGemma**
   - Done when: pipeline runs end-to-end without error
   - Log whether image embedding was cited in response text
   - Use 2 chest X-rays, 2 derm images, 1 OCT scan

### Day 2 — Score baseline + Indian Medicine audit

5. **Baseline scorecard — 4 numbers**
   - Side-effect exact match %
   - Diet correct flag %
   - Hallucination rate %
   - Image cited in response %
   - These are your day-14 comparison anchors

6. **Indian Medicine CSV audit report**
   - Total rows, rows with non-null salt composition, rows with non-null side effects, unique drug classes, % usable without augmentation

### Day 3 — Drug-Food CSV audit + go/no-go

7. **Drug-Food CSV audit report**
   - Row count, null mechanism%, interaction type distribution (inhibition / induction / absorption)
   - If inhibition pairs < 500 rows → plan synthetic augmentation on Day 5

8. **SFT volume plan — one number per adapter**
   - Real rows + synthetic rows needed to hit 3K per adapter

9. **Go/no-go gate** *(most important deliverable)*
   - If zero-shot baseline already >70% on any feature → adapter ROI is low, narrow scope to weak feature
   - If image pipeline fails end-to-end → fix before Phase 2. Fix: add `"The following image features were extracted: {medsiglip_caption}. Use these in your reasoning."` to system prompt

## Shreesha

list all the conversation including mine in the markdown file

## Claude

*(Attempted to generate transcript — file creation was cut off)*

## Shreesha

yeh continue

## Claude

*(Completed and saved this full transcript)*
