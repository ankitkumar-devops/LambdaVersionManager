# LambdaVersionManager (Lambda Janitor)

Lambda Janitor is a tool designed to manage AWS Lambda function versions by cleaning up old versions based on configurable criteria. This script helps in keeping your AWS environment tidy by removing old function versions while retaining a specified number of recent versions.

## Features
- **Automated Cleanup**: Lambda Janitor automates the process of cleaning up old Lambda function versions, reducing manual effort and ensuring a cleaner AWS environment.
- **Customizable Retention Policy**: You can configure Lambda Janitor to retain a specific number of recent versions while deleting older ones, providing flexibility based on your project requirements.
- **Detailed Logging**: The script provides detailed logging to track which versions are being deleted and why, ensuring transparency and accountability in the cleanup process.
- **Error Handling**: Lambda Janitor includes error handling mechanisms to gracefully handle exceptions, ensuring the cleanup process continues smoothly even in the event of unexpected errors.

## How It Works
Lambda Janitor utilizes the AWS Boto3 library to interact with the AWS Lambda service. It retrieves a list of all Lambda functions in the specified AWS region, then iterates through each function to identify and delete old versions based on the configured retention policy.

The cleanup criteria are as follows:
- Retain the latest N versions (default: 5).
- Delete versions older than 90 days, excluding those retained as per the first criterion.
- Versions associated with aliases are not deleted, ensuring that only unreferenced versions are removed.

## Getting Started
To get started with Lambda Janitor, follow these steps:

1. **Installation**: Clone the repository to your local environment or download the script directly.
2. **Configuration**: Update the AWS credentials in the script or ensure that the environment variables are correctly set up to allow access to the AWS Lambda service.

Feel free to customize this content further to suit your project's specific needs!
