FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Pass the key at runtime — do not bake secrets into the image:
#   docker build -t week-1v2 .
#   docker run --rm -p 8000:8000 -e OPENAI_API_KEY=sk-... week-1v2
#
# Optional Streamlit UI on another port:
#   docker run --rm -p 8501:8501 -e OPENAI_API_KEY=sk-... week-1v2 \
#     streamlit run demo_page.py --server.address 0.0.0.0 --server.port 8501
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
