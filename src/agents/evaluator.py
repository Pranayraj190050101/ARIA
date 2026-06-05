from dotenv import load_dotenv
import os
import re

load_dotenv()

# ── Simple Guardrails ─────────────────────────────────────

# PII patterns
PII_PATTERNS = [
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',          # Phone numbers
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
    r'\b\d{3}-\d{2}-\d{4}\b',                   # SSN
    r'\b(?:\d[ -]*?){13,16}\b',                 # Credit card
]

# Prompt injection patterns
INJECTION_PATTERNS = [
    r'ignore previous instructions',
    r'ignore all instructions',
    r'forget everything',
    r'you are now',
    r'act as',
    r'jailbreak',
    r'bypass',
]


def check_pii(text: str) -> tuple[bool, str]:
    """
    Check if text contains PII.
    Returns (has_pii, cleaned_text)
    """
    cleaned = text
    has_pii = False

    for pattern in PII_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            has_pii = True
            cleaned = re.sub(pattern, "[REDACTED]", cleaned, flags=re.IGNORECASE)

    return has_pii, cleaned


def check_injection(text: str) -> bool:
    """
    Check if text contains prompt injection attempts.
    """
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def guard_input(query: str) -> tuple[bool, str]:
    """
    Guard the input query.
    Returns (is_safe, message)
    """
    # Check injection
    if check_injection(query):
        return False, "⚠️ Potential prompt injection detected. Query blocked."

    # Check PII in query
    has_pii, cleaned = check_pii(query)
    if has_pii:
        print(f"[Evaluator Agent] PII detected in query — redacted")
        return True, cleaned  # Allow but redacted

    return True, query


def guard_output(answer: str) -> str:
    """
    Guard the output answer — redact any PII that slipped through.
    """
    has_pii, cleaned = check_pii(answer)
    if has_pii:
        print(f"[Evaluator Agent] PII detected in answer — redacted")
    return cleaned


# ── RAGAS-style Evaluation ────────────────────────────────

def evaluate_response(
    query: str,
    answer: str,
    context_chunks: list[dict]
) -> dict:
    """
    Simple RAGAS-style evaluation metrics.
    """
    context_text = " ".join([c["content"] for c in context_chunks]).lower()
    answer_lower = answer.lower()
    query_lower = query.lower()

    # 1. Faithfulness — is answer grounded in context?
    answer_words = set(answer_lower.split())
    context_words = set(context_text.split())
    overlap = answer_words.intersection(context_words)
    faithfulness = round(len(overlap) / max(len(answer_words), 1), 2)
    faithfulness = min(faithfulness, 1.0)

    # 2. Answer Relevancy — does answer relate to query?
    query_words = set(query_lower.split())
    answer_query_overlap = answer_words.intersection(query_words)
    relevancy = round(len(answer_query_overlap) / max(len(query_words), 1), 2)
    relevancy = min(relevancy, 1.0)

    # 3. Context Precision — how much context is actually used?
    context_precision = round(len(overlap) / max(len(context_words), 1), 2)
    context_precision = min(context_precision, 1.0)

    metrics = {
        "faithfulness": faithfulness,
        "answer_relevancy": relevancy,
        "context_precision": context_precision,
        "overall_score": round((faithfulness + relevancy + context_precision) / 3, 2)
    }

    print(f"[Evaluator Agent] RAGAS Metrics: {metrics}")
    return metrics


def run_evaluator_agent(
    query: str,
    answer: str,
    context_chunks: list[dict]
) -> dict:
    """
    Full evaluation pipeline — guardrails + RAGAS metrics.
    """
    # Guard output
    safe_answer = guard_output(answer)

    # Evaluate
    metrics = evaluate_response(query, safe_answer, context_chunks)

    return {
        "answer": safe_answer,
        "metrics": metrics
    }