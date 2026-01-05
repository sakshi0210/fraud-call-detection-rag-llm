
# app.py — Streamlit GUI 


import streamlit as st
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from main_pipeline import cfg, init_pipeline, analyze_call


# Load pipeline once

@st.cache_resource
def get_pipeline_objects():
    return init_pipeline()

st.set_page_config(page_title="Fraud Call Detection", layout="wide")

st.title("Fraud Call Detection System")

st.write(
    "This app analyzes synthetic bank calls and predicts whether each call is "
    "**Fraud** or **Normal** using the full pipeline "
    "(Encryption → Whisper ASR → Identity Verification → RAG → LLaMA)."
)

with st.spinner("Loading models & Pinecone…"):
    enc, idv, rag, asr = get_pipeline_objects()

st.markdown("---")

# ------------------------------------------------------------
# Permission
# ------------------------------------------------------------
st.subheader("Permission to Analyze Calls")
choice = st.radio("Do you want to analyze a call?", ["No", "Yes"], index=0)

audio_files = sorted(Path(cfg.AUDIODIR).glob("*.wav"))

if choice == "Yes":
    if not audio_files:
        st.error(
            f"No .wav files found in {cfg.AUDIODIR}.\n\n"
            "Please run dataset_generator.py to create your dataset."
        )
        st.stop()

    max_calls = len(audio_files)

    
    # SINGLE CALL ANALYSIS
    
    st.subheader("Analyze a Single Call")

    call_no = st.number_input(
        f"Select Call Number (1–{max_calls})",
        min_value=1, max_value=max_calls, value=1, step=1
    )

    if st.button("Analyze Selected Call", key="analyze_single"):
        path = audio_files[call_no - 1]

        with st.spinner(f"Analyzing {path.name}…"):
            fname, true, pred, correct = analyze_call(path, enc, idv, rag, asr)

        st.markdown("### Result")
        st.write(f"**File Name:** {fname}")
        st.write(f"**True Label:** {true}")
        st.write(f"**Predicted Label:** {pred}")

        # AUDIO PLAYER
        st.audio(str(path))

        if correct:
            st.success("Prediction: **CORRECT**")
        else:
            st.error("Prediction: **WRONG**")

    st.markdown("---")

    
    # FULL MODEL EVALUATION
   
    st.subheader("Evaluate Model on ALL Calls")

    if st.button("Run Full Evaluation (All Calls)", key="evaluate_all"):
        true_labels = []
        pred_labels = []

        with st.spinner("Running evaluation over all calls…"):
            for path in audio_files:
                fname, true, pred, correct = analyze_call(path, enc, idv, rag, asr)
                true_labels.append(true)
                pred_labels.append(pred)

        # Compute metrics
        acc = accuracy_score(true_labels, pred_labels)
        prec = precision_score(true_labels, pred_labels, pos_label="Fraud")
        rec = recall_score(true_labels, pred_labels, pos_label="Fraud")
        f1 = f1_score(true_labels, pred_labels, pos_label="Fraud")

        st.markdown("### Model Evaluation Metrics")
        st.write(f"**Accuracy:** {acc:.4f}")
        st.write(f"**Precision:** {prec:.4f}")
        st.write(f"**Recall:** {rec:.4f}")
        st.write(f"**F1 Score:** {f1:.4f}")

else:
    st.info("Select **Yes** above when you are ready to analyze a call.")
