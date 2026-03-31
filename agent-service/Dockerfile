FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r /app/requirements.txt

COPY src /app/src
COPY clearing_calibration_sample.json /app/clearing_calibration_sample.json

EXPOSE 8001

CMD ["uvicorn", "stagex2.api:app", "--host", "0.0.0.0", "--port", "8001"]
