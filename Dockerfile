FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
ENV PORT=8000
EXPOSE 8000

# --proxy-headers/--forwarded-allow-ips make uvicorn trust the
# X-Forwarded-Proto header Render's edge proxy sets, so the app sees
# "https" instead of "http" (this matters for the QR code / join link
# generation in app/routes/api.py, which reads request.url.scheme).
# Safe here because Render puts the container behind its own proxy with
# no other path for an untrusted client to reach uvicorn directly.
#
# Never add --workers or run more than one instance: app/store.py is a
# plain in-process dict, not shared across processes.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
