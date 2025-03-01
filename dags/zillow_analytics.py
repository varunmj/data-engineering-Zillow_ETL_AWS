from airflow import DAG
from datetime import timedelta, datetime
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.decorators import task
import json
import requests

# Load API credentials
with open('/home/ubuntu/airflow/config_api.json', 'r') as config_file:
    api_host_key = json.load(config_file)

dt_now_string = datetime.now().strftime('%d-%m-%Y-%H:%M:%S')

s3_bucket = 'zillow-stage3-transformed-data-bucket'


def extract_zillow_data(**kwargs):
    url = kwargs['url']
    headers = kwargs['headers']
    querystring = kwargs['querystring']
    dt_string = kwargs['date_string']

    response = requests.get(url, headers=headers, params=querystring)
    response_data = response.json()

    output_file_path = f"/home/ubuntu/response_data_{dt_string}.json"
    file_str = f"response_data_{dt_string}.csv"

    with open(output_file_path, 'w') as output_file:
        json.dump(response_data, output_file, indent=4)

    return [output_file_path, file_str]  # Store filename in XCom

#Fetch latest file from S3
@task(task_id="fetch_latest_s3_file")
def get_latest_s3_file(bucket_name, prefix="response_data"):
    """Fetch the most recent file from S3 matching the given prefix"""
    s3_hook = S3Hook(aws_conn_id="aws_s3_conn")
    files = s3_hook.list_keys(bucket_name=bucket_name, prefix=prefix)

    if not files:
        raise ValueError("No matching files found in S3 bucket")

    latest_file = sorted(files)[-1]  # Get the latest file based on name order
    return latest_file  # This will be stored in XCom


default_args = {
    'owner': 'varun',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 1),
    'email': ['varunmj978@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=15)
}

### Define DAG
with DAG('zillow_analytics_dag',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    ### Extract Zillow Data
    extract_zillow_data_var = PythonOperator(
        task_id='tsk_extract_zillow_data_var',
        python_callable=extract_zillow_data,
        op_kwargs={
            'url': 'https://zillow56.p.rapidapi.com/search',
            'querystring': {"location": "columbus, ch"},
            'headers': api_host_key,
            'date_string': dt_now_string
        }
    )

    ### Move extracted data to S3
    load_to_s3 = BashOperator(
        task_id='tsk_load_to_s3',
        bash_command='aws s3 mv {{ti.xcom_pull("tsk_extract_zillow_data_var")[0]}} s3://zillow-analytics-etl-project-bucket/',
    )

    ### Check if the file is available in S3
    is_file_in_s3_available = S3KeySensor(
        task_id='tsk_is_file_in_s3_available',
        bucket_key='{{ti.xcom_pull("tsk_extract_zillow_data_var")[1]}}',
        bucket_name=s3_bucket,
        aws_conn_id='aws_s3_conn',
        wildcard_match=False,
        timeout=60,
        poke_interval=5,
    )

    ###Fetch the latest file dynamically
    fetch_latest_s3_file = get_latest_s3_file(s3_bucket)

    ### Transfer the latest S3 file to Redshift
    transfer_s3_to_redshift = S3ToRedshiftOperator(
        task_id='tsk_transfer_s3_to_redshift',
        aws_conn_id='aws_s3_conn',
        redshift_conn_id='conn_id_redshift',
        s3_bucket=s3_bucket,
        s3_key="{{ ti.xcom_pull(task_ids='fetch_latest_s3_file') }}",  # Dynamically fetch latest file
        schema="PUBLIC",
        table="zillowdata",
        copy_options=["CSV", "IGNOREHEADER 1", "DELIMITER ','"]  
    )

    ###DAG Dependencies
    extract_zillow_data_var >> load_to_s3 >> is_file_in_s3_available >> fetch_latest_s3_file >> transfer_s3_to_redshift
