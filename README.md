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
  ```
- **Automated Grading**: Every time you push to GitHub, our autograder will evaluate your progress. Check the **Actions** tab in your repo for your score.

---

## 🏆 Phase 3: The Challenge (Tracks)

Choose one of the following tracks to build your final project. Problem statements are located in `hackathon-resources/tracks/`.

1.  **Dataset Quality** — Optimizing data pipelines for high-fidelity LLM training.
2.  **Hallucination** — Building guardrails to detect and prevent LLM misinformation.
3.  **MCP Workflow** — Creating agentic workflows using the Model Context Protocol.
4.  **Toon Converter** — Developing advanced image-to-cartoon pipelines.
5.  **Traffic AI** — Real-time vehicle detection and analysis.

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
