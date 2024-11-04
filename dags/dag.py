import logging

import pendulum
from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
import clickhouse_connect  # python integration pkg for clickhouse


# create table in clickhouse 
def create_table_ch():

    # connect to clickhouse
    client = clickhouse_connect.get_client(
        host=Variable.get('ch_host'), 
        username=Variable.get('ch_user'), 
        password=Variable.get('ch_password'),
    )
    logging.info('Connected to clickhouse')

    # create table
    client.command(
        "CREATE TABLE IF NOT EXISTS replenishments (email String, price Int32) \
         ENGINE MergeTree ORDER BY email"
    )
    logging.info('Created table')


# insert date in the table in clickhouse 
def transfer_data_to_ch():
    
    # connect to clickhouse
    client = clickhouse_connect.get_client(
        host=Variable.get('ch_host'), 
        username=Variable.get('ch_user'), 
        password=Variable.get('ch_password'),
    )
    logging.info('Connected to clickhouse')

    # insert data
    parameters = {
        'postgres_host' : Variable.get('pg_host'), 
        'db_name' : Variable.get('pgdb_name'), 
        'user' : Variable.get('pg_user'), 
        'password' : Variable.get('pg_password'), 
    }
    client.command(
        """INSERT INTO replenishments
            SELECT * FROM postgresql(
                %(postgres_host)s, 
                %(db_name)s, 
                'replenishments', 
                %(user)s,
                %(password)s
            )""",
        parameters=parameters,
    )
    logging.info('Data transfered')


with DAG(
    dag_id='yandex_test_dag',
    start_date=pendulum.today(),
    schedule=None,
    description='Load data into postgres, transform and place into clickhouse',
    catchup=False,
) as dag:
    
    start_op = EmptyOperator(task_id='start')

    # create tables in postgres
    create_pg_table_op = PostgresOperator(
        task_id='pg_table_creation',
        sql='sql_scripts/table_creation_postgres.sql',
        postgres_conn_id='postgres'
    )

    # load data into postgres
    load_data_op = PostgresOperator(
        task_id='data_loading',
        sql='sql_scripts/data_loading_postgres.sql',
        postgres_conn_id='postgres'
    )

    # create a materialized view in postgres 
    create_view_op = PostgresOperator(
        task_id='view_creation',
        sql='sql_scripts/view_creation_postgres.sql',
        postgres_conn_id='postgres'
    )

    # create table in clickhouse
    create_ch_table_op = PythonOperator(
        task_id='ch_table_creation',
        python_callable=create_table_ch,
    )

    # transfer the view to clickhouse 
    send_view_op = PythonOperator(
        task_id='data_transfering',
        python_callable=transfer_data_to_ch,
    )

    finish_op = EmptyOperator(task_id='finish')

    start_op >> create_pg_table_op >> load_data_op >> create_view_op \
        >> create_ch_table_op >> send_view_op >> finish_op
