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

COPY  app app

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0
