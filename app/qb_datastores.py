import time
import boto3
import qb_config
from botocore.exceptions import ClientError
# create athena client
athena = boto3.client('athena', 'us-east-1')


def query_execution_details(query_execution_id):
    response = athena.get_query_execution(QueryExecutionId=query_execution_id)
    return response


# function to send query to athena
def send_query(athena_query,db_name,s3_loc):
    try:
        response_start_exec = athena.start_query_execution(
            QueryString=athena_query,
            QueryExecutionContext={
                'Database': db_name
            },
            ResultConfiguration={
                'OutputLocation': s3_loc
            },
        )
        return response_start_exec
    except ClientError as e:
        print(f"An error occurred while getting query results: {e.response['Error']['Message']}")
        return None

def wait_for_query_to_complete(query_execution_id):
    while True:
        response = athena.get_query_execution(QueryExecutionId=query_execution_id)
        print("Query state is: " + response['QueryExecution']['Status']['State'])
        state = response['QueryExecution']['Status']['State']
        if state == 'SUCCEEDED':
            return
        elif state == 'FAILED':
            raise Exception('Query failed')
        else:
            time.sleep(5)


# get athena query results
def get_query_results(query_execution_id):
    try:
        athena_results = athena.get_query_results(QueryExecutionId=query_execution_id)
        return athena_results
    except ClientError as e:
        print(f"An error occurred while getting query results: {e.response['Error']['Message']}")
        return None
