# IAM Role Setup – Lambda Execution Role for Data Lake

## Role Name
`aws_datalake_lambda_role`

---

# 📌 Purpose

This IAM role is used by the AWS Lambda function responsible for:

- Triggering Athena queries
- Managing S3 objects (raw → processed → curated)
- Sending notifications (SNS)
- Accessing parameters (SSM)
- Interacting with Glue Data Catalog
- Writing logs to CloudWatch

---

# 🏗 Architecture Context

This role supports the following architecture:

S3 (Raw Layer)  
→ Lambda (Triggered by S3 Event)  
→ Athena Transformation  
→ Processed Layer (Parquet, Partitioned)  
→ Curated Layer  
→ Reporting  

---

# 🔐 Attached Policies

The following AWS Managed Policies are attached to this role:

| Policy Name | Type | Purpose |
|------------|------|----------|
| `AmazonAthenaFullAccess` | AWS Managed | Allows Lambda to execute and monitor Athena queries |
| `AmazonS3FullAccess` | AWS Managed | Allows read/write access to Data Lake buckets |
| `AmazonSNSFullAccess` | AWS Managed | Enables notification publishing (alerts, failures) |
| `AmazonSSMFullAccess` | AWS Managed | Access to Parameter Store for configuration values |
| `AWSGlueConsoleFullAccess` | AWS Managed | Access to Glue Data Catalog metadata |
| `AWSLambdaBasicExecutionRole` | AWS Managed | Allows writing logs to CloudWatch |

---
## Usage Scope

Environment: Development / Learning  
Execution Type: Event-Driven Lambda (Triggered by S3 Upload)