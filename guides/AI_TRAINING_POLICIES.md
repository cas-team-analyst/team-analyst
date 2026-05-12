# AI Data Privacy Guide for Actuarial Professionals

**[TLDR](#tldr)** | **[Why This Matters](#why-this-matters-for-actuaries)** | **[Consumer vs Enterprise](#the-critical-distinction-consumer-vs-enterpriseapi)** | **[Provider Policies](#provider-by-provider-policy-summary)** | **[How to Protect Yourself](#how-to-protect-yourself-five-rules)** | **[FAQ](#faq)** | **[Local AI](#running-ai-on-your-own-machine)** | **[Quick Reference](#quick-reference-card)**

---

## TLDR

1. **Consumer accounts train by default** — ChatGPT, Claude, and Gemini (including paid Pro/Plus subscriptions) use your conversations for training unless you opt out.

2. **How to opt out:** Each provider offers a straightforward opt-out mechanism:
   - **ChatGPT:** Settings → Data Controls → disable "Improve the model for everyone"
   - **Claude:** Settings → Privacy → disable "Improve Claude for everyone"  
   - **Gemini:** Google Account → Data & Privacy → disable "Gemini Apps Activity"

3. **Enterprise/API tiers are protected by default** — All major providers contractually exclude business data from training.

4. **Complete privacy option: Run locally** — [Ollama](https://ollama.com) runs AI entirely on your hardware. Nothing leaves your machine. Handles actuarial workflows, document analysis, coding. See [Running on Your Own Machine](#running-ai-on-your-own-machine).

5. **Settings aren't retroactive** — Configure before sharing proprietary data.

---

## The critical distinction: consumer vs. enterprise/API

AI subscriptions can be classified into two categories, each with different default privacy settings:

| Tier | Examples | Default | Can opt out? |
|---|---|---|---|
| **Consumer** | ChatGPT Free/Plus/Pro, Claude Free/Pro/Max, Gemini (web) | Training ON | ✓ Manual opt-out available |
| **API / Enterprise** | OpenAI API, Claude for Work/Enterprise, Google Vertex AI, Azure OpenAI, M365 Copilot | No training | N/A — protected |

> **Important to understand:** Every provider offers a no-training option. The key difference is that Enterprise/API tiers provide this protection by default, while Consumer tiers require manual configuration. Even paid "Pro" or "Plus" subscriptions don't automatically protect your data from training.

---

## Provider-by-provider policy summary

### OpenAI / ChatGPT

**Consumer accounts (Free, Plus, Pro):**
Training is enabled by default. **To disable:** Navigate to Settings → Data Controls → "Improve the model for everyone" and toggle it off. You can also use **Temporary Chat** mode for one-off private conversations that won't be saved or used for training.

**API and Enterprise accounts (ChatGPT Business, Enterprise):**
Your data is not used for training by default. OpenAI also offers a **Zero Data Retention (ZDR)** option for API customers, which means no prompts or responses are stored at all.

- [OpenAI data training policy](https://openai.com/policies/how-your-data-is-used-to-improve-model-performance/)
- [OpenAI enterprise privacy](https://openai.com/enterprise-privacy/)

---

### Anthropic / Claude

**Consumer accounts (Free, Pro, Max):**
Following a September 2025 policy update, users who opted in (or did not opt out by the deadline) now have conversations retained for up to 5 years and used for model training. **You can disable this at any time:** Navigate to Claude.ai → Settings → Privacy → "Improve Claude for everyone" and toggle it off. Once disabled, your conversations are retained for only 30 days and are not used for training. You can also use **Incognito Chat** mode for conversations that are never stored or used for training, regardless of your account settings.

**API and Enterprise accounts (Claude for Work, Team, Enterprise, Bedrock, Vertex AI):**
Commercial customer data is not used for training. These accounts are governed by Anthropic's Commercial Terms rather than consumer privacy policies.

- [Anthropic consumer terms update (August 2025)](https://www.anthropic.com/news/updates-to-our-consumer-terms)
- [Anthropic privacy centre — model training](https://privacy.claude.com/en/articles/10023580-is-my-data-used-for-model-training)
- [Anthropic privacy centre — data retention](https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data)

---

### Google Gemini

**Consumer accounts (Gemini.google.com):**
Google states that Gemini interactions may be used to improve its products and services, including AI models. **To disable:** Navigate to Google Account → Data & Privacy → Gemini Apps Activity and toggle it off. Note that doing so also disables your conversation history. The opt-out mechanism is less prominently displayed than other providers, but it is available and effective.

**Enterprise accounts (Google Workspace with Gemini, Vertex AI):**
Google provides a contractual no-training guarantee for business data processed through these services.

- [Google Gemini Apps Privacy Hub](https://support.google.com/gemini/answer/13594961)
- [Google Cloud / Vertex AI data governance](https://cloud.google.com/vertex-ai/docs/general/data-governance)

---

### Microsoft Copilot / Azure OpenAI

**Consumer Copilot (copilot.microsoft.com):**
The consumer version has weaker privacy defaults compared to the enterprise version. **To review your settings:** Navigate to account.microsoft.com → Privacy → Activity data. Microsoft's privacy controls are less transparent than some competitors, so for sensitive actuarial work, we recommend using the enterprise tier.

**Microsoft 365 Copilot and Azure OpenAI Service:**
Both products provide enterprise-grade privacy protection. Microsoft does not use data from M365 Copilot conversations or Azure OpenAI prompts to train foundation models. Azure OpenAI also inherits Microsoft's compliance certifications, including SOC 2, ISO 27001, HIPAA, and FedRAMP.

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

Please note that these settings only protect future conversations, not past ones.

### 2. Prefer API or enterprise tiers for organizational use
If your organization is providing you with an AI tool, confirm that it is built on an API or enterprise plan. These tiers default to no-training without requiring manual configuration. Don't hesitate to ask your tool provider directly—a legitimate business tool should be able to confirm this easily.

### 3. Anonymize proprietary data
Abstract or anonymize sensitive inputs before querying any AI tool, regardless of which tier you're using:

| Instead of... | Use... |
|---|---|
| Actual loss ratios/claims | "Loss ratio = X%" |
| Client names/policy numbers | "Client A", "Portfolio 1" |
| Proprietary pricing logic | Structural description |

Remember: AI almost never needs actual numbers to help with methodology questions.

### 4. Treat AI outputs as drafts, not conclusions
Your professional judgment is irreplaceable. AI can assist with structure, language, and calculations, but actuarial sign-off must remain human. This is also good regulatory practice under most actuarial standards of practice.

### 5. For the highest-sensitivity work, use zero-retention options
OpenAI's Zero Data Retention (ZDR) API option means no prompts or responses are stored after the request completes. Claude offers Incognito Chat mode for consumers with the same guarantee. Similar arrangements are available at the enterprise level from other providers. If your organization handles particularly sensitive client data, ask whether a zero-retention agreement is in place.

---

## FAQ

**Q: Can AI actually learn my proprietary methods and replace me?**

Not in the way you might think. Training on conversational data teaches a model how to communicate more effectively, but it doesn't replicate your specific judgment, experience, or professional accountability. Your expertise isn't just about the facts you know—it's about how you weigh uncertainty, interpret ambiguous data, and take responsibility for your conclusions. That dimension of professional work isn't what training pipelines capture.

**Q: I use ChatGPT Plus for work. Am I at risk?**

Only if you haven't configured your privacy settings. ChatGPT Plus is a consumer product, and training is enabled by default. You should navigate to Settings → Data Controls and disable "Improve the model for everyone" right away. Once you do this, your new conversations will not be used to train OpenAI's models. For immediate privacy on specific conversations, you can also use Temporary Chat mode.

**Q: Does using a VPN or incognito browser mode change anything?**

No, it doesn't. Data handling is governed by your account terms and privacy settings, not by your network connection or browser mode.

**Q: What about free trials of enterprise products?**

Enterprise trial accounts typically inherit the same enterprise data protection terms as paid accounts. However, you should confirm this with the provider before inputting any sensitive data.

**Q: Are there any AI providers that never train on user data at all?**

Yes. Several enterprise and on-premises options (such as Aleph Alpha's sovereign cloud deployments or self-hosted open-weight models like Llama) can be configured to never send data to a third party at all. These options are more complex to deploy but offer the strongest possible data isolation. If this level of control is required for your organization, consult your IT or compliance team.

---

## Running AI on your own machine

For organizations that require absolute data control, there's a third option: running open-weight AI models locally on hardware you control. With this approach, there are no network calls, no third-party servers, and no training implications whatsoever. This approach has matured significantly and is now practical for most professional workstations as of 2026.

### What this means

**[Ollama](https://ollama.com)** is a tool that allows you to run AI models directly on your laptop or server. The model downloads once, runs entirely locally, and transmits nothing over the internet. It's similar to running any other piece of installed software—the vendor has no visibility into how you use it after the initial download.

As of 2026, Ollama also supports **Claude Code** natively. Claude Code is Anthropic's agentic coding and analysis tool. When you point Claude Code at a local Ollama instance instead of Anthropic's cloud API, it runs entirely offline using an open-weight model. This gives you a capable agentic workflow (including file reading, multi-step reasoning, and tool use) with zero cloud dependency.

- [Ollama](https://ollama.com)
- [Ollama + Claude Code](https://docs.ollama.com/integrations/claude-code)
- [Claude Code](https://code.claude.com/docs/en/overview)

### Setup

The setup process is straightforward. Once Ollama is installed on your system, you can launch Claude Code pointed at your local model with a single command:

```bash
ollama launch claude --model qwen3.5
```

Ollama handles the API translation automatically—Claude Code works natively with Ollama v0.14 and later.

If you prefer to configure this manually (for example, to lock it into a specific model), you can also use environment variables:

```bash
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_AUTH_TOKEN="ollama"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

To verify that your setup is truly offline, disconnect from the internet and run a test prompt. If you get a response, no cloud connection is involved.

### Model selection

Not all open-weight models perform equally. For professional analytical work, model choice matters. Here's a practical guide organized by hardware tier:

| Hardware | Recommended models | Notes |
|---|---|---|
| 8 GB RAM | `qwen3.5:9b`, `llama3.2:3b` | Usable but slower; best to avoid complex multi-step tasks |
| 16 GB RAM | `qwen3.5:27b`, `phi-4:14b` | Good balance of quality and speed; suitable for document analysis |
| 32 GB RAM / M-series | `qwen3.5:27b`, `llama3.3:70b` | Strong quality across most tasks |
| GPU workstation (24 GB+ VRAM) | `qwen3.5:27b`, `qwen3-coder` | Best local quality available |

For actuarial work specifically—structured analysis, document review, and methodology drafting—the `qwen3.5` family and Microsoft's `phi-4` model perform particularly well on reasoning and numerical tasks relative to their hardware requirements. The `qwen2.5-coder:14b` variant is well-suited if your primary use case involves working with code or structured data files.

You can also use **4-bit quantization** (the Q4_K_M format) to roughly halve the memory footprint with minimal quality loss. Ollama applies this optimization by default for most models.

> **Quality trade-off to consider:** Local models currently trail the best cloud models (like Claude Opus or GPT-5) on highly complex, multi-step reasoning tasks. However, for routine professional work—summarizing reports, drafting methodology notes, and reviewing calculations for structure—the quality gap is relatively small. For the most demanding analytical chains, you may prefer a cloud API with strong contractual protections over a local model. The choice is essentially between perfect privacy with moderate capability versus strong privacy with higher capability.

### GUI alternatives to the command line

If command-line tools aren't comfortable for you or your team, there are two GUI applications that provide the same local inference capabilities in a more familiar interface:

- **[LM Studio](https://lmstudio.ai)** — A desktop application available for macOS, Windows, and Linux. It provides model management, a chat interface, and a local API server without requiring any terminal work. It exposes an OpenAI-compatible API that your actuarial tools can connect to directly.
- **[Jan](https://jan.ai)** — An open-source offline desktop assistant with a similar approach to LM Studio. This is particularly useful if you want a ChatGPT-style experience with complete local control.

Both tools expose a local API endpoint, which means you can point your existing workflows at localhost instead of a cloud provider by simply changing a URL.

### Important caveats

While local deployment offers maximum privacy, it's not without trade-offs:

- **Hardware requirements** — Running a capable model locally requires a reasonably modern machine. Older laptops with only 8 GB of RAM will produce slow, lower-quality responses.
- **Quality ceiling** — While the best open-weight models in 2026 are quite good, frontier proprietary models (like Claude Opus and GPT-5) still lead on the most demanding tasks.
- **Maintenance responsibility** — You're responsible for updating models and managing disk space. Cloud APIs handle this invisibly.
- **No audit trail by default** — If your organization requires logging of AI interactions for compliance purposes, a local setup needs additional tooling to provide that. Cloud enterprise plans typically include audit logging by default.

**When to choose local deployment:** This approach is ideal for organizations where data sovereignty is non-negotiable or where regulatory requirements prohibit data from leaving a specific jurisdiction. **For most others:** A well-configured API or enterprise plan provides sufficient protection with significantly less operational overhead.

---

*This document reflects provider policies as of May 2026. AI provider terms change frequently. Review linked policy pages periodically and consult your organization's compliance team for guidance.*