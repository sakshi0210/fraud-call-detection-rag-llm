import os
import random
from pathlib import Path
import pandas as pd
import pyttsx3
import time

# =====================================================
# CONFIG
# =====================================================
BASEDIR = "syntheticdataset100"
AUDIODIR = f"{BASEDIR}/calls"
POLICYDIR = f"{BASEDIR}/Policies"
EMPLOYEEDIR = f"{BASEDIR}/employeelist"

# Create folders
os.makedirs(AUDIODIR, exist_ok=True)
os.makedirs(POLICYDIR, exist_ok=True)
os.makedirs(EMPLOYEEDIR, exist_ok=True)

# =====================================================
# OFFLINE TTS ENGINE (pyttsx3)
# =====================================================
engine = pyttsx3.init()
engine.setProperty("rate", 160)

def text_to_audio(text, out_file):
    """Convert text → WAV using offline pyttsx3."""
    try:
        engine.save_to_file(text, out_file)
        engine.runAndWait()
    except Exception as e:
        print(f"❌ TTS ERROR for file: {out_file} — {e}")

# =====================================================
# EMPLOYEE LISTS
# =====================================================
banks = ["BankA", "BankB", "BankC"]

for bank in banks:
    names = [f"Name{i}" for i in range(1, 6)]
    df = pd.DataFrame({"name": names})
    df.to_csv(f"{EMPLOYEEDIR}/{bank}.csv", index=False)

print("✔ Employee lists created.")

# =====================================================
# POLICIES
# =====================================================
policy_text = (
    "Never share full card details. "
    "Never share OTP. "
    "Verify last four digits only. "
    "Do not approve large transfers without manager. "
)

for bank in banks:
    with open(f"{POLICYDIR}/{bank}.txt", "w") as f:
        f.write((policy_text + "\n") * 40)

print("✔ Policies created.")

# =====================================================
# CALL SCRIPTS
# =====================================================
NORMAL = [
    "Hello this is {emp} calling from {bank}. Please verify the last four digits of your card.",
    "Your payment has been processed successfully.",
    "We detected a login attempt. Please confirm if it was you."
]

FRAUD = [
    "Urgent! Share your full card number immediately to avoid charges.",
    "I need your OTP right now to prevent account blocking.",
    "Transfer ten thousand rupees immediately or your account will be frozen!"
]

# =====================================================
# GENERATE 100 CALLS (50 Normal + 50 Fraud)
# =====================================================
call_id = 1
print("\n========== GENERATING CALLS ==========")

for label, scripts, count in [
    ("Normal", NORMAL, 50),
    ("Fraudulent", FRAUD, 50),
]:

    for _ in range(count):
        bank = random.choice(banks)
        emp = random.choice([f"Name{i}" for i in range(1, 6)])

        if label == "Fraudulent" and random.random() < 0.4:
            emp = "Scammer"

        text = random.choice(scripts).format(emp=emp, bank=bank)

        out_path = f"{AUDIODIR}/{label}_{bank}_{call_id:03d}.wav"

        print(f"[{call_id}/100] Generating → {out_path}")

        text_to_audio(text, out_path)
        time.sleep(0.1)  # small delay helps pyttsx3 avoid missing files

        call_id += 1

print("\n✔ Dataset generation completed successfully.")
print("✔ 100 WAV files saved in:", AUDIODIR)
