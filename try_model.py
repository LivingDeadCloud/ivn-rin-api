from transformers import pipeline

# Define NER model
MODEL_ID = "IVN-RIN/MedPsyNIT"

ner = pipeline(
    "token-classification",
    model=MODEL_ID,
    aggregation_strategy="simple",  # merge sub-tokens into whole entities
    device="cpu"
)

testo = "Il paziente presenta cefalea e assume paracetamolo 1000 mg."
for ent in ner(testo):
    print(ent["entity_group"], "|", ent["word"], "|", round(float(ent["score"]), 3))