# Use a minimal Python base imag for a smaller container size (no extra OS packages).

FROM python:3.12-slim
# Install packages earlier so whenever source code is altered, docker can skip pip install step on every rebuild where 
# dependancies haventt changed

# Set the directory inside container
WORKDIR /app

# Copy requirements first to leverage docker layer caching whenever only source code is altered
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application code
COPY . .
# By doing this later, only the final layer will be rebuilt when editing Python files..

# Dcoument port the container lists on
EXPOSE 8000

# to start the ASGI server when container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# --host 0.0.0.0 to make uvicorn listen on all network interafaces so traffic can be routed to container


