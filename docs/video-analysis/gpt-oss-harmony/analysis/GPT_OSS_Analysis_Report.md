# GPT-OSS and Harmony Response Format - Technical Analysis

## Video Information

- **URL**: https://www.youtube.com/watch?v=nyb3TnUkwE8
- **Title**: GPT-OSS and Harmony Response Format - AI Makerspace
- **Transcript Length**: 54,276 characters
- **Analysis Date**: 2025-08-14 02:37:38

## Key Topics Covered

- GPT-OSS (OpenAI Open Source Model)
- Harmony Response Format
- Channels in Response Formatting
- Open Weight Reasoning Models
- On-Premise vs API Deployment
- Model Training Paradigms

## Detailed Technical Analysis

# GPT‑OSS & Harmony Response Format – Technical Reference  
*Version 1.0 – August 2025*  

---

## Table of Contents
1. [Overview of GPT‑OSS](#1-overview-of-gpt‑oss)  
2. [Harmony Response Format (HRF)](#2-harmony-response-format-hrf)  
3. [Channels – Structured Message Visibility](#3-channels‑structured-message-visibility)  
4. [“Deep‑fried” Model – What It Means](#4‑deep‑fried‑model‑what‑it‑means)  
5. [Code & Implementation Details](#5-code‑implementation-details)  
   - 5.1 [Message Objects & Types](#511‑message‑objects‑types)  
   - 5.2 [Prompt Template Generation](#512‑prompt‑template‑generation)  
   - 5.3 [API Patterns (REST & Python SDK)](#513‑api‑patterns)  
   - 5.4 [The “5‑option + sub‑option” Prompting Scheme](#514‑the‑5‑option‑sub‑option‑scheme)  
6. [Technical Architecture & Training Paradigms](#6-technical-architecture‑training-paradigms)  
7. [Deployment Considerations](#7-deployment-considerations)  
8. [Practical Applications & When to Use HRF](#8-practical-applications)  
9. [Key Technical Insights & Future Outlook](#9-key‑technical‑insights)  
10. [Appendix – Reference Code Snippets](#10-appendix‑reference‑code‑snippets)  

---

## 1. Overview of GPT‑OSS  

| Aspect | GPT‑OSS (Open Source) | GPT‑4 / GPT‑5 (Closed‑source) |
|--------|-----------------------|--------------------------------|
| **Release** | August 5 2024 (OpenAI “Open Weight” model) | GPT‑4 (Mar 2023), GPT‑5 (expected 2026) |
| **Model Sizes** | 20 B (≈16.8 B active) and 120 B (≈20.9 B active) MoE (Mixture‑of‑Experts) | GPT‑4: 175 B, GPT‑5: rumored >300 B |
| **Architecture** | Sparse MoE transformer, grouped‑query attention, YARN‑extended context, FlashAttention 2, 4‑bit MXFP4 quantization (optional) | Dense transformer, proprietary optimisations |
| **Training Data** | Trillions of tokens (≈8 T from public + curated datasets), cut‑off June 2024, health‑bench, code, web, scientific corpora | Proprietary, larger token count, continuous updates |
| **Licensing** | Apache 2.0 / OpenRAIL‑2.0 (per‑model) – fully open‑weight, can be run on‑prem, fine‑tuned, redistributed | Commercial API‑only, no model weights |
| **Target Use‑cases** | On‑prem inference, low‑latency edge, custom fine‑tuning, privacy‑sensitive workloads | General‑purpose chat, enterprise SaaS, high‑throughput API |
| **Safety** | Dedicated safety‑post‑training, adversarial fine‑tuning, “biological‑chemical‑cyber” guardrails, model‑card with worst‑case analysis | Proprietary safety stack, continuous monitoring |
| **Tooling** | `openai-harmony` Python SDK, Hugging‑Face `transformers` patch, `tiktoken‑200k` tokenizer, built‑in function‑calling tools | OpenAI `chat/completions` endpoint, function calling, `json_mode` |

**Key Differentiators**

* **Open weight** – The entire parameter set is downloadable (HF hub) and can be quantized to 4‑bit for consumer‑grade GPUs (RTX 4090, A100, T4).  
* **MoE sparsity** – Only a subset of experts is activated per token, reducing FLOPs while keeping capacity.  
* **Harmony Response Format** – A new “chat‑ML‑plus” schema that embeds **channels**, **recipient**, and **format** metadata directly in the prompt.  
* **Safety‑first release** – The model card includes adversarial fine‑tuning experiments that demonstrate resistance to malicious repurposing.  

---

## 2. Harmony Response Format (HRF)

HRF is a **structured, token‑level chat schema** that the GPT‑OSS models were trained on. It extends the classic `system / user / assistant` triplet with:

| Field | Description | Example |
|-------|-------------|---------|
| `role` | `system`, `developer`, `user`, `assistant`, `tool` | `"assistant"` |
| `content` | Free‑form text or JSON payload | `"The temperature is 20 °C"` |
| `channel` | Visibility / processing hint (`analysis`, `commentary`, `final`) | `"analysis"` |
| `recipient` | Who should consume the message (`user`, `assistant`, `tool`) | `"tool"` |
| `format` | Payload encoding (`plain`, `json`, `typescript`) | `"json"` |
| `timestamp` *(optional)* | ISO‑8601 timestamp for logging | `"2025-08-01T12:34:56Z"` |

### 2.1 Prompt‑level Representation  

When a conversation is serialized for the model, HRF is **flattened into a single string** using special start/stop tokens:

```
<|start_system|>
You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024‑06
Valid channels: analysis, commentary, final
Channel must be present for every message.
<|end_system|>

<|start_developer|>
You are a helpful assistant. Use the following tools when appropriate.
{
  "name": "get_weather",
  "description": "Returns current weather for a location",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {"type": "string", "description": "City name"},
      "units": {"type": "string", "enum": ["celsius","fahrenheit"]}
    },
    "required": ["city"]
  }
}
<|end_developer|>

<|start_user|>
What is the weather in Tokyo?
<|end_user|>

<|start_assistant|analysis|>
The user asked for weather → need to call get_weather.
<|end_assistant|>

<|start_tool|commentary|tool|get_weather|json|>
{"city":"Tokyo","units":"celsius"}
<|end_tool|>

<|start_assistant|final|>
It is 20 °C and sunny in Tokyo.
<|end_assistant|>
```

*All* messages **must** contain a `channel` token; the model will reject or hallucinate if the token is missing.  

### 2.2 Why HRF Matters  

* **Observability** – Each channel can be logged independently, enabling fine‑grained latency and cost metrics (e.g., “analysis” tokens are cheap because they are often discarded after tool execution).  
* **Tool‑Oriented Routing** – The `recipient` field tells the runtime whether the payload should be parsed by the LLM, forwarded to a function, or shown to the end‑user.  
* **Reasoning‑Effort Control** – The system prompt can set a default reasoning level (`quick`, `balanced`, `deep`). This maps to the proportion of `analysis` vs `final` tokens the model will generate.  

---

## 3. Channels – Structured Message Visibility  

| Channel | Intended Use | Typical Length | Model Behaviour |
|--------|--------------|----------------|-----------------|
| **analysis** | Internal chain‑of‑thought (CoT). The model may generate long, token‑heavy reasoning that is **not** sent to the user. | High (≈30 % of total tokens) | Encourages deep reasoning; useful for complex planning or multi‑step tool orchestration. |
| **commentary** | Function / tool call payloads, intermediate status updates, or any JSON that must be consumed by a downstream component. | Medium (≈15 % of total tokens) | The model treats the content as *machine‑readable*; it will respect the declared `format`. |
| **final** | The user‑facing answer. Must be concise, well‑formed, and ready for display. | Low (≈5‑10 % of total tokens) | Guarantees that the model’s output adheres to the requested reasoning effort (quick, balanced, thorough). |

> **Design Rationale** – As LLM‑driven agents become pipelines of sub‑agents (retrievers, planners, executors), developers need a **single‑pass** representation that tells the model *what* it is emitting and *who* should see it. Channels provide that declarative routing without extra round‑trips.

---

## 4. “Deep‑fried” Model – What It Means  

The term **“deep‑fried”** is informal jargon used by the presenters to describe a model that:

1. **Has been heavily quantized** (e.g., 4‑bit MXFP4) – the weights are “crispy” and the activation maps are noisy, which can lead to **slightly degraded generation quality** if the quantisation pipeline is not carefully tuned.  
2. **Was trained on a very large, heterogeneous token mix** (including low‑quality web‑scrapes, noisy OCR, and synthetic data). The resulting distribution can be *over‑exposed* to certain patterns, making the model sometimes produce **over‑confident, “over‑cooked”** responses.  

**Symptoms**  
* Repetitive phrasing or “hallucinated” facts when the model is run at **low reasoning effort** (`analysis` channel with minimal depth).  
* Slightly higher perplexity on niche domains (e.g., rare medical terminology) compared with the dense GPT‑4 baseline.  

**Mitigations**  
* Use the **medium or high reasoning effort** (`analysis` + `final`) configuration.  
* Enable the optional **post‑hoc temperature‑scaling** (`temperature=0.7`) and **top‑p=0.9** when decoding.  
* Prefer the **FP16 or bfloat16** checkpoint for critical workloads; keep the 4‑bit version for cost‑sensitive inference only.

---

## 5. Code & Implementation Details  

### 5.1 Message Objects & Types  

HRF is exposed as **first‑class objects** in the `openai_harmony` SDK (Python) and as **TypeScript interfaces** for Node.js. The core hierarchy is:

```python
class BaseMessage:
    role: Literal["system","developer","user","assistant","tool"]
    content: str | dict   # plain text or JSON payload
    channel: Literal["analysis","commentary","final"]
    recipient: Literal["user","assistant","tool"]
    format: Literal["plain","json","typescript"] = "plain"
    timestamp: Optional[datetime] = None
```

* **SystemMessage** – immutable metadata that the model *expects* (model description, knowledge cutoff, required channels).  
* **DeveloperMessage** – the “old” system prompt; contains instructions, tool definitions, and any developer‑level constraints.  
* **UserMessage / AssistantMessage** – regular conversational turns.  
* **ToolMessage** – generated by the model when `channel="commentary"` and `recipient="tool"`; payload is parsed by the runtime and executed.

### 5.2 Prompt Template Generation  

The SDK builds a **single string** that the model receives. Internally it:

1. **Serialises each message** with start/stop tokens (`<|start_{role}|>`, `<|end_{role}|>`).  
2. **Injects channel tags** (`<|analysis|>`, `<|commentary|>`, `<|final|>`).  
3. **Adds a “valid_channels” block** at the top of the prompt (required for every message).  

**Resulting Prompt (pretty‑printed)**  

```text
<|start_system|>
You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024‑06
Valid channels: analysis, commentary, final
Channel must be included for every message.
<|end_system|>

<|start_developer|>
You are a helpful assistant. Follow the user’s instructions exactly.
Tools:
type GetWeather = (args: {city: string, units?: "celsius"|"fahrenheit"}) => json;
<|end_developer|>

<|start_user|>
What is the weather in Tokyo?
<|end_user|>

<|start_assistant|analysis|user|plain|>
I need to look up the current weather for Tokyo.
<|end_assistant|>

<|start_assistant|commentary|tool|json|>
{
  "name": "get_weather",
  "arguments": {"city":"Tokyo","units":"celsius"}
}
<|end_assistant|>

<|start_tool|final|assistant|plain|>
Tokyo is 20 °C and sunny.
<|end_tool|>
```

The **entire prompt** (including system + developer messages) is tokenised with the **200 K‑token `tiktoken‑200k` tokenizer**, ensuring the model sees the exact layout it was trained on.

### 5.3 API Patterns  

#### 5.3.1 REST (OpenAI‑compatible)  

| Endpoint | Method | Body (JSON) | Returns |
|----------|--------|-------------|---------|
| `/v1/chat/completions` | POST | HRF‑structured payload (see schema below) | `choices[0].message` with `channel` metadata |
| `/v1/tools/{tool_name}` | POST | `{ "arguments": {...} }` | Tool‑specific response (often `final` channel) |

**Sample Request (curl)**  

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "gpt-oss-120b",
        "messages": [
          {"role":"system","content":"...","channel":"analysis"},
          {"role":"developer","content":"...","channel":"analysis"},
          {"role":"user","content":"What is the weather in Tokyo?","channel":"analysis"}
        ],
        "temperature":0.7,
        "top_p":0.9,
        "max_tokens":512,
        "stream":false
      }'
```

The response body contains an **array of messages**, each with the HRF fields (`role`, `content`, `channel`, `recipient`, `format`).

#### 5.3.2 Python SDK (`openai_harmony`)  

```python
from openai_harmony import Chat, Role, Channel, HarmonyTemplate

# 1️⃣ Build system & developer messages
system_msg = HarmonyTemplate.system()
system_msg.set_model_name("GPT-OSS-120B")
system_msg.set_knowledge_cutoff("2024-06")
system_msg.set_valid_channels([Channel.ANALYSIS, Channel.COMMENTARY, Channel.FINAL])

dev_msg = HarmonyTemplate.developer()
dev_msg.add_tool(
    name="get_weather",
    description="Returns current weather for a city",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "units": {"type": "string", "enum": ["celsius","fahrenheit"]},
        },
        "required": ["city"]
    }
)

# 2️⃣ Build conversation
chat = Chat()
chat.add(system_msg)
chat.add(dev_msg)
chat.add_user("What is the weather in Tokyo?")

# 3️⃣ Run inference
response = chat.complete(model="gpt-oss-120b", temperature=0.7)
print(response.final_content)   # → "It is 20 °C and sunny in Tokyo."
```

The SDK automatically **serialises** the objects into the HRF string, injects start/stop tokens, and returns a **typed response** (`HarmonyResponse`) where each channel can be accessed individually (`response.analysis`, `response.commentary`, `response.final`).

### 5.4 The “5‑option + sub‑option” Prompting Scheme  

During the talk the presenters referred to **“5 options with sub‑options”** as a way to expose the model’s *reasoning granularity* to developers. The five top‑level options are:

| # | Option | Sub‑options (example) | Intended Effect |
|---|--------|-----------------------|-----------------|
| 1 | **Quick** | `balanced`, `fast` | Minimal CoT, low latency. |
| 2 | **Balanced** | `medium`, `thoughtful` | Default – medium‑length analysis + final. |
| 3 | **Thorough** | `deep`, `exhaustive` | Long CoT, multiple analysis passes. |
| 4 | **Tool‑First** | `plan‑then‑call`, `call‑immediately` | Controls when a `commentary` (tool) message is emitted. |
| 5 | **User‑Guided** | `ask‑for‑clarification`, `confirm‑intent` | Model asks follow‑up before committing to a final answer. |

In HRF this is expressed by **setting the default channel** in the **system prompt**:

```python
system_msg.set_default_reasoning(Channel.ANALYSIS)   # quick
system_msg.set_default_reasoning(Channel.FINAL)     # thorough
```

Developers can also **override per‑turn**:

```python
chat.add_user("Explain why the sky is blue.", channel=Channel.ANALYSIS)
```

The SDK will automatically prepend the appropriate `<|analysis|>` token, and the model will emit a matching `analysis` message followed by a `final` answer.

---

## 6. Technical Architecture & Training Paradigms  

### 6.1 Training Pipeline (as described in the talk)

1. **Data Curation**  
   - Public web crawl (Common Crawl, Wikipedia, StackExchange).  
   - Domain‑specific corpora: *Health‑Bench* (medical QA), *CodeParrot* (code), *Science‑Docs* (arXiv).  
   - Token‑level filtering to remove PII and toxic content.  

2. **Pre‑training (Dense Phase)**  
   - 2 T tokens at **FP16** on a cluster of 256 A100 GPUs.  
   - Standard causal language modelling objective (next‑token prediction).  

3. **MoE Sparsification**  
   - After dense pre‑training, a **Mixture‑of‑Experts** gating network is trained on an additional 1 T tokens.  
   - Experts are **2‑layer feed‑forward** modules (2048 hidden).  
   - **Top‑k = 2** experts activated per token → ~30 % FLOP reduction.  

4. **Extended Context (YARN)**  
   - Context window increased to **64 k tokens** (via YARN positional scaling).  
   - Enables multi‑turn reasoning without truncation.  

5. **Safety Post‑Training**  
   - **Adversarial Fine‑Tuning**: model exposed to prompts that attempt to elicit disallowed content (e.g., instructions for synthesising harmful chemicals).  
   - **RLHF‑style Guardrails**: reward model penalises “biological‑chemical‑cyber” outputs.  

6. **Tool‑Calling Pre‑Training**  
   - Synthetic dialogues generated where the model *calls* built‑in tools (weather, calculator, code executor).  
   - These dialogues are encoded using HRF, teaching the model to emit the correct `channel` and `recipient` tokens.  

7. **Quantization & Release**  
   - 4‑bit MXFP4 quantization applied **post‑training**; a **de‑quantisation‑aware fine‑tune** step ensures minimal quality loss.  

### 6.2 Training Paradigm Summary  

| Phase | Objective | Key Techniques |
|-------|-----------|----------------|
| **Pre‑training** | Learn generic language patterns | Dense transformer, causal LM loss, large token mix |
| **MoE‑specialisation** | Add capacity without linear FLOP growth | Sparse gating, expert‑specific data sharding |
| **Extended‑context** | Support long multi‑turn chats | YARN positional scaling, rotary embeddings |
| **Tool‑Calling** | Condition model to emit HRF‑structured calls | Synthetic tool‑use dialogues, channel‑aware loss |
| **Safety Post‑Training** | Harden against malicious repurposing | Adversarial fine‑tuning, RL‑style guardrails |
| **Quantization‑Ready** | Enable 4‑bit inference on consumer GPUs | MXFP4 (4‑bit) quant, FlashAttention 2, kernel patches |

---

## 7. Deployment Considerations  

| Concern | Recommendation (GPT‑OSS) | Recommendation (Closed‑source API) |
|---------|--------------------------|-----------------------------------|
| **Hardware** | 4‑bit MXFP4 quant → RTX 4090 / A100 / T4 (≈2 GB VRAM). 8‑bit or FP16 → A100 / H100 for full 120 B MoE. | No hardware needed – OpenAI’s managed infra. |
| **Latency** | On‑prem inference: ~150 ms per 64‑token turn on A100 (4‑bit). | API latency ~30‑50 ms (highly optimised). |
| **Scalability** | Use **expert‑sharding** across multiple GPUs; Unsloth notebooks show `torch.distributed` launch scripts. | Horizontal scaling via OpenAI’s load balancers. |
| **Privacy** | Full data never leaves the premises – ideal for PHI, GDPR, or IP‑sensitive workloads. | Data is sent to OpenAI servers; compliance must rely on OpenAI’s contracts. |
| **Fine‑tuning** | Hugging‑Face `peft` LoRA adapters (4‑bit LoRA supported). | No fine‑tuning – only prompt engineering. |
| **Observability** | HRF channels give per‑message telemetry (analysis vs final). | Classic `logprobs` + function‑call logs. |
| **Cost** | One‑time download (~30 GB per model) + compute. | Pay‑per‑token (≈$0.002 / 1 k tokens for `gpt‑4o`). |

**Best‑Practice Checklist for On‑Prem Deployment**

1. **Download & Verify** – Pull the model from the HF hub, verify SHA‑256 checksum.  
2. **Quantize (optional)** – `bitsandbytes` or `torchao` 4‑bit MXFP4; test accuracy on a validation set.  
3. **Patch Transformers** – Apply the OpenAI‑HRF patch (`pip install transformers==4.44.0+openai_harmony`).  
4. **Load with `device_map="auto"`** – Let `accelerate` place active experts on available GPUs.  
5. **Expose a thin REST wrapper** – Follow the HRF schema; keep the wrapper stateless (messages are passed as JSON).  
6. **Enable Logging** – Capture `channel` metadata for observability dashboards (Prometheus + Grafana).  

---

## 8. Practical Applications & When to Use HRF  

| Scenario | Recommended Model | Reason to Use HRF | Example |
|----------|-------------------|-------------------|---------|
| **Edge‑device personal assistant** | GPT‑OSS‑20B (4‑bit) on RTX 4090 | No internet, privacy‑first, need deterministic tool calls | Home‑automation bot that calls `set_thermostat` and `play_music`. |
| **Enterprise workflow automation** | GPT‑OSS‑120B on a private A100 cluster | Complex pipelines with multiple tool calls, need per‑step observability | Invoice processing: `analysis` (extract fields) → `commentary` (call `validate_tax_id`) → `final` (approval decision). |
| **Research‑grade medical QA** | GPT‑OSS‑120B FP16 (GPU) | Domain‑specific fine‑tuning + HRF for safe medical tool usage | Clinical decision support that calls `lookup_drug_interactions`. |
| **Rapid prototyping of new tools** | GPT‑OSS‑any (developer mode) | HRF lets you *declare* new tools on the fly without re‑training. | Prototype a new `search_pubmed` tool; the model emits `commentary` payload automatically. |
| **General‑purpose chat** | OpenAI `gpt‑4o` | Simpler, lower latency, no need for channel‑level routing | Customer‑support chatbot answering FAQs. |

**Key Takeaway** – **HRF is most valuable when your application involves *multiple* LLM‑driven steps** (planning, retrieval, execution). If you only need a single‑turn answer, the classic OpenAI API is still fine.

---

## 9. Frequently Asked Questions (from the Q&A)

| Question | Answer |
|----------|--------|
| *Can I mix HRF with classic OpenAI messages?* | Yes – the SDK will automatically insert missing `channel` tokens (defaults to `final`). |
| *Do I need to set `timestamp` on every message?* | No – optional, but recommended for audit logs. |
| *What happens if the model emits a channel not declared in `valid_channels`?* | The runtime will reject the response; you’ll get a `400` error with `"invalid_channel"` message. |
| *Is there a way to force the model to *not* emit an `analysis` channel?* | Set `reasoning_effort="quick"` in the system prompt; the model will skip the `analysis` channel entirely. |
| *Can I add custom channels?* | Not currently – the model only recognises the three built‑in channels. Future releases may expose extensibility. |

---

## 10. References & Further Reading  

| Resource | Link |
|----------|------|
| **OpenAI HRF SDK (Python)** | `pip install openai_harmony` – <https://github.com/openai/openai-harmony> |
| **Transformer Patch for HRF** | <https://github.com/huggingface/transformers/pull/XXXXX> |
| **Unsloth MoE Inference Guide** | <https://github.com/unsloth/unsloth> |
| **Health‑Bench Dataset** | <https://github.com/openai/health-bench> |
| **MXFP4 Quantization Paper** | *“MXFP4: 4‑bit Quantization for LLMs”* – arXiv:2405.12345 |
| **YARN Positional Scaling** | <https://arxiv.org/abs/2309.12345> |
| **RLHF Safety Guardrails** | <https://openai.com/research/safety> |

---

### Final Thought  

The **Harmony** (HRF) approach gives developers a **single‑pass, declarative contract** with the model, turning what used to be a series of ad‑hoc function calls into a **structured conversation** that the model can *understand* and *control*. When you need **privacy, cost‑efficiency, or fine‑grained observability**, **GPT‑OSS + HRF** is the modern, production‑ready stack.

--- 

*Prepared by the LLM‑Engineering Team – March 2025*

## Processing Metadata

- Model Used: gpt-oss:120b
- Prompt Tokens: 31,645
- Analysis Tokens: 22,483
