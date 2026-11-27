# IVN-RIN NER API

A REST API that serves an Italian biomedical Named Entity Recognition (NER) model, built to bring one of my open-source [IVN-RIN models](https://huggingface.co/IVN-RIN) (100k+ downloads on Hugging Face) from research to a production-style service.

Given a clinical text in Italian, the API returns the recognized entities (e.g. drug treatments, diagnoses), with their position in the text and a confidence score.

> **Work in progress.** This project is being extended step by step with Docker, tests and CI/CD,
> cloud deployment on AWS, model registry and monitoring (see [Roadmap](#roadmap)).

## Model

The model is [MedPsyNIT](https://huggingface.co/IVN-RIN/MedPsyNIT), built on top of [BioBIT](https://huggingface.co/IVN-RIN/bioBIT), and developed in my research on information extraction from Italian clinical notes: we created [PsyNIT](https://huggingface.co/datasets/IVN-RIN/PsyNIT), the first Italian neuropsychiatric NER dataset, and combined it with three external datasets to train a multicenter model (F1-score 84.77%, precision 83.16%, recall 86.44%).

- **Model:** [`IVN-RIN/MedPsyNIT`](https://huggingface.co/IVN-RIN/MedPsyNIT)
- **Paper:** Crema C. et al., ["Advancing Italian biomedical information extraction with transformers-based models: Methodological insights and multicenter practical application"](https://doi.org/10.1016/j.jbi.2023.104557), *Journal of Biomedical Informatics*, 148, 104557 (2023)
- **Task:** token classification (NER) on Italian clinical text
- **Entity types:**
    - *Diagnosis and comorbidities*
    - *Cognitive symptoms*
    - *Neuropsychiatric symptoms*
    - *Drug treatment*
    - *Medical assessment*

## Features

- `POST /ner`: extracts entities from a text, returns JSON with label, text span, character offsets and score
- `GET /health`: health check endpoint, for load balancers and post-deploy smoke tests
- **Input validation** with Pydantic: empty, blank or too long texts (> 5,000 characters) are rejected with `422`
- **Long texts:** inputs over the model's 512-token limit are processed with a sliding window (`stride`),
  so entities at the end of long clinical notes are not lost
- **Error handling:** model failures return a generic `500`, with the details logged server-side only
- **Interactive API documentation (OpenAPI)**, generated automatically at `/docs`
- Runs on **CPU**

## Quick start

Requirements: Python 3.10+, Linux or macOS.

```bash
git clone https://github.com/LivingDeadCloud/ivn-rin-api.git
cd ivn-rin-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
```

The model (~440 MB) is downloaded from Hugging Face on the first start, then cached.

The API is available at `http://127.0.0.1:8000`, the interactive documentation at `http://127.0.0.1:8000/docs`.

## Usage

### Extract entities

```bash
curl -X POST http://127.0.0.1:8000/ner \
  -H "Content-Type: application/json" \
  -d '{"text": "Il paziente presenta cefalea e assume paracetamolo 1000 mg."}'
```

Response:

```json
{
  "entities": [
    {
      "label": "TRATTAMENTO FARMACOLOGICO (B)",
      "text": "paracetamolo",
      "score": 0.9258,
      "start": 38,
      "end": 50
    }
  ]
}
```

`start` and `end` are character offsets in the input text: `text[start:end]` is the entity.

### Health check

```bash
curl http://127.0.0.1:8000/health
```

```json
{"status": "ok", "model": "IVN-RIN/<model-name>"}
```

### Errors

| Status | When |
|---|---|
| `422` | Missing, empty or blank `text`, or longer than 5,000 characters |
| `500` | Unexpected model failure |

## Tech stack

Python, FastAPI, Pydantic, Hugging Face Transformers, PyTorch (CPU).

## Roadmap

- [x] REST API around the model, with validation, error handling and health check
- [ ] Docker image
- [ ] Tests (`pytest`) and CI with GitHub Actions
- [ ] Deployment on AWS (ECR, ECS Fargate)
- [ ] Experiment tracking and model registry with MLflow
- [ ] Continuous deployment from GitHub Actions to AWS
- [ ] Monitoring: structured logs, metrics, data drift

## Citation

If you use this model, please cite:

```bibtex
@article{CREMA2023104557,
  title   = {Advancing Italian biomedical information extraction with transformers-based models: Methodological insights and multicenter practical application},
  author  = {Crema, Claudio and Buonocore, Tommaso Mario and Fostinelli, Silvia and Parimbelli, Enea and Verde, Federico and Fundar{\`o}, Cira and Manera, Marina and Cotta Ramusino, Matteo and Capelli, Marco and Costa, Alfredo and Binetti, Giuliano and Bellazzi, Riccardo and Redolfi, Alberto},
  journal = {Journal of Biomedical Informatics},
  volume  = {148},
  pages   = {104557},
  year    = {2023},
  doi     = {10.1016/j.jbi.2023.104557}
}
```

## Notes

Example texts in this repository are synthetic. No real patient data is used.