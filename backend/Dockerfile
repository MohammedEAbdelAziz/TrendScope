FROM python:3.12

WORKDIR /app

# (Full image includes all system dependencies like libgomp1 and ca-certificates)

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Copy application code
COPY . .

# Copy the locally built quantized model
COPY model_quantized/ ./model_quantized/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
