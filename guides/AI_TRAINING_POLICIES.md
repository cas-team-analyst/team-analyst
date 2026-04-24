# AI Data Privacy Guide for Actuarial Professionals

> **The short version:** Your data is only protected if you are using AI through a business API or enterprise plan. Consumer accounts — even paid ones like Claude Pro or ChatGPT Plus — may use your conversations to train future models unless you actively opt out. This guide explains what that means for you and how to stay protected.

---

## Why this matters for actuaries

Actuarial work involves proprietary pricing models, client loss data, reserving judgments, and competitive methodologies. If that information enters an AI provider's training pipeline, it could — in theory — influence how future models respond to similar queries, potentially benefiting competitors or eroding the value of your expertise.

The good news: every major AI provider offers a protected path. The risk only materialises when professionals use the **wrong tier** of a product, often unknowingly.

---

## The critical distinction: consumer vs. enterprise/API

AI providers run two fundamentally different systems under the same brand name.

| Tier | Examples | Training risk |
|---|---|---|
| **Consumer** | ChatGPT Free/Plus/Pro, Claude Free/Pro/Max, Gemini (web) | Moderate to high — training on by default in most cases |
| **API / Enterprise** | OpenAI API, Claude for Work/Enterprise, Google Vertex AI, Azure OpenAI, Microsoft 365 Copilot | Low — contractually excluded from training by default |

> **Important:** Paying for a "Pro" or "Plus" subscription does **not** give you enterprise-grade data protection. Claude Pro and ChatGPT Plus are consumer products. Only API and enterprise plans carry contractual training exclusions.

---

## Provider-by-provider policy summary

### OpenAI / ChatGPT

**Consumer accounts (Free, Plus, Pro):**
By default, conversations may be used to train models. Users can opt out via **Settings → Data Controls → Improve the model for everyone**, but this must be done manually and is not retroactive.

**API and enterprise accounts (ChatGPT Business, Enterprise):**
Data is not used for training by default. OpenAI also offers a **Zero Data Retention (ZDR)** option for API customers, under which no prompts or responses are stored at all.

