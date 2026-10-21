FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && addgroup --system app \
    && adduser --system --ingroup app app

COPY src ./src
COPY tests ./tests
COPY CONTEXT_RULES.md ./CONTEXT_RULES.md
COPY specs ./specs

RUN chown -R app:app /app
USER app

CMD ["python", "-m", "pytest", "tests/test_harness.py", "-v", "-p", "no:cacheprovider"]
