FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

COPY agent-src/stagex2-source-package/stagex2-source-package/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r /app/requirements.txt

COPY agent-src/stagex2-source-package/stagex2-source-package/src /app/src
COPY agent-src/stagex2-source-package/stagex2-source-package/models.py /app/models.py
COPY agent-src/stagex2-source-package/stagex2-source-package/agent_output.py /app/agent_output.py
COPY agent-src/stagex2-source-package/stagex2-source-package/spacex2.1input-main.py /app/spacex2.1input-main.py
COPY agent-src/stagex2-source-package/stagex2-source-package/clearing_calibration_sample.json /app/clearing_calibration_sample.json

EXPOSE 8001

CMD ["uvicorn", "stagex2.api:app", "--host", "0.0.0.0", "--port", "8001"]
