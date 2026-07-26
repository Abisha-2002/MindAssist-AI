# 🧠 MindAssist AI

> **🤖 Agentic Research Assistant for Depression Risk Prediction**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mindassist-aigit.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/Abisha-2002/MindAssist-AI)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)
![License](https://img.shields.io/badge/License-MIT-green)

# 📖 Project Description

MindAssist AI is an **Agentic AI-powered research assistant** developed for **Depression Risk Prediction**. It combines **multi-agent orchestration**, **Retrieval-Augmented Generation (RAG)**, **web search**, and **reflection-based validation** to provide reliable, evidence-based answers from trusted mental health resources.

The system indexes **26+ mental health PDFs** (PHQ-9, DASS-21, GAD-7, Sri Lankan Mental Health Reports, WHO Guidelines, IEEE papers, etc.) and retrieves the most relevant information before generating responses.

## 🎯 Problem Statement

Researchers and university students often struggle to find accurate mental health information because resources are scattered across numerous research papers, reports, and screening guidelines.

## 💡 Solution

MindAssist AI solves this by using an **Agentic AI workflow** that can:

- 🧠 Understand user intent
- 📚 Search local research documents using RAG
- 🌐 Search the web when required
- ✅ Validate and improve responses before presenting the final answer

# 🏗️ System Architecture
![Multi-Agent Workflow](images/Architecture.png)


# 🤖 Model Selection Strategy

| 🛠️ Sub-task | 🤖 Model / Provider | 💡 Reason for Selection |
|-------------|--------------------|--------------------------|
| 🎯 Intent Routing | Llama 3.1 8B (Groq) | Very low latency (~300ms), near-zero cost, ideal for classification |
| 🧠 Deep Reasoning | Llama 3.1 70B (OpenRouter) | Higher reasoning quality for medical responses |
| 🌍 Web Search | Serper API | Google-powered search with generous free tier |


# 🔄 Agent-to-Agent Communication

The agents communicate using structured **JSON messages**.

## 📦 Example JSON Message

```json
{
  "from": "Orchestrator",
  "to": "ResearchAgent",
  "payload": {
    "task": "rag_search",
    "query": "What is PHQ-9?",
    "k": 5
  },
  "metadata": {
    "intent": "literature_search",
    "message_id": 1
  }
}
```

## 🔁 Communication Flow
![Multi-Agent Workflow](images/Communication-Flow.png)



# 📚 Retrieval-Augmented Generation (RAG)

## 📖 Overview

MindAssist AI ingests **26+ mental health PDFs** and transforms them into searchable vector embeddings.


## ✂️ Chunking Strategy

| Parameter | Value |
|------------|--------|
| 📄 Chunk Size | 1000 Characters |
| 🔁 Chunk Overlap | 200 Characters |
| ✨ Separators | `\n\n`, `\n`, `.`, ` ` |



## 🧠 Embedding Model

| Item | Value |
|------|-------|
| Model | all-MiniLM-L6-v2 |
| Provider | Sentence Transformers |
| Embedding Size | 384 Dimensions |



## 🗂️ Vector Database

| Feature | Value |
|----------|--------|
| Database | ChromaDB |
| Search Method | Cosine Similarity |



## 📊 Retrieval Evaluation

| 🔍 Query | 📄 Retrieved Context | ✅ Relevance |
|-----------|---------------------|--------------|
| What is PHQ-9 and how is it scored? | PHQ-9 Scoring Guide | ⭐ 0.89 |
| Depression prevalence in Sri Lanka | Mental Health Report | ⭐ 0.85 |
| Latest ML techniques | IEEE Research Papers | ⭐ 0.82 |
| Depression Risk Factors | Student Mental Health Study | ⭐ 0.78 |
| Difference between DASS-21 and PHQ-9 | Screening Questionnaires | ⭐ 0.87 |

---

# ⚙️ Installation Guide

## 📥 Clone Repository

```bash
git clone https://github.com/Abisha-2002/MindAssist-AI.git
cd MindAssist-AI
```



## 🐍 Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Configure API Keys

Create:

```
.streamlit/secrets.toml
```

Add:

```toml
GROQ_API_KEY="gsk_your_key"

OPENROUTER_API_KEY="sk-or-v1_your_key"

SERPER_API_KEY="your_key"
```

---

## 📂 Add Research PDFs

Place all PDFs inside

```
data/pdfs/
```



## ▶️ Run Streamlit

```bash
streamlit run app.py
```


# 🚀 Live Demo

🌐 **Streamlit Application**

https://mindassist-aigit.streamlit.app

![Multi-Agent Workflow](images/out1.jpeg)
![Multi-Agent Workflow](images/out2.jpeg)
![Multi-Agent Workflow](images/out3.jpeg)
![Multi-Agent Workflow](images/out4.jpeg)

# 📂 Project Structure

```text
MindAssist-AI
│
├── agents/
│   ├── router_agent.py
│   ├── orchestrator.py
│   ├── research_agent.py
│   └── reflection_agent.py
│
├── rag/
│   ├── loader.py
│   └── embeddings.py
│
├── tools/
│   └── web_search.py
│
├── data/
│   └── pdfs/
│
├── utils/
│
├── app.py
├── requirements.txt
└── README.md
```

---

# 🌐 Deployment

### 🚀 Streamlit Community Cloud

✅ GitHub Repository Connected

✅ Secrets Configured

✅ Automatic Deployment Enabled

---

# ⚠️ Known Limitations

| ⚠️ Limitation | 📌 Description |
|---------------|----------------|
| 📄 Large PDFs | Loading large documents takes longer |
| 🌍 Search Limits | Serper API allows ~2,500 free searches/month |
| ⏱️ Rate Limits | Groq & OpenRouter free tiers have usage limits |
| 🗂️ Vector Database | ChromaDB rebuilds on deployment |
| 🌐 Language Support | Currently optimized for English |

---

# 🔀 GitHub Workflow

## 🌿 Branch Strategy

- ✅ main
- ✅ feature/rag-pipeline
- ✅ feature/agent-orchestration
- ✅ feature/model-router
- ✅ feature/streamlit-ui
- ✅ feature/web-search

---

## 💬 Commit Convention

```text
feat:
fix:
docs:
style:
refactor:
test:
chore:
```



# ✅ Assignment Requirements Checklist

| Requirement | Status |
|-------------|--------|
| 🤖 Agentic Design Patterns (≥3) | ✅ Completed |
| 🔄 Agent Communication | ✅ JSON Messaging |
| 🧠 Multi-Model Strategy | ✅ Groq + OpenRouter |
| 📚 RAG Pipeline (20+ PDFs) | ✅ 26 Documents |
| 🌐 Streamlit Deployment | ✅ Live |
| 🔀 GitHub Workflow | ✅ Branches + PRs + Commits |



# 🛠️ Technologies Used

- 🐍 Python
- 🎈 Streamlit
- 🧠 LangChain
- 🤖 Groq API
- 🌐 OpenRouter API
- 🔍 Serper API
- 📚 ChromaDB
- 🔡 Sentence Transformers
- 📝 HuggingFace Embeddings



# 📸 Workflow Summary

![Multi-Agent Workflow](images/multi-agent-workflow.png)



# 👨‍💻 Author

## 👤 Abisha Wesly Jeyananthan

🎓  undergraduate at Horizon Campus

💻 BSc (Hons) Information Technology

📚 IT41043 – Intelligent Systems

🤖 Agentic AI Assignment


# ⭐ If you found this project useful

Please consider giving it a ⭐ on GitHub!

> **🧠 MindAssist AI — Empowering Depression Risk Research with Agentic AI, RAG, and Multi-Agent Intelligence.**

