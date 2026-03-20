FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
COPY models.py /app/models.py
COPY agent_output.py /app/agent_output.py
COPY spacex2.1input-main.py /app/spacex2.1input-main.py
COPY clearing_calibration_sample.json /app/clearing_calibration_sample.json

EXPOSE 8000

CMD ["uvicorn", "stagex2.api:app", "--host", "0.0.0.0", "--port", "8000"]
