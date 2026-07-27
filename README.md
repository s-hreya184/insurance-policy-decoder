## Overview of the problem
Legal documentation can be a complicated and time-consuming process, especially for individuals and small
businesses who may not have access to legal resources. In addition, the language and jargon used in legal documents
can be difficult for non-lawyers to understand, which can lead to errors and misunderstandings

## Objective
To simplify legal documentation by automatically decoding legal documents in plain language and using easy-to-understand terms

## LegalX - AI-powered Legal Documentation Assistant
A Streamlit app that lets a user upload a health insurance policy PDF and:
- Get a plain-English summary and risk score (waiting periods, co-payments, hidden limits, exclusions) via Groq's LLM API.
- Chat with the document using a RAG pipeline (LlamaIndex + local HuggingFace embeddings + in-memory ChromaDB) so answers are grounded in the retrieved policy text.

## Features
 1. User-friendly interface for inputting relevant information such as their policy cover, potential diseases, age, etc for a Personalized Risk Profiling
 2. Ability to customize legal documents based on the specific needs of the user.
 3. Insurance Vulnerability Score.
 4. Indicates financial exposure level
 5. Identifies top risk drivers and “What’s Not Covered”
 6. High-Risk Clauses, Detects waiting periods, Identifies co-payment clauses, Flags disease-specific exclusions

## Impact 
Impact: The proposed solution can greatly benefit individuals and small businesses in India, who often
face challenges with legal documentation due to limited access to legal resources. By simplifying legal documentation,
this solution can potentially save time and reduce financial exposure during crisis

## Snapshots of Protoype
<img width="2204" height="928" alt="image" src="https://github.com/user-attachments/assets/a68be49b-7a39-4338-8540-2c087862a489" />
<img width="2277" height="873" alt="image" src="https://github.com/user-attachments/assets/5ded67ee-2e19-4cd2-a7e1-d92a88fa1ab5" />
<img width="2302" height="924" alt="image" src="https://github.com/user-attachments/assets/311fecc1-015e-48cd-9c9e-4c67b25adcc8" />
<img width="2272" height="929" alt="image" src="https://github.com/user-attachments/assets/195b0574-c410-462b-8b80-8ce3dc186392" />
<img width="2274" height="1058" alt="image" src="https://github.com/user-attachments/assets/85e15003-0303-486a-8c53-3d3aa457dc00" />
<img width="2268" height="845" alt="image" src="https://github.com/user-attachments/assets/b96a05c7-24f9-4031-9864-89dfac5f39fc" />
<img width="2360" height="1030" alt="image" src="https://github.com/user-attachments/assets/31406042-eedb-49d6-9305-14bdc633ec3f" />
<img width="2350" height="1142" alt="image" src="https://github.com/user-attachments/assets/9c2f62d2-3250-49e6-821e-9e274a1b96dd" />

## Tech Stack
- **UI**: Streamlit (`app.py`)
- **PDF parsing**: `pdfplumber` (`pdf_utils.py`)
- **LLM calls**: Groq API (`llm.py`, model `llama-3.1-8b-instant`)
- **RAG**: LlamaIndex + HuggingFace `BAAI/bge-small-en-v1.5` embeddings + ChromaDB, in-memory and session-scoped (`rag.py`, `rag_qa.py`)
- **Risk scoring**: `risk_engine.py`
## Run Locally

Install dependencies:

pip install -r requirements.txt

Start app:

streamlit run app.py

##Secrets
- `GROQ_API_KEY` — required for both the summarizer LLM calls and the RAG chat engine.

## Collaborators
Shreya Babar
Rutuja Zawar
