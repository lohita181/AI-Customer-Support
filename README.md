# Hiver SDE Intern - AI Customer Support Agent

This repository contains the complete pipeline for the Hiver SDE Intern take-home assignment.

## 1. Quickstart (Reproduce Results in < 15 mins)

1. Clone this repo: `git clone https://github.com/lohita181/AI-Customer-Support`
2. Install requirements: `pip install pandas scikit-learn google-genai pydantic`
3. Set your Gemini API key:
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your_api_key_here"
   ```
4. Run the evaluation harness (this will evaluate the baselines and the Agent against the Golden Dataset, then run the LLM-as-a-judge):
   ```bash
   python eval.py
   ```
5. **(Optional) Test the agent manually:** If you'd like to test the agent interactively with your own custom tweets without running the full evaluation, you can open a Python shell and call the function directly:
   ```python
   # Inside your python shell
   from agent import run_agent
   result = run_agent("My iPhone battery is draining so fast after the update!")
   print(result)
   ```

## 2. Problem Framing

**What "good" means for @AppleSupport:**
A good support agent for Apple must correctly identify hardware vs software issues. Hardware issues almost always require escalation (to set up a physical repair appointment), while software bugs, subscription inquiries, and general how-tos can often be auto-handled. Therefore, "good" means high precision on escalations to avoid frustrating customers and wasting human agents' time.

**What I chose NOT to build:**
I intentionally chose not to build multi-turn context memory or RAG (Retrieval-Augmented Generation). Twitter customer support is usually resolved quickly in DMs or requires an immediate pivot from public tweet to DM. The first touchpoint classification is the most critical to route it correctly.

## 3. Golden Dataset Sampling & Labeling

**Sampling Strategy:**
The Kaggle dataset was first filtered for conversations exclusively involving `@AppleSupport` as the responding brand. From the resulting ~106k reconstructed threads (customer message -> brand reply), we took a completely random sample of 200 rows to create our evaluation set. A random sample was chosen over keyword stratification to accurately reflect the real-world highly skewed distribution of inbound customer requests.

**Labeling Strategy:**
To label the 200 examples rapidly and consistently, we utilized an LLM (Gemini 2.5 Flash) to perform a first pass across the sampled rows, classifying each into one of six predefined intents and making an escalation decision with reasoning. As a human-in-the-loop, these labels were then audited to ensure they made logical sense for the context. This generated our `golden_dataset.csv`.

## 4. Results vs. Baselines

Our `eval.py` tests against three systems:
- **Trivial Baseline:** Always predicts majority class intent (`general_inquiry`) and always escalates.
- **Simple Baseline:** Uses keyword matching to assign intent and rules to trigger escalation.
- **Agent:** An LLM Pipeline utilizing `google-genai` forced to output structured JSON with intents and escalation reasoning.

*See `eval_results.txt` for exact F1 and Accuracy scores.*

## 5. Failure Analysis

Through inspecting the Golden Dataset and the Agent's predictions, here are the top failure modes:
1. **Sarcasm / Implicit Frustration:** The LLM struggles to detect when a user is being sarcastic about a "great update" that actually broke their phone. (Hypothesis: Needs few-shot examples of sarcasm).
2. **Ambiguous Mentions:** Sometimes a user just tags `@AppleSupport` with an image and no text. The model defaults to `general_inquiry`. (Hypothesis: Multimodal inputs are needed for these).
3. **Over-Escalation on Billing:** The model tends to escalate any mention of "money" or "charge" even if it's a simple refund request that could be auto-handled via a link. (Hypothesis: The prompt needs stricter rules on billing).
4. **Third-Party App Confusion:** If a user complains about Spotify crashing on iOS, the model classifies it as a `software_bug` for Apple to fix, instead of auto-handling and directing them to the third-party developer.
5. **Vague Pronouns:** "It isn't working." The model guesses `hardware_issue` but it could be anything. 

## 6. What is misleading about my headline number?

The high Intent Accuracy (e.g. ~85%+) is highly misleading because the dataset is extremely skewed. A vast majority of tweets sent to `@AppleSupport` fall under `general_inquiry` or `software_bug`. A trivial baseline that just predicts the most common class will score decently high. The real test is the *precision* on rare intents (like billing issues), which the headline accuracy number obscures. 

## 7. What I'd do with one more week
- **Implement RAG:** Use vector embeddings of historical support docs so the drafted replies contain real, accurate troubleshooting steps.
- **Active Learning:** Instead of randomly sampling 200 rows, use the model to find the 200 rows it is *least confident* about, and hand-label those to improve the edge cases.
- **Prompt A/B Testing:** Build a rigorous test framework (like `promptfoo`) to test different system prompts to minimize API costs (token usage) without dropping accuracy.

## 8. Decision Log

1. **Brand Choice (`@AppleSupport`):** Selected because they handle both physical hardware and digital services, making intent classification non-trivial.
2. **LLM Provider (Gemini 2.5 Flash):** Selected for its very low latency, cheap cost, and excellent native JSON structure generation via `response_schema`.
3. **No multi-turn:** Dropped to focus strictly on first-touch routing accuracy.
4. **Discarded tweets without `in_response_to`:** I specifically filtered the dataset to only include customer messages that eventually received a brand reply, ensuring we have implicit ground truth that the message was valid.
5. **No custom LLM Judge rubric file:** Kept the rubric directly in the `eval.py` prompt to minimize file clutter and dependencies.
6. **Binary Escalation:** Modeled escalation as a simple boolean rather than tiered routing to keep the metrics (F1 score) interpretable.
7. **Zero-Shot for Agent:** Used zero-shot instead of few-shot for the agent to demonstrate baseline LLM reasoning; few-shot would improve it further.
8. **Automated Golden Set Generation:** Used the LLM to do a first pass of the golden set labels to save 3 hours of manual data entry, acting as human-in-the-loop to verify them later.
9. **No complex chunking:** Customer tweets are short (<280 chars), so no text chunking or map-reduce was needed for the LLM pipeline.
10. **JSON Strict Output:** Forced `pydantic` schemas so `json.loads` never fails in the pipeline, which is a common failure mode in LLM wrappers.
