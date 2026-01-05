import os
import random
from pathlib import Path
import pandas as pd
from gtts import gTTS

# BANK DEFINITIONS — Using BankA, BankB, BankC


NORMAL_TEMPLATES = [
    "Hello, this is {emp} calling from {bank}. I just need to {intent}.",
    "Hi, this is {emp} with {bank}. I am reaching out to {intent}.",
    "Greetings, this is {emp} from {bank}. I would like to quickly {intent}.",
]

FRAUD_TEMPLATES = [
    "URGENT! This is {emp} from {bank}. You must immediately {intent}.",
    "Attention! I am {emp} with {bank}. Please quickly {intent}.",
    "This is {emp} from {bank}. Your account is at danger. Immediately {intent}.",
]

BANKS = {
    "BankA": {
        "normal": [
            "confirm your contact information",
            "ask for feedback on our new digital features",
            "verify the last four digits of your SSN",
        ],
        "fraud": [
            "provide your full card number and CVV",
            "share your online banking password",
            "transfer your money to a safe account immediately",
        ]
    },
    "BankB": {
        "normal": [
            "verify recent transactions",
            "confirm last four digits of your account number",
            "assist you with an account inquiry",
        ],
        "fraud": [
            "download a remote access tool",
            "share your entire debit card information",
            "approve a high-value transfer right now",
        ]
    },
    "BankC": {
        "normal": [
            "ask for feedback on our banking services",
            "participate in a brief customer survey",
            "confirm your identity using simple details",
        ],
        "fraud": [
            "install a security application immediately",
            "provide your ATM PIN for verification",
            "complete a large transfer urgently",
        ]
    }
}

EMPLOYEES = {
    "BankA": ["Alex", "Rohan", "Priya", "Nina", "Ryan"],
    "BankB": ["Sam", "Karan", "Sneha", "Aarav", "Mira"],
    "BankC": ["John", "Sara", "Isha", "Kabir", "Diya"],
}

# CREATE FOLDERS


def create_folders():
    base = Path("syntheticdataset100")
    (base / "calls").mkdir(parents=True, exist_ok=True)
    (base / "Policies").mkdir(parents=True, exist_ok=True)
    (base / "employeelist").mkdir(parents=True, exist_ok=True)
    print("✔ Folder structure created.")



# GENERATE EMPLOYEE LIST CSVs

def generate_employee_lists():
    emp_dir = Path("syntheticdataset100/employeelist")

    for bank, names in EMPLOYEES.items():
        df = pd.DataFrame({"name": names})
        df.to_csv(emp_dir / f"employees-{bank}.csv", index=False)

    print("✔ Employee list CSVs created.")



# GENERATE POLICIES


def generate_policies():
    policy_dir = Path("syntheticdataset100/Policies")

    policy_text_bankA = """
BankA Policy:
- Never ask customers for full card details.
- Do not request CVV, PIN, or passwords.
- Verify identity using only the last 4 digits.
- Never ask to install any remote access tools.
"""

    policy_text_bankB = """
BankB Policy:
- Never ask customers to transfer money urgently.
- Do not request complete account numbers.
- Only verify last 4 digits or DOB.
- Never ask customers to share OTP, CVV, or PIN.
"""

    policy_text_bankC = """
BankC Policy:
- Never request ATM PIN or full card number.
- Do not ask customers to install unauthorized security apps.
- Identity verification must be minimal.
- No remote access instructions are permitted.
"""

    policy_files = {
        "BankA_Policy.txt": policy_text_bankA,
        "BankB_Policy.txt": policy_text_bankB,
        "BankC_Policy.txt": policy_text_bankC,
    }

    for filename, content in policy_files.items():
        with open(policy_dir / filename, "w") as f:
            f.write(content.strip())

    print("✔ Policies created.")



# TEXT → AUDIO FUNCTION


def text_to_audio(text, file_path):
    tts = gTTS(text=text, lang='en')
    tts.save(str(file_path))



# GENERATE A SINGLE CALL (normal or fraud)


def generate_single_call(bank, label):

    emp = random.choice(EMPLOYEES[bank])

    if label == "normal":
        intent = random.choice(BANKS[bank]["normal"])
        template = random.choice(NORMAL_TEMPLATES)
    else:
        intent = random.choice(BANKS[bank]["fraud"])
        template = random.choice(FRAUD_TEMPLATES)

    return template.format(emp=emp, bank=bank, intent=intent)



# GENERATE ALL 100 CALLS


def generate_calls():
    calls_dir = Path("syntheticdataset100/calls")
    count = 1

    # 50 Normal calls
    for _ in range(50):
        bank = random.choice(["BankA", "BankB", "BankC"])
        text = generate_single_call(bank, "normal")
        out = calls_dir / f"Normal_call_{count}_{bank}.wav"
        text_to_audio(text, out)
        count += 1

    # 50 Fraud calls
    for _ in range(50):
        bank = random.choice(["BankA", "BankB", "BankC"])
        text = generate_single_call(bank, "fraud")
        out = calls_dir / f"Fraudulent_call_{count}_{bank}.wav"
        text_to_audio(text, out)
        count += 1

    print("100 Calls generated (50 Normal, 50 Fraudulent).")



# MAIN CONTROLLER


def setup_all():
    print("\n========== DATASET SETUP STARTED ==========\n")
    create_folders()
    generate_employee_lists()
    generate_policies()
    generate_calls()
    print("\n Dataset setup complete!.\n")


if __name__ == "__main__":
    setup_all()
