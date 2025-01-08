To run the script for fetching bucket sizes using GitHub Actions, you can create a workflow that installs the necessary dependencies, runs the Python script, and optionally sends the output to a logging or visualization platform.

GitHub Actions Workflow Configuration
	1.	Set Up the Workflow File
Create a workflow file in your repository under .github/workflows/bucket-size.yml.
	2.	Workflow Code

name: Get Bucket Sizes

on:
  workflow_dispatch:  # Allows manual triggering of the workflow

jobs:
  fetch-bucket-sizes:
    runs-on: ubuntu-latest

    steps:
      # Step 1: Checkout the repository
      - name: Checkout Code
        uses: actions/checkout@v3

      # Step 2: Set up Python
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.9

      # Step 3: Install dependencies
      - name: Install Dependencies
        run: pip install boto3

      # Step 4: Run the Python script
      - name: Fetch Bucket Sizes
        env:
          S3_ENDPOINT: ${{ secrets.S3_ENDPOINT }}  # S3-compatible endpoint
          ACCESS_KEY: ${{ secrets.S3_ACCESS_KEY }}  # Access key from secrets
          SECRET_KEY: ${{ secrets.S3_SECRET_KEY }}  # Secret key from secrets
        run: |
          python <<EOF
          import boto3
          from botocore.exceptions import NoCredentialsError, PartialCredentialsError

          # Get environment variables
          S3_ENDPOINT = "${{ secrets.S3_ENDPOINT }}"
          ACCESS_KEY = "${{ secrets.S3_ACCESS_KEY }}"
          SECRET_KEY = "${{ secrets.S3_SECRET_KEY }}"

          def get_bucket_sizes():
              try:
                  s3_client = boto3.client(
                      's3',
                      endpoint_url=S3_ENDPOINT,
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY
                  )

                  buckets = s3_client.list_buckets()['Buckets']
                  bucket_sizes = {}

                  for bucket in buckets:
                      bucket_name = bucket['Name']
                      total_size = 0
                      paginator = s3_client.get_paginator('list_objects_v2')
                      for page in paginator.paginate(Bucket=bucket_name):
                          if 'Contents' in page:
                              total_size += sum(obj['Size'] for obj in page['Contents'])

                      bucket_sizes[bucket_name] = total_size
                      print(f"Bucket: {bucket_name}, Size: {total_size / (1024**3):.2f} GB")

                  return bucket_sizes

              except (NoCredentialsError, PartialCredentialsError) as e:
                  print(f"Error with credentials: {e}")
              except Exception as e:
                  print(f"An error occurred: {e}")

          get_bucket_sizes()
          EOF

Secrets Configuration

Store sensitive information (S3 endpoint, access key, and secret key) as GitHub Secrets:
	1.	Go to your GitHub repository.
	2.	Navigate to Settings > Secrets and variables > Actions.
	3.	Add the following secrets:
	•	S3_ENDPOINT – Your S3-compatible endpoint.
	•	S3_ACCESS_KEY – The access key for your object storage.
	•	S3_SECRET_KEY – The secret key for your object storage.

Triggering the Workflow

You can trigger this workflow manually from the Actions tab in your GitHub repository.

Optional: Save Output to a File

If you want to save the bucket sizes to a file (e.g., bucket_sizes.json), modify the script to write the results:

import json
with open("bucket_sizes.json", "w") as f:
    json.dump(bucket_sizes, f)

Then, upload the file as an artifact:

      # Step 5: Upload Results as Artifact
      - name: Upload Artifact
        uses: actions/upload-artifact@v3
        with:
          name: bucket-sizes
          path: bucket_sizes.json

Optional: Send Data to Visualization Platforms

You can integrate this script with ElasticSearch, Splunk, or other platforms to visualize bucket sizes. Let me know if you’d like assistance with these integrations.