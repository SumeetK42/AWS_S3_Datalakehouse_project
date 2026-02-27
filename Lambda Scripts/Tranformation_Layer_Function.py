import json
import boto3

athena_client = boto3.client('athena')
glue_client = boto3.client('glue')

def get_crawler_name():
    crawler_name = 'csv-datalake-crawler'
    return crawler_name    

def get_sns_alerts(msg):
    sns = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-east-1:<account_id>:dl-alerts'
    sns.publish(
        TopicArn=topic_arn,
        Message=msg,
        Subject='DataLake Alert'
    )

def run_glue_crawler():
    try:
        crawler_name = get_crawler_name()
        response = glue_client.start_crawler(Name=crawler_name)
        print("Crawler started successfully" , response)
    except Exception as e:
        print('Error in running crawler : ', str(e))
    

def do_athena_partitioning_processed():
    try:
        glue_database = 'hyn_stocks_db'
        processed_table = 'stocks_processed'
        OUTPUT_LOCATION = 's3://hyn-motor-stock-datalake/athena_outputs/'
        raw_table = 'stocks_raw'
        #query = f'select * from {raw_table}'
        query = f''' insert into {processed_table} 
                    with parsed_date_data as ( 
                    SELECT * , cast(date_parse("date", '%d-%m-%Y') as date) as parsed_date FROM {raw_table} 
                    ) select 
                    "date",
                    "open",
                    "open" - (lag("open") OVER (ORDER BY parsed_date)) as current_open_vs_last_day_open,
                    "high",
                    "low",
                    "high" - "low" AS daily_range,
                    "close",
                    "close" - (lag("close") OVER (ORDER BY parsed_date)) as current_close_vs_last_day_close,
                    "adjclose",
                    "volume",
                    current_date as ingested_at,
                    year(parsed_date) as "year",
                    month(parsed_date) as "month"
                    from parsed_date_data
                    where "Date" not in (select "Date" from {processed_table}) '''
        print("Query to be processed" , query)
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': glue_database},
            ResultConfiguration={'OutputLocation': OUTPUT_LOCATION }
        )   
        print('print_response',response)        
        return response
    except Exception as e:
        print('Error in processing in Athena: ', str(e))

def lambda_handler(event, context):
    # TODO implement
    try: 
        rec = event['Records'][0]
        ## get the record details for S3 event
        bucket_name = rec['s3']['bucket']['name']
        key = rec['s3']['object']['key']

        print('bucket_name',bucket_name)
        print('key',key)

        ## Running Glue Crawler Trigger when file is added to raw folder
        if 'raw' in key:
            print('running crawler')
            run_glue_crawler()
            get_sns_alerts(f'Crawler triggered for {bucket_name} and key is {key}')    
    
        ## Athena partitioning for Data in RAW layer to Processed Layer
        response_query = do_athena_partitioning_processed()

        print(response_query)
        resqueryid = response_query['QueryExecutionId']
        
        ## get athena query status

        query_status = athena_client.get_query_execution(QueryExecutionId=resqueryid);
        print('Query STATUS ' , query_status)
        
     
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as e:
        print('Error in processing the request : ', str(e))
        get_sns_alerts(f'Error in processing the Lambda request : {str(e)}')
        raise e
    


