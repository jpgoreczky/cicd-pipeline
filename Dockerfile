# Official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing.pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file initially
COPY requirements.txt .

# Install dependencies without caching pip data
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY./app./app

# Expose the port the application will run on
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]