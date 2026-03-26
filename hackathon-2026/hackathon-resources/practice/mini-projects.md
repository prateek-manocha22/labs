# 🛠️ Mini Practice Projects

**When to do this**: Days 3–4 of the hackathon.

These tasks each take 1–2 hours. They map directly to the **auto-graded labs** — complete them here first, then submit via the labs repo to get scored.

> 💡 **Graded version**: See the [`labs/` repo](../../../labs/) — push your code and GitHub Actions scores you automatically (0–100 pts).


## 1. Simple API Fetcher
- **Task**: Write a Python script to fetch all "open" issues from a public GitHub repository.
- **Goal**: Master REST APIs and JSON parsing.
- **Constraint**: Use `requests` or `httpx`.

## 2. Basic LLM Prompt App
- **Task**: Create a script that takes a long article and outputs a 3-bullet point summary in JSON format.
- **Goal**: Master Prompt Engineering and System Prompts.
- **Constraint**: Output MUST be valid JSON (use `json.loads` to verify).

## 3. JSON to TOON Converter
- **Task**: Take a complex nested JSON object and manually (or via script) convert it to TOON format.
- **Goal**: Understand token efficiency.
- **Constraint**: Compare the character count between the two.

## 4. Simple Object Detection
- **Task**: Use YOLOv8 to detect vehicles in a still image of a traffic intersection.
- **Goal**: Get started with Computer Vision.
- **Constraint**: Print the number of cars detected.

## 5. RAG from Local TXT
- **Task**: Create a simple script that "reads" a text file about a generic topic and answers questions based *only* on that file.
- **Goal**: Understand context window injection.
- **Constraint**: If the answer isn't in the file, the script should say "I don't know".
