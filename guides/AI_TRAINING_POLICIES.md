# AI Data Privacy Guide for Actuarial Professionals

## Navigation

**[TLDR](#tldr)** | **[Why This Matters](#why-this-matters-for-actuaries)** | **[Consumer vs Enterprise](#the-critical-distinction-consumer-vs-enterpriseapi)** | **[Provider Policies](#provider-by-provider-policy-summary)** | **[How to Protect Yourself](#how-to-protect-yourself-five-rules)** | **[FAQ](#faq)** | **[Local AI](#running-ai-on-your-own-machine)** | **[Quick Reference](#quick-reference-card)**

---

## TLDR

1. **Consumer accounts train by default** — ChatGPT, Claude, and Gemini (including paid Pro/Plus) use your conversations for training unless you opt out.

2. **Opt out in seconds:**
   - **ChatGPT:** Settings → Data Controls → disable "Improve the model for everyone"
   - **Claude:** Settings → Privacy → disable "Improve Claude for everyone"  
   - **Gemini:** Google Account → Data & Privacy → disable "Gemini Apps Activity"

3. **Enterprise/API tiers protected by default** — All major providers contractually exclude business data from training.

4. **Complete privacy: Run locally** — **[Ollama](https://ollama.com)** runs AI entirely on your hardware. Nothing leaves your machine. Handles actuarial workflows, document analysis, coding. See [local AI section](#running-ai-on-your-own-machine).

5. **Settings aren't retroactive** — Configure before sharing proprietary data.

**Bottom line:** Choose enterprise for auto-protection, configure consumer settings, or use Ollama for offline control.

---

## Why this matters for actuaries

Actuarial work involves proprietary pricing models, client data, reserving judgments, and competitive methodologies. If this enters an AI training pipeline, future models could theoretically respond to similar queries in ways that benefit competitors.

**Every major provider offers data protection — you control which path you use.** Risk arises from: (1) using the wrong tier, or (2) not configuring consumer privacy settings. Both are preventable.

---

## The critical distinction: consumer vs. enterprise/API

Same brand, different defaults:

| Tier | Examples | Default | Can opt out? |
|---|---|---|---|
| **Consumer** | ChatGPT Free/Plus/Pro, Claude Free/Pro/Max, Gemini (web) | Training ON | ✓ Manual opt-out available |
| **API / Enterprise** | OpenAI API, Claude for Work/Enterprise, Google Vertex AI, Azure OpenAI, M365 Copilot | No training | N/A — protected |

> **Key:** Every provider offers no-training. Enterprise/API gives it by default. Consumer requires configuration. Paid "Pro/Plus" subscriptions don't automatically protect data.

---

## Provider-by-provider policy summary

### OpenAI / ChatGPT

**Consumer (Free, Plus, Pro):**
Training enabled by default. **Disable:** Settings → Data Controls → "Improve the model for everyone" (toggle off). Use **Temporary Chat** for one-off private conversations.

**API/Enterprise (ChatGPT Business, Enterprise):**
No training by default. **Zero Data Retention (ZDR)** option available — nothing stored.

- [OpenAI data training policy](https://openai.com/policies/how-your-data-is-used-to-improve-model-performance/)
- [OpenAI enterprise privacy](https://openai.com/enterprise-privacy/)

---

### Anthropic / Claude

**Consumer (Free, Pro, Max):**
September 2025 update: opted-in users have 5-year retention and training. **Disable anytime:** Claude.ai → Settings → Privacy → "Improve Claude for everyone" (toggle off). Disabled = 30-day retention, no training. **Incognito Chat** never stores or trains, regardless of settings.

**API/Enterprise (Claude for Work, Team, Enterprise, Bedrock, Vertex AI):**
No training on commercial data. Governed by Commercial Terms.

- [Anthropic consumer terms update (August 2025)](https://www.anthropic.com/news/updates-to-our-consumer-terms)
- [Anthropic privacy centre — model training](https://privacy.claude.com/en/articles/10023580-is-my-data-used-for-model-training)
- [Anthropic privacy centre — data retention](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data)

---

### Google Gemini

**Consumer (Gemini.google.com):**
May be used for training. **Disable:** Google Account → Data & Privacy → Gemini Apps Activity (toggle off). Note: also disables conversation history. Less visible than other providers, but effective.

**Enterprise (Google Workspace with Gemini, Vertex AI):**
Contractual no-training guarantee for business data.

- [Google Gemini Apps Privacy Hub](https://support.google.com/gemini/answer/13594961)
- [Google Cloud / Vertex AI data governance](https://cloud.google.com/vertex-ai/docs/general/data-governance)

---

### Microsoft Copilot / Azure OpenAI

**Consumer (copilot.microsoft.com):**
Weaker defaults. **Review:** account.microsoft.com → Privacy → Activity data. Less transparent than competitors. Prefer enterprise for sensitive work.

**M365 Copilot / Azure OpenAI:**
Enterprise-grade privacy. No training on user data. Azure OpenAI: SOC 2, ISO 27001, HIPAA, FedRAMP certified.

- [Microsoft Copilot data privacy](https://privacy.microsoft.com/en-us/privacystatement)
- [Azure OpenAI data, privacy, and security](https://learn.microsoft.com/en-us/legal/cognitive-services/openai/data-privacy)

---

## How to protect yourself: five rules

### 1. Configure privacy settings immediately
If using consumer accounts professionally:

- **ChatGPT:** Settings → Data Controls → disable "Improve the model for everyone"
- **Claude:** Settings → Privacy → disable "Improve Claude for everyone"
- **Gemini:** Google Account → Data & Privacy → disable "Gemini Apps Activity"
- **Microsoft Copilot:** Microsoft Account → Privacy → review Activity data

Settings protect future conversations only, not past ones.

### 2. Prefer API/enterprise for organizational use
Confirm organizational tools use API or enterprise plans — they default to no-training. Ask your provider directly.

### 3. Anonymize proprietary data
Abstract sensitive inputs regardless of tier:

| Instead of... | Use... |
|---|---|
| Actual loss ratios/claims | "Loss ratio = X%" |
| Client names/policy numbers | "Client A", "Portfolio 1" |
| Proprietary pricing logic | Structural description |

AI rarely needs real numbers for methodology.

### 4. Treat outputs as drafts
Your judgment is irreplaceable. AI assists with structure and calculation — actuarial sign-off stays human.

### 5. For highest sensitivity, use zero-retention
OpenAI ZDR: nothing stored. Claude Incognito: nothing stored. Ask your provider about similar options.

---

## FAQ

**Q: Can AI learn my proprietary methods and replace me?**

Training teaches models to communicate, not replicate your judgment, experience, or accountability. Your expertise is how you weigh uncertainty and take responsibility — training doesn't capture that.

**Q: I use ChatGPT Plus for work. Am I exposed?**

Only if you haven't changed settings. Go to Settings → Data Controls → disable "Improve the model for everyone" now. Use Temporary Chat for immediate privacy.

**Q: Does VPN or incognito mode help?**

No. Data handling follows account terms, not network setup.

**Q: What about free trials of enterprise products?**

Typically inherit enterprise terms. Confirm before inputting sensitive data.

**Q: Any providers that never train on user data?**

Enterprise/on-premises options (Aleph Alpha sovereign cloud, self-hosted Llama) can be configured for complete isolation. More complex but strongest protection. Consult IT/compliance.

---

## Running AI on your own machine

For absolute data control: run open-weight models locally. No network calls, no third-party servers, no training. Practical for most workstations as of 2026.

### What this means

**[Ollama](https://ollama.com)** runs AI models on your laptop/server. Model downloads once, runs locally, transmits nothing. Like installed software — vendor has no visibility after download.

Ollama supports **Claude Code** natively (2026). Point Claude Code at local Ollama instead of Anthropic's API — full agentic workflow (file reading, reasoning, tool use) with zero cloud dependency.

- [Ollama](https://ollama.com)
- [Ollama + Claude Code](https://docs.ollama.com/integrations/claude-code)
- [Claude Code](https://code.claude.com/docs/en/overview)

### Setup

Once Ollama is installed:

```bash
ollama launch claude --model qwen3.5
```

Ollama handles API translation — Claude Code works natively (Ollama v0.14+).

Manual config (optional):

```bash
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_AUTH_TOKEN="ollama"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

Verify offline: disconnect internet, run prompt. Response = no cloud.

### Model selection

| Hardware | Model | Notes |
|---|---|---|
| 8 GB RAM | `qwen3.5:9b`, `llama3.2:3b` | Slow, avoid complex tasks |
| 16 GB RAM | `qwen3.5:27b`, `phi-4:14b` | Good balance, handles document analysis |
| 32 GB / M-series | `qwen3.5:27b`, `llama3.3:70b` | Strong quality |
| GPU (24 GB+ VRAM) | `qwen3.5:27b`, `qwen3-coder` | Best local quality |

For actuarial work: `qwen3.5` and `phi-4` excel at reasoning/numerical tasks. `qwen2.5-coder:14b` for code/structured data.

**4-bit quantization** (Q4_K_M): halves memory, minimal quality loss. Ollama default.

> **Quality trade-off:** Local models lag frontier cloud models on complex reasoning. For routine work (reports, methodology, calculation review), gap is small. For hardest problems, cloud API with strong contract may be better. Choice: perfect privacy + moderate capability vs. strong privacy + higher capability.

### GUI options

- **[LM Studio](https://lmstudio.ai)** — Desktop app (macOS/Windows/Linux). Chat interface, local API. No terminal.
- **[Jan](https://jan.ai)** — Open-source desktop assistant. Similar to LM Studio.

Both expose local API — point workflows at localhost instead of cloud.

### Caveats

- **Hardware cost** — Modern machine required. 8 GB laptops = slow.
- **Quality ceiling** — 2026 open-weight models good, but Claude Opus/GPT-5 still lead on hardest tasks.
- **Maintenance** — You update models and manage disk. Cloud handles invisibly.
- **No audit trail** — Compliance logging needs extra tooling. Cloud enterprise includes by default.

**Best for:** Data sovereignty requirements or prohibited data export. **Otherwise:** API/enterprise plan = sufficient protection, less overhead.

---

*This document reflects provider policies as of May 2026. AI provider terms change frequently. Review linked policy pages periodically and consult your organization's compliance team for guidance.*