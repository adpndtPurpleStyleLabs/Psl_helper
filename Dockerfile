FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Expose the port that the app runs on
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
#CMD ["uvicorn", "VendorsInvoicePdfToExcel.Controller.VendorInvoiceController", "--host", "0.0.0.0", "--port", "8000"]
## Set the working directory to the desired folder
WORKDIR /VendorsInvoicePdfToExcel/Controller

CMD ["uvicorn", "VendorInvoiceController:app", "--host", "0.0.0.0", "--port", "8000"]