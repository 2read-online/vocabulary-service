FROM python:3.9 AS builder

WORKDIR /build
COPY requirements.txt .
COPY requirements/ requirements/

ARG REQUEREMENTS="requirements/prod.txt"
RUN pip install --user -r ${REQUEREMENTS}

FROM python:3.9-slim

COPY --from=builder /root/.local /root/.local/
ENV PATH=${PATH}:/root/.local/bin

WORKDIR /service

RUN python3 -m spacy download de_core_news_md
RUN python3 -m spacy download en_core_web_md
RUN python3 -m spacy download ru_core_news_md
RUN python3 -m spacy download fr_core_news_md
RUN python3 -m spacy download es_core_news_md

COPY app app
COPY requirements.txt .
COPY requirements/ requirements/

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0
