import json
import boto3

athena_client = boto3.client('athena')

def build_athena_reporting_monthly(year,month):
    print("Building Athena Reporting Layer Monthly")
    try:
        glue_database = 'hyn_stocks_db'
        processed_table = 'stocks_processed'
        OUTPUT_LOCATION = 's3://hyn-motor-stock-datalake/athena_outputs/'
        monthly_reporting_table = 'monthly_stock_reporting'
        query = f''' insert into { monthly_reporting_table } 
                        SELECT
                            year,
                            month,
                            COUNT(*)                     AS trading_days,
                            ROUND(AVG(close), 2)         AS avg_close_price,
                            MAX(high)                    AS highest_price,
                            MIN(low)                     AS lowest_price,
                            SUM(volume)                  AS total_volume,
                            ROUND(AVG(daily_range), 2)   AS avg_daily_range
                        FROM { processed_table } where year = {year} and month = {month}
                        GROUP BY year, month
                        ORDER BY year, month
                        '''
        print("Query to be processed" , query)
        response = athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': glue_database},
                ResultConfiguration={'OutputLocation': OUTPUT_LOCATION }
        )   
        print('print_response',response)        
        return response
    except Exception as e:
        print('Error in processing in Athena Monthly: ', str(e))

def build_athena_reporting_yearly(year):
    print("Building Athena Reporting Layer Yearly")
    try:
        glue_database = 'hyn_stocks_db'
        processed_table = 'stocks_processed'
        OUTPUT_LOCATION = 's3://hyn-motor-stock-datalake/athena_outputs/'
        yearly_reporting_table = 'yearly_stock_reporting'
        query = f''' insert into { yearly_reporting_table } 
                            SELECT
                            year,
                            COUNT(*)                     AS trading_days,
                            ROUND(AVG(close), 2)         AS avg_close_price,
                            MAX(high)                    AS yearly_high,
                            MIN(low)                     AS yearly_low,
                            SUM(volume)                  AS total_volume
                        FROM { processed_table } where year = {year} 
                        and year not in (select distinct year from {yearly_reporting_table})
                        GROUP BY year
                        ORDER BY year
                        '''
        print("Query to be processed" , query)
        response = athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': glue_database},
                ResultConfiguration={'OutputLocation': OUTPUT_LOCATION }
        )   
        print('print_response',response)        
        return response
    except Exception as e:
        print('Error in processing in Athena Yearly: ', str(e))        

def lambda_handler(event, context):
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    year = key.split('year%3D')[1].split('/')[0]
    month = key.split('month%3D')[1].split('/')[0]

    monthly_query_response = build_athena_reporting_monthly(year,month)
    yearly_query_response = build_athena_reporting_yearly(year)
    

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
