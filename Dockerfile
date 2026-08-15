FROM python:3.12-slim
WORKDIR /app
COPY . .
ENV HOST=0.0.0.0
ENV PORT=5173
ENV PUBLIC_URL=https://alvaloja.store
EXPOSE 5173
CMD ["python", "-u", "server.py"]
