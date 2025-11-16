from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import os
import pandas as pd
import psycopg2
import subprocess

NASA_API_KEY = os.getenv("nasa_api_key", "ZCK0kL848fngn5PNf0PD2faqNzLt6WbjHU9C7rsZ")

# --- Helper function: Save metadata to Postgres ---
def save_to_postgres(data):
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", 5432)),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        dbname=os.getenv("POSTGRES_DB", "postgres")
    )

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS apod_data (
            date DATE PRIMARY KEY,
            title TEXT,
            url TEXT,
            explanation TEXT
        )
    """)
    cur.execute("""
        INSERT INTO apod_data (date, title, url, explanation)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (date) DO NOTHING
    """, (data["date"], data["title"], data["url"], data["explanation"]))
    conn.commit()
    cur.close()
    conn.close()

# --- DVC versioning function ---
def version_with_dvc():
    csv_path = "/usr/local/airflow/include/apod_data.csv"
    include_dir = "/usr/local/airflow/include"
    
    # Initialize DVC if not already done
    if not os.path.exists(os.path.join(include_dir, ".dvc")):
        subprocess.run(["dvc", "init", "--no-scm"], cwd=include_dir, check=False)
        print("DVC initialized")
    
    # Add CSV to DVC
    result = subprocess.run(
        ["dvc", "add", csv_path],
        cwd=include_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ CSV file tracked with DVC")
        print(f"DVC output: {result.stdout}")
        print(f"Generated: {csv_path}.dvc")
    else:
        print(f"⚠️ DVC add warning/error: {result.stderr}")
        print(f"This is normal if file is already tracked")

# --- Main function: Fetch APOD ---
def fetch_apod():
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    response = requests.get(url).json()

    # --- Save image ---
    img_url = response["url"]
    title = response["title"].replace(" ", "_")
    img_data = requests.get(img_url).content
    img_dir = "/usr/local/airflow/include/images"
    os.makedirs(img_dir, exist_ok=True)
    img_path = os.path.join(img_dir, f"{title}.jpg")
    with open(img_path, "wb") as f:
        f.write(img_data)
    print("Image saved to:", img_path)

    # --- Save metadata to CSV ---
    data = {
        "date": response["date"],
        "title": response["title"],
        "url": response["url"],
        "explanation": response["explanation"]
    }
    csv_path = "/usr/local/airflow/include/apod_data.csv"
    df = pd.DataFrame([data])
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)
    print("CSV saved to:", csv_path)

    # --- Save metadata to Postgres ---
    save_to_postgres(response)
    print("Data saved to Postgres.")

# --- Define DAG ---
with DAG(
    dag_id="nasa_apod_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["nasa", "etl", "mlops"],
    default_args={"retries": 2}
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_nasa_apod",
        python_callable=fetch_apod
    )
    
    dvc_task = PythonOperator(
        task_id="version_with_dvc",
        python_callable=version_with_dvc
    )
    
    # Task dependency: fetch data first, then version it
    fetch_task >> dvc_task