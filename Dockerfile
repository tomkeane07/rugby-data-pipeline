FROM python:3.13

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Set working directory
WORKDIR /app
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--no-browser"]