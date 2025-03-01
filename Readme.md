# Zillow ETL Pipeline with Apache Airflow

## 📌 Project Overview

This project implements an **End-to-End ETL Pipeline** to extract real estate data from Zillow using **RapidAPI**, transform the data, and load it into **Amazon Redshift**. The workflow is orchestrated using **Apache Airflow** running on an **EC2 instance** to automate data ingestion and processing. The pipeline also integrates **AWS S3** for intermediate storage and **AWS QuickSight** for visualization.

## 🏗️ Tech Stack

- **Python** – Data extraction, transformation, and processing
- **Apache Airflow (on EC2)** – Workflow orchestration
- **RapidAPI** – Zillow API integration
- **Pandas & NumPy** – Data manipulation and transformation
- **Amazon Redshift** – Data warehouse storage
- **AWS S3** – Intermediate storage and backup
- **AWS Lambda** – Automated processing and transformation
- **AWS QuickSight** – Data visualization

## 📊 ETL Pipeline Workflow

1. **Extract**: Retrieve Zillow real estate data from RapidAPI using a Python script.
2. **Transform**: Convert JSON response to CSV format using **AWS Lambda** and Pandas.
3. **Load**: Store the processed CSV data in **Amazon S3** and then transfer it to **Amazon Redshift**.
4. **Automate**: Use **Apache Airflow (running on EC2)** to schedule and monitor the ETL jobs.
5. **Visualize**: Connect **Amazon Redshift** to **AWS QuickSight** for interactive data visualization and analysis.

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/zillow-etl-airflow.git
cd zillow-etl-airflow
```

### 2️⃣ Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Apache Airflow on AWS EC2
```bash
# Update packages and install dependencies
sudo apt update && sudo apt install -y python3-pip python3-venv

# Create a virtual environment and activate it
python3 -m venv airflow_venv
source airflow_venv/bin/activate

# Install Apache Airflow
pip install apache-airflow

# Initialize Airflow
airflow db init
airflow users create --username admin --password admin --firstname John --lastname Doe --role Admin --email admin@example.com

# Start Airflow web server and scheduler
airflow webserver --port 8080 &
airflow scheduler &

```

### 5️⃣Run the ETL Pipeline

- **Trigger DAG in Airflow UI**: Navigate to [`http://<EC2-PUBLIC-IP>:8080`](http://<EC2-PUBLIC-IP>:8080) and trigger the DAG manually.
- **Check Logs**: Monitor execution logs in Airflow UI.


