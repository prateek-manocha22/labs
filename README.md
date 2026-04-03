# 🚀 AI Hackathon 2026: Student Guide

Welcome to the **Gen-AI Hackathon 2026**! This repository is your central hub for all resources, starter kits, and submission templates.

---

## 📂 Repository Structure

```text
├── hackathon-resources/
│   └── tracks/          # Problem statements and challenge details
├── labs/                # Auto-graded skill-building exercises
├── starter-kits/        # Template code to jumpstart your project
├── submission-template/ # MUST USE: Format for your final submission
└── README.md            # This guide!
```

---

## 🛠️ Phase 1: Local Setup

Follow these steps to prepare your development environment:

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Set Up Python Environment
We recommend using a virtual environment (Python 3.10+):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and add your API keys (OpenAI, Anthropic, etc.):
```bash
cp .env.example .env
```

---

## 🎓 Phase 2: Skills Check (Labs)

Before diving into the main challenge, complete the **Auto-Graded Labs** in the `labs/` directory. These are designed to build your AI engineering skills.

- **Objective**: Pass all tests to score 100/100 points.
- **To Run Locally**: 
  ```bash
  cd hackathon-2026/labs
  pytest lab-01-api-fetcher/tests/  # Example for Lab 01
  pytest lab-06-healthcare-agents/tests/  # Example for Lab 06
  ```
- **Automated Grading**: Every time you push to GitHub, our autograder will evaluate your progress. Check the **Actions** tab in your repo for your score.

---

## 🏆 Phase 3: The Challenge (Tracks)

Choose one of the following tracks to build your final project. Problem statements are located in `hackathon-2026/hackathon-resources/tracks/`.

### 🚩 Flagship Track
*   **[MCP-Based AI Work Assistant](hackathon-2026/hackathon-resources/tracks/mcp-workflow.md)** — Build a context-aware AI assistant using Model Context Protocol.

### ⚡ Advanced Tracks
*   **[Healthcare Agentic AI](hackathon-2026/hackathon-resources/tracks/healthcare.md)** — Real-time patient monitoring and anomaly detection.
*   **[Hallucination Detection](hackathon-2026/hackathon-resources/tracks/hallucination.md)** — Scoring and flagging hallucinated LLM content.
*   **[Dataset Quality Analyzer](hackathon-2026/hackathon-resources/tracks/dataset-quality.md)** — Evaluating datasets for bias and noise with NLP support.
*   **[Technology (Agentic Coding)](hackathon-2026/hackathon-resources/tracks/technology-coding.md)** — Autonomous issue detection and code improvement.
*   **[Event Recommender](hackathon-2026/hackathon-resources/tracks/event-recommender.md)** — Personalized engine with collaborative filtering and reasoning.
*   **[Traffic AI](hackathon-2026/hackathon-resources/tracks/traffic-ai.md)** — Real-time vehicle detection and analysis.

### 🌱 Foundation Tracks
*   **[Churn Predictor](hackathon-2026/hackathon-resources/tracks/churn-predictor.md)** — Customer churn prediction with explainable AI.
*   **[Cybersecurity](hackathon-2026/hackathon-resources/tracks/cybersecurity.md)** — Autonomous threat detection and response.
*   **[Form Filler](hackathon-2026/hackathon-resources/tracks/form-filler.md)** — Extraction and auto-filling from documents.
*   **[TOON Converter](hackathon-2026/hackathon-resources/tracks/toon.md)** — Tokenized graph structures for AI reasoning.

---

## 🏗️ Phase 4: Building & Submission

### 1. Use a Starter Kit
Don't start from zero! Use the code in `starter-kits/` to jumpstart your development.

### 2. Follow the Submission Template
Your final project **must** be structured according to the `submission-template/` directory. 
- Create a new folder in the root (e.g., `my-awesome-project/`).
- Copy the contents of `submission-template/` into it.
- Fill out the `README.md` with your project details and demo link.

### 3. Submission Checklist
- [ ] **Code**: Clean, documented code in the `src/` folder.
- [ ] **Demo**: A 2-minute video (YouTube/Loom) or high-quality GIF of your tool in action.
- [ ] **Installation**: Clear instructions on how to run your code locally.
- [ ] **Documentation**: A clear explanation of your architecture and AI approach.

---

## ⚖️ Evaluation Criteria

Your project will be evaluated by our mentors based on:

| Category | Weight | Description |
| :--- | :--- | :--- |
| **Logic & Accuracy** | 40% | Does the AI solve the problem effectively? |
| **Innovation** | 25% | Is the approach creative or technically unique? |
| **Code Hygiene** | 20% | Is the code well-structured and documented? |
| **Presentation** | 15% | Is the README clear and the demo compelling? |

---

## 🆘 Need Help?
- **Discord**: Join the `#hackathon-support` channel.
- **Issues**: Use GitHub Issues for bug reports in the starter kits.

Good luck, and happy hacking! 🚀

---

# Lab UX & Support 🛠️

Welcome to the auto-graded lab system! These labs are designed to build your AI engineering skills step-by-step.

## 📜 Table of Contents
1. [**Lab 01: API Fetcher**](./lab-01-api-fetcher/) — Easy
2. [**Lab 02: LLM JSON**](./lab-02-llm-json/) — Easy
3. [**Lab 03: TOON Converter**](./lab-03-toon-convert/) — Medium
4. [**Lab 04: Vehicle Detect**](./lab-04-vehicle-detect/) — Medium
5. [**Lab 05: RAG Q&A**](./lab-05-rag-qa/) — Hard

---

## 🔍 How to Read GitHub Actions Logs

If your score isn't what you expected, check the logs:
1. Go to the **Actions** tab in your repository.
2. Click on the latest run (e.g., "🎓 Auto-Grade Labs").
3. Click the **grade** job on the left.
4. Expand the **🧪 Run All Lab Tests** step.
5. If a test failed, it will show a red `F` and a traceback explaining why.

## 💡 Common Errors

-   **SyntaxError**: Python can't run your code because of a typo (missing `:` or `)`).
-   **ImportError**: You are using a library (like `requests`) but didn't import it.
-   **AssertionError**: Your function returned something, but it's not what the test expected (e.g., returning a string instead of a list).

## 🆘 Where to Ask for Help
-   Post in the `#labs-help` Discord channel.
-   Check the `README.md` inside each lab folder for specific tips.

