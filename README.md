
# AI Fraud Call Detection System 

An end-to-end AI-powered system that detects **fraudulent banking phone calls** by analyzing **audio conversations** using **speech recognition, identity verification, policy-based RAG, and large language models (LLMs)**.

This project simulates real-world banking fraud detection pipelines, focusing on **security, explainability, and modern AI architecture**.

<img width="926" height="413" alt="Image" src="https://github.com/user-attachments/assets/2b3fcb31-23b0-4b4c-b1cd-7d88f6aa56cb" />

## Features

- **Audio-based fraud detection** (not just text)
-  **Secure audio handling** using AES + RSA encryption
-  **Speech-to-Text** using OpenAI Whisper
- **Caller identity verification** using embeddings + cosine similarity
- **Policy-based fraud detection** using RAG (Pinecone + Sentence Transformers)
- **LLM reasoning** with LLaMA (via Ollama)
- **Evaluation metrics**: Accuracy, Precision, Recall, F1-score
- **Interactive Streamlit dashboard**

---

##  System Architecture
Audio Call (.wav)
↓
Encryption (AES + RSA)
↓
Decryption
↓
Whisper ASR (Speech → Text)
↓
Entity Extraction (LLM)
↓
Identity Verification (Embeddings)
↓
Policy Retrieval (Pinecone Vector DB)
↓
LLM-based Reasoning (RAG)
↓
Fraud / Normal Classification



## Project Structure



.
├── app.py # Streamlit UI
├── main_pipeline.py # Core fraud detection pipeline
├── dataset_generator.py # Synthetic dataset generation (TTS-based)
├── setup_dataset.py # Alternate dataset setup script
├── requirements.txt # Python dependencies
├── syntheticdataset100/
│ ├── calls/ # Generated call audio files
│ ├── Policies/ # Bank policy documents
│ └── employeelist/ # Employee lists per bank
└── README.md


---

##  Dataset

- **100 synthetic banking calls**
  - 50 Normal
  - 50 Fraudulent
- Generated using **Text-to-Speech**
- Includes:
  - Legitimate bank calls
  - Fraud scenarios (OTP theft, card details, urgent transfers)

⚠️ No real user data is used.

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit** (UI)
- **OpenAI Whisper** (ASR)
- **Sentence Transformers**
- **Pinecone Vector Database**
- **LLaMA (Ollama)**
- **Cryptography (AES + RSA)**
- **Scikit-learn**

---

## How to Run

### 1) Install Dependencies
```bash
pip install -r requirements.txt

2️) Generate Dataset
python dataset_generator.py

3️) Ensure Pinecone Index Exists

Index name: fraud-policies

Policies must be embedded and uploaded beforehand

4️) Start Ollama (LLaMA)
ollama run llama3:8b

5️) Run the App
streamlit run app.py

Evaluation Metrics
The system evaluates performance on all calls using:

Accuracy

Precision (Fraud class)

Recall (Fraud class)

F1 Score

Results are displayed directly in the Streamlit UI.

 Security Considerations

Audio data is encrypted before processing

No real banking or personal data is used

Designed for research and educational purposes only

 Use Cases

Banking fraud detection research

AI security demonstrations

Speech + NLP pipeline learning

RAG-based compliance systems

 Disclaimer

This project uses synthetic data only and is intended for academic and educational use.
It is not deployed in a real banking environment.

 Author

Sakshi Vispute

If you found this project helpful, feel free to ⭐ the repository!
