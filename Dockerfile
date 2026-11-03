FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/python
COPY python/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY python/ /app/python/
COPY ui/ /app/ui/
RUN useradd --system --uid 10001 app && mkdir -p /app/data && chown -R app /app
USER app
ENV DEMO_DATABASE=/app/data/workflows.db
EXPOSE 8000
CMD ["python","-m","uvicorn","financial-reconciliation-and-exception-workbench-python.app:app","--host","0.0.0.0","--port","8000"]