- [OpenAI data training policy](https://openai.com/policies/how-your-data-is-used-to-improve-model-performance/)
- [OpenAI enterprise privacy](https://openai.com/enterprise-privacy/)

---

### Anthropic / Claude

**Consumer accounts (Free, Pro, Max):**
In September 2025, Anthropic updated its consumer terms. Users who opted in (or did not opt out by the deadline) now have conversations retained for up to **5 years** and used for model training. Users who opted out retain the previous 30-day retention with no training use. You can check and change your setting at any time: **Claude.ai → Settings → Privacy → "Improve Claude for everyone"**.

**API and enterprise accounts (Claude for Work, Team, Enterprise, Amazon Bedrock, Google Vertex AI):**
Explicitly excluded from the 2025 policy change. No training on commercial customer data. This is governed by Anthropic's Commercial Terms, not the consumer privacy policy.

- [Anthropic consumer terms update (August 2025)](https://www.anthropic.com/news/updates-to-our-consumer-terms)
- [Anthropic privacy centre — model training](https://privacy.claude.com/en/articles/10023580-is-my-data-used-for-model-training)
- [Anthropic privacy centre — data retention](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data)

---

### Google Gemini

**Consumer accounts (Gemini.google.com):**
Google states that Gemini interactions may be used to improve its products and services, including AI models. Opt-out mechanisms exist but are not prominently surfaced. Consumer Gemini is the highest-risk tier among the major providers.

To disable: **Gemini App Activity** must be turned off in your Google Account settings. Note that doing so also disables conversation history.

**Enterprise accounts (Google Workspace with Gemini, Vertex AI):**
Google contractually guarantees that data processed through Vertex AI is not used to train foundation models. Gemini Enterprise, announced October 2025, carries the same no-training guarantee for business data.

- [Google Gemini Apps Privacy Hub](https://support.google.com/gemini/answer/13594961)
- [Google Cloud / Vertex AI data governance](https://cloud.google.com/vertex-ai/docs/general/data-governance)

---

### Microsoft Copilot / Azure OpenAI

**Consumer Copilot:**
The consumer version of Microsoft Copilot (copilot.microsoft.com) has weaker defaults than the enterprise version. Avoid using it for work involving sensitive actuarial data.

**Microsoft 365 Copilot and Azure OpenAI Service:**
Both products default to enterprise-grade privacy. Microsoft does not use M365 Copilot conversations or Azure OpenAI prompts to train foundation models. Azure OpenAI also inherits Microsoft's compliance certifications (SOC 2, ISO 27001, HIPAA, FedRAMP).

- [Microsoft Copilot data privacy](https://privacy.microsoft.com/en-us/privacystatement)
- [Azure OpenAI data, privacy, and security](https://learn.microsoft.com/en-us/legal/cognitive-services/openai/data-privacy)

---

## How to protect yourself: five rules

### 1. Always use the API or enterprise tier
If your organisation is providing you with an AI tool, confirm it is built on an API or enterprise plan — not a shared consumer account. Ask your tool provider directly. A legitimate business tool will be able to confirm this.

### 2. Never paste proprietary data in raw form
Anonymise or abstract sensitive inputs before querying any AI tool, regardless of tier:

| Instead of... | Use... |
|---|---|
| Actual loss ratios or claims figures | Normalised or placeholder values (e.g. "Loss ratio = X%") |
| Client names or policy numbers | "Client A", "Portfolio 1" |
| Proprietary pricing model logic | A structural description of the approach |

The AI almost never needs real numbers to help with methodology.

### 3. Opt out on any consumer account you use personally
If you use ChatGPT, Claude, or Gemini through a personal or consumer account for any professional purpose:

- **ChatGPT:** Settings → Data Controls → turn off "Improve the model for everyone"
- **Claude:** Settings → Privacy → turn off "Improve Claude for everyone"
- **Gemini:** Google Account → Data & Privacy → turn off Gemini Apps Activity

Remember: opt-out is **not retroactive**. It only applies to conversations after the setting is changed.

### 4. Treat AI outputs as drafts, not conclusions
Your professional judgement is the protection that cannot be trained away. An AI can assist with structure, language, and calculation — but actuarial sign-off must remain human. This is also good regulatory practice under most actuarial standards of practice.

### 5. For the highest-sensitivity work, request zero-data-retention
OpenAI's ZDR API option means no prompts or responses are stored after the request completes. Similar arrangements are available at the enterprise level from other providers. If your organisation handles particularly sensitive client data, ask whether a ZDR agreement is in place.

---

## Frequently asked questions

**Q: Can an AI model actually learn my proprietary methods and use them to replace me?**

Training on conversational data teaches a model how to *communicate* — not how to replicate your specific judgement, experience, or professional accountability. Your expertise is not just the facts you know; it is how you weigh uncertainty, interpret ambiguous data, and take responsibility for a conclusion. That is not what training pipelines capture.

**Q: I use ChatGPT Plus for work. Am I exposed?**

Possibly. ChatGPT Plus is a consumer product. Unless you have disabled the training setting in your account, conversations may be used to improve OpenAI's models. You should opt out immediately, and avoid inputting anything proprietary until you have confirmed the setting has changed.

**Q: Does using a VPN or incognito mode change anything?**

No. Data handling is governed by your account terms, not your network connection.

**Q: What if I use a free trial of an enterprise product?**

Enterprise trial accounts typically inherit the enterprise data terms. Confirm with the provider before inputting sensitive data.

**Q: Are there AI providers that never train on any user data?**

Several enterprise and on-premises options (such as Aleph Alpha's sovereign cloud deployments, or self-hosted open-weight models like Llama) can be configured to never send data to a third party at all. These are more complex to deploy but offer the strongest possible data isolation. Speak to your IT or compliance team if this level of control is required.

---

## The nuclear option: running AI entirely on your own machine

If the idea of any data leaving your organisation is unacceptable — even through a contractually protected API — there is a third path: running an open-weight language model locally, on hardware you control. No network calls. No third-party servers. No training implications whatsoever. This approach has matured significantly in 2025–2026 and is now practical for most professional workstations.

### What this means in practice

Tools like **[Ollama](https://ollama.com)** let you download and run open-weight AI models directly on a laptop or server. The model runs on your machine, inference happens locally, and nothing is transmitted anywhere. It is the AI equivalent of running software you have installed — the vendor has no visibility into how you use it after download.

As of 2026, Ollama also supports the **Claude Code** command-line tool natively. Claude Code is Anthropic's agentic coding and analysis tool; when pointed at a local Ollama instance rather than Anthropic's API, it runs entirely offline using an open-weight model. This means you get a capable agentic workflow — file reading, multi-step reasoning, tool use — with zero data leaving your machine.

- [Ollama official site](https://ollama.com)
- [Ollama + Claude Code integration docs](https://docs.ollama.com/integrations/claude-code)
- [Claude Code overview](https://code.claude.com/docs/en/overview)

### How to set it up

The setup is simpler than it sounds. Once Ollama is installed, a single command launches Claude Code pointed at your local model:

```bash
ollama launch claude --model qwen3.5
```

Ollama handles the API translation automatically — Claude Code expects Anthropic's message format, and since Ollama v0.14, Ollama speaks it natively. No proxy or adapter is needed.

For teams that want to configure this manually (for example, to lock it into a specific model), the environment variables approach also works:

```bash
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_AUTH_TOKEN="ollama"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

To verify the setup is truly offline, disconnect from the internet and run a prompt. If you get a response, no cloud connection is involved.

### Choosing a model

Not all open-weight models are equal. For professional analytical work, model choice matters. Here is a practical guide by hardware tier:

| Your hardware | Recommended model | Notes |
|---|---|---|
| 8 GB RAM | `qwen3.5:9b` or `llama3.2:3b` | Usable but slower; avoid complex multi-step tasks |
| 16 GB RAM | `qwen3.5:27b` or `phi-4:14b` | Good balance of quality and speed; suitable for document analysis |
| 32 GB RAM / Apple Silicon M-series | `qwen3.5:27b` or `llama3.3:70b` | Strong quality; M-series unified memory handles larger models well |
| Workstation with dedicated GPU (24 GB+ VRAM) | `qwen3.5:27b` or `qwen3-coder` | Best local quality; comparable to mid-tier cloud models on many tasks |

For actuarial work specifically — structured analysis, document review, methodology drafting — the `qwen3.5` family and Microsoft's `phi-4` model perform particularly well on reasoning and numerical tasks relative to their hardware requirements. The `qwen2.5-coder:14b` variant is well suited if the primary use case involves working with code or structured data files.

You can also use **4-bit quantisation** (the `Q4_K_M` format) to roughly halve the memory footprint with minimal quality loss. Ollama applies this by default for most models.

> **On quality expectations:** Local models trail the best cloud models on complex, multi-step reasoning tasks. For routine work — summarising reports, drafting methodology notes, reviewing calculations for structure — the gap is small. For highly complex analytical chains, you may prefer a cloud API with strong contractual protections over a weaker local model. The choice is between perfect privacy with moderate capability and strong privacy with higher capability.

### GUI alternatives to the command line

If command-line tools are not comfortable for your users, two GUI applications wrap the same local inference in a more familiar interface:

- **[LM Studio](https://lmstudio.ai)** — A desktop application for macOS, Windows, and Linux. Model management, a chat interface, and a local API server, all without touching a terminal. Exposes an OpenAI-compatible API that your actuarial tool can point at directly.
- **[Jan](https://jan.ai)** — An open-source offline desktop assistant. Similar to LM Studio in approach; useful for users who want a ChatGPT-style experience with complete local control.

Both tools expose a local API endpoint, which means your existing workflows can be pointed at them rather than a cloud provider by changing a single URL.

### What this approach does not solve

Local deployment is not a panacea. A few honest caveats:

- **Hardware cost.** Running a capable model locally requires a reasonably modern machine. Older laptops with 8 GB RAM will produce slow, lower-quality responses. The hardware investment is real.
- **Model quality ceiling.** The best open-weight models in 2026 are very good — but the frontier proprietary models (Claude Opus, GPT-5, etc.) still lead on the most demanding tasks. Local models are a strong option for routine professional work, not necessarily for the hardest analytical problems.
- **Maintenance.** You are responsible for updating models and managing disk space. Cloud APIs handle this invisibly; local deployment does not.
- **No audit trail.** If your organisation requires logging of AI interactions for compliance purposes, a local setup needs additional tooling to provide that. Cloud enterprise plans typically include this by default.

For organisations where data sovereignty is non-negotiable — or where regulatory requirements prohibit data leaving a specific jurisdiction — local deployment is the strongest available option. For most others, a well-configured API or enterprise plan provides sufficient protection with less operational overhead.

---

## Quick reference card

```
MAXIMUM PRIVACY — NO DATA LEAVES YOUR MACHINE:
  ✓ Ollama (local open-weight models, e.g. qwen3.5, phi-4, llama3.3)
  ✓ Claude Code + Ollama (local model backend, fully offline)
  ✓ LM Studio or Jan (GUI wrappers for local inference)

SAFE TO USE FOR SENSITIVE ACTUARIAL WORK (cloud, contractually protected):
  ✓ OpenAI API (with ZDR for highest sensitivity)
  ✓ ChatGPT Business or Enterprise accounts
  ✓ Anthropic API / Claude for Work / Claude Enterprise
  ✓ Google Vertex AI
  ✓ Microsoft 365 Copilot (enterprise licences)
  ✓ Azure OpenAI Service

USE WITH CAUTION — OPT OUT OF TRAINING FIRST:
  ⚠ ChatGPT Free / Plus / Pro
  ⚠ Claude Free / Pro / Max
  ⚠ Microsoft Copilot (consumer)

AVOID FOR SENSITIVE WORK:
  ✗ Google Gemini (consumer web interface)
  ✗ Any AI tool where you cannot confirm the data tier
```

---

*This document reflects provider policies as of April 2026. AI provider terms change frequently. Review the linked policy pages periodically and consult your organisation's compliance team for guidance specific to your regulatory environment.*