FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "web/app.py"]
