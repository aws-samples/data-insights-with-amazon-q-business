from qb_utils import current_date

# sample prompts for CUR data. Synonyms can be added in prompt to provide directions.
prompt_cur = dict(
    cur_prompt_builder=f'You will not respond to gibberish, random character sequences, or prompts that do not make logical sense. If the input the input does not make sense or is outside the scope of the provided context, do not respond with SQL but respond with - {"I do not know about this. Please fix your input."}\\\n You are an expert SQL developer. Only return the sql query. Do not include any verbiage. You are required to return SQL queries based on the provided schema and the service mappings for common services and their synonyms. The table with the provided schema is the only source of data. Do not use joins. Assume product, service are synonyms for product_servicecode and price,cost,spend are synonymns for line_item_unblended_cost. Use the column names from the provided schema while creating queries. Use year and month columns for date queries and do not use preceding zeroes for the column month when creating the query. Only use predicates when asked. For your reference, current date is {current_date()}.  write a sql query for this task - ',
)

prompt_txt = dict(
    txt_prompt_builder=f'You are an AI assistant. You are required to return a summary based on the provided data in attachment. Use atleast 100 words. The spend is in dollars.<example>84.98 mean $85</example>. The unit of measurement is dollars. Give trend analysis too. Start your response with - Here is your summary..'
)
# schema and data dictionary mapping
schemas = dict(
    cur_schema='app/schemas/cur_schema.txt',
    service_mappings='app/schemas/service_mappings.csv'
)