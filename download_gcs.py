import os
from google.cloud import bigquery
import csv
import json

# Initialize BigQuery client
client = bigquery.Client(project="semantic-scholar")

# Define your fully-qualified table
dt = "sqa"
if dt == "os":
    output_file = os.path.join("data", "os_filtered_returning.jsonl")
    table_ref = "semantic-scholar.open_scholar_demo.os_traces"
    
else:
    output_file = os.path.join("data", "sqa_filtered_returning.jsonl")
    table_ref = "semantic-scholar.ai2_scholar_qa.scholar_qa_usage"

# SQL query: get queries + timestamps from users with ≥3 queries, limited to 100k rows
query = f"""
WITH queries AS (
  SELECT
    user_id,
    task_id,
    query,
    timestamp,
    DATETIME_TRUNC(timestamp, DAY) AS query_day
  FROM `semantic-scholar.ai2_scholar_qa.scholar_qa_usage`
),

-- Users with more than 3 queries
user_query_counts AS (
  SELECT
    user_id,
    COUNT(*) AS query_count
  FROM queries
  GROUP BY user_id
  HAVING COUNT(*) > 3
),

-- For each user/day, get the earliest query timestamp
user_day_first_query AS (
  SELECT
    user_id,
    query_day,
    MIN(timestamp) AS first_query_time
  FROM queries
  GROUP BY user_id, query_day
),

-- For each user, count how many of their query_days are separated from others by ≥ 3 hours
user_day_gaps AS (
  SELECT
    a.user_id,
    COUNT(*) AS valid_day_count
  FROM user_day_first_query a
  JOIN user_day_first_query b
    ON a.user_id = b.user_id
   AND b.query_day > a.query_day
   AND DATETIME_DIFF(b.first_query_time, a.first_query_time, HOUR) >= 3
  GROUP BY a.user_id
  HAVING COUNT(*) >= 1  -- At least one valid day-to-day gap
),

-- Final filtered queries
filtered_queries AS (
  SELECT q.*
  FROM queries q
  JOIN user_query_counts uqc ON q.user_id = uqc.user_id
  JOIN user_day_gaps udg ON q.user_id = udg.user_id
)

SELECT user_id, timestamp, task_id, query
FROM filtered_queries
ORDER BY user_id, timestamp

LIMIT 5000
"""

# Run the query
print("Running query...")
query_job = client.query(query)
results = query_job.result()
print("Query completed.")

# Save results to a local JSON file
print(f"Writing results to {output_file} ...")

with open(output_file, "w", encoding="utf-8") as f:
    for row in results:
        # Convert each row to a dict
        row_dict = {
            "user_id": row.user_id,
            "timestamp": row.timestamp.isoformat() if hasattr(row.timestamp, 'isoformat') else str(row.timestamp),
            "task_id": row.task_id,
            "query": row.query,
        }
        # Write JSON line
        f.write(json.dumps(row_dict) + "\n")

print(f"JSONL file saved to {output_file}")


