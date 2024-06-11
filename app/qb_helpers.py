# Helper functions

import pandas as pd
from tabulate import tabulate


# Print the query results as a table
def print_query_results(query_results):
    # Extract the headers and rows from the query results
    headers = [header['Name'] for header in query_results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = [row['Data'] for row in query_results['ResultSet']['Rows'][1:]]  # Skip the header row

    # remove VarCharValue in data
    for row in rows:
        for i, cell in enumerate(row):
            if 'VarCharValue' in cell:
                row[i] = cell['VarCharValue']

    # Print the query results as a table
    print(tabulate(rows, headers, tablefmt='grid'))


# Print the query results as a table using a Pandas Dataframe
def print_query_results_df(query_results):
    column_headers = [header['Name'] for header in query_results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = [row['Data'] for row in query_results['ResultSet']['Rows'][1:]]  # Skip the header row

    # remove VarCharValue in data
    for row in rows:
        for i, cell in enumerate(row):
            if 'VarCharValue' in cell:
                row[i] = cell['VarCharValue']
    df = pd.DataFrame(rows, columns=column_headers)
    return df
