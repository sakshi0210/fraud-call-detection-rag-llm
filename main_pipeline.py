
# main_pipeline.py — core logic only (NO GUI)

import os
import re
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import whisper
from json_repair import repair_json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pinecone import Pinecone  #   pinecone v8 import

from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import hashes, padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# CONFIG

class Config:
    INDEX_NAME = "fraud-policies"
    BASEDIR = "syntheticdataset100"
    AUDIODIR = f"{BASEDIR}/calls"
    POLICYDIR = f"{BASEDIR}/Policies"
    EMPLOYEEDIR = f"{BASEDIR}/employeelist"
    ASR_MODEL = "small"
    EMB_MODEL = "all-MiniLM-L6-v2"
    TOPK = 10
    SIM_THRESH = 0.72


cfg = Config()

#  Pinecone API key 
PINECONE_API_KEY = "pcsk_TSGAH_T9sAfK9ZqhfyXWfB158zrQVZQgyzyNakpSDEW2PRmf4wcxkLwProZg3dhSjegxo"  # <- <-- EDIT THIS



# ENCRYPTION (AES+RSA)

class EncryptionManager:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def encrypt(self, data: bytes):
        aes_key = os.urandom(32)
        iv = os.urandom(16)

        padder = sym_padding.PKCS7(128).padder()
        padded = padder.update(data) + padder.finalize()

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        enc = encryptor.update(padded) + encryptor.finalize()

        enc_key = self.public_key.encrypt(
            aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return enc, enc_key, iv

    def decrypt(self, ciphertext: bytes, encrypted_key: bytes, iv: bytes):
        aes_key = self.private_key.decrypt(
            encrypted_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        dec = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = sym_padding.PKCS7(128).unpadder()
        return unpadder.update(dec) + unpadder.finalize()



# IDENTITY VERIFIER

class IdentityVerifier:
    def __init__(self, embedder, employeedir, sim_thresh=cfg.SIM_THRESH):
        self.embedder = embedder
        self.sim_thresh = sim_thresh
        self.db = {}
        self.db_embs = {}

        for f in Path(employeedir).glob("*.csv"):
            bank = f.stem.split("-")[-1]
            names = pd.read_csv(f)["name"].tolist()
            self.db[bank] = names
            embs = embedder.encode(names, convert_to_numpy=True)
            self.db_embs[bank] = embs

    def verify(self, name, company):
        if company not in self.db:
            return {"Answer": "Fraud"}
        if not name:
            return {"Answer": "Fraud"}

        q = self.embedder.encode([name], convert_to_numpy=True)
        sims = cosine_similarity(q, self.db_embs[company])[0]

        if float(np.max(sims)) < self.sim_thresh:
            return {"Answer": "Fraud"}
        return {"Answer": "Normal"}



# OLLAMA + POLICY RAG

def ollama_chat(prompt: str) -> str:
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3:8b",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.0,
        "format": "json",
    }
    try:
        resp = requests.post(url, json=payload, timeout=60)
        return resp.json()["message"]["content"]
    except Exception:
        return ""


class PolicyRAG:
    def __init__(self, embedder, index):
        self.emb = embedder
        self.index = index

    def extract(self, text: str):
        prompt = f"""Extract ONLY JSON:
{{"employee_name":"","company_name":""}}
Conversation:
{text}"""

        raw = ollama_chat(prompt)

        try:
            fixed = repair_json(raw)
            data = json.loads(fixed)
            return data.get("employee_name", ""), data.get("company_name", "")
        except Exception:
            emp = re.search(r"(Name\d+|Scammer)", text)
            comp = re.search(r"Bank[A-C]", text)
            return (
                emp.group(0) if emp else "",
                comp.group(0) if comp else "",
            )

    def check(self, transcript: str, company: str):
        q = self.emb.encode(transcript[:500]).tolist()
        # new pinecone v8 query API
        res = self.index.query(vector=q, top_k=cfg.TOPK, include_metadata=True)

        # res.matches is a list of ScoredVector objects
        docs = []
        for m in res.matches:
            md = getattr(m, "metadata", None) or {}
            txt = md.get("text")
            if txt:
                docs.append(txt)

        context = "\n".join(docs)

        prompt = f"""Return ONLY JSON:
{{"label":"Fraud","justification":""}}
Policies:
{context}
Call:
{transcript}"""

        raw = ollama_chat(prompt)

        try:
            fixed = repair_json(raw)
            data = json.loads(fixed)
            return data.get("label", "Fraud")
        except Exception:
            return "Fraud"



# INIT PIPELINE (load models once)

def init_pipeline():
    """
    Initializes:
    - Pinecone client + connects to existing index `fraud-policies`
    - SentenceTransformer embedding model
    - Whisper ASR model
    - Encryption manager
    - Identity verifier
    - Policy RAG
    """

    # Pinecone v8 client
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(cfg.INDEX_NAME)  # assumes index already created and populated

    emb = SentenceTransformer(cfg.EMB_MODEL)
    asr = whisper.load_model(cfg.ASR_MODEL)
    enc = EncryptionManager()
    idv = IdentityVerifier(emb, cfg.EMPLOYEEDIR)
    rag = PolicyRAG(emb, index)

    return enc, idv, rag, asr


# SINGLE CALL ANALYSIS (used by Streamlit)

def analyze_call(path: Path, enc, idv, rag, asr):
    """
    Full pipeline for one call:
    1) Encrypt + decrypt audio (AES+RSA)
    2) Transcribe with Whisper
    3) Extract employee + company with LLaMA
    4) Identity verification
    5) Policy + RAG fraud/normal decision
    6) Compare with true label from filename
    """
    raw = path.read_bytes()
    e, ek, iv = enc.encrypt(raw)
    dec = enc.decrypt(e, ek, iv)

    temp = "temp.wav"
    Path(temp).write_bytes(dec)
    transcript = asr.transcribe(temp)["text"]
    os.remove(temp)

    emp, comp = rag.extract(transcript)
    id_res = idv.verify(emp, comp)

    if id_res["Answer"] == "Fraud":
        pred = "Fraud"
    else:
        pred = rag.check(transcript, comp)

    true = "Fraud" if "Fraudulent" in path.name else "Normal"
    correct = (true == pred)

    return path.name, true, pred, correct
