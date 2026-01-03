FROM python:3.11-slim

WORKDIR /app

# 가상환경 생성
RUN python -m venv /opt/venv
# 환경변수 설정 (Python 로그 버퍼링 방지)
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
