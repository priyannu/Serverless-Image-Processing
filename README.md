
# Local Serverless Image Processing Pipeline

### An AWS-compatible image processing pipeline built locally using Docker, LocalStack, AWS Lambda, Amazon S3, Amazon SNS and Python

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)

![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

![LocalStack](https://img.shields.io/badge/LocalStack-AWS%20Emulation-purple)

![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange?logo=awslambda)

![Amazon S3](https://img.shields.io/badge/Amazon-S3-green?logo=amazons3)

![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

The **Local Serverless Image Processing Pipeline** is an event-driven application that simulates an AWS serverless architecture entirely on a local machine.

It uses **Docker and LocalStack** to emulate AWS services, allowing developers to build and test a cloud-style image processing workflow without deploying infrastructure to a real AWS account.

When an image is uploaded to an input S3 bucket, an S3 event automatically invokes an AWS Lambda function. The function processes the image using Python and Pillow, generates three resized JPEG versions and a PDF, stores the results in an output S3 bucket, and publishes a processing notification to Amazon SNS.

> **Note:** This project runs locally using LocalStack. It demonstrates an AWS-compatible architecture but is not deployed to the actual AWS cloud.

---

## Architecture

![System Architecture](docs/architecture.png)

### Processing workflow

```text

                       LOCAL MACHINE

                             |

                             v

                      Docker Desktop

                             |

                             v

                        LocalStack

                             |

                 +-----------+-----------+

                 |                       |

                 v                       |

           Amazon S3                    |

           Input Bucket                 |

           image-input                  |

                 |                       |

                 | ObjectCreated Event   |

                 v                       |

            AWS Lambda                  |

          Image Processor               |

                 |                       |

        +--------+---------+             |

        |                  |             |

        v                  v             |

   Image Processing    PDF Generation    |

        |                  |             |

        +--------+---------+             |

                 |                       |

        +--------+---------+             |

        |                  |             |

        v                  v             |

   Amazon S3          Amazon SNS         |

  Output Bucket       Notifications      |

   image-output       Success/Failure    |

        |

        +-- image_small.jpg

        |

        +-- image_medium.jpg

        |

        +-- image_large.jpg

        |

        +-- image.pdf

```

### How it works

1. An image is uploaded to the `image-input` S3 bucket.

2. An `s3:ObjectCreated:*` event triggers the `image-processor` Lambda function.

3. Lambda downloads the uploaded image and validates its format.

4. Pillow generates small, medium and large JPEG versions.

5. Configured watermarks are applied to the selected JPEG outputs.

6. A PDF is generated, with an optional independent watermark.

7. All generated files are uploaded to the `image-output` bucket.

8. Lambda publishes a success or failure message to an SNS topic.

The S3 event automatically invokes Lambda. No continuously running Python file watcher is required.

---

## Features

- **Event-driven processing:** Automatically invokes Lambda when a new image is uploaded to S3.

- **Local AWS emulation:** Uses LocalStack to run AWS-compatible services on a local machine.

- **Automatic resizing:** Generates three JPEG variants with maximum dimensions of 300 × 300, 600 × 600 and 1200 × 1200 pixels.

- **Aspect ratio preservation:** Resizes images without stretching or distortion.

- **JPEG compression:** Uses Pillow to reduce JPEG output size.

- **PDF generation:** Creates a PDF from the uploaded image.

- **Selective JPEG watermarking:** Supports watermarking any combination of small, medium and large images.

- **Independent PDF watermark:** Supports a separate watermark and text for the generated PDF.

- **Image validation:** Rejects unsupported, empty or corrupted files.

- **SNS notifications:** Publishes processing success and failure events.

- **Docker-based deployment:** Provides a reproducible local development environment.

- **AWS CLI integration:** Uses standard AWS commands against LocalStack.

---

## Technology Stack

| Technology | Purpose |

|---|---|

| Python 3.12 | Application and Lambda development |

| Pillow | Image resizing, JPEG compression and PDF generation |

| Boto3 | AWS-compatible service integration |

| Docker Desktop | Container runtime |

| Docker Compose | LocalStack container configuration |

| LocalStack | Local AWS service emulation |

| Amazon S3 | Input and output object storage |

| AWS Lambda | Event-driven image processing |

| Amazon SNS | Processing notifications |

| AWS IAM | Lambda execution role configuration |

| AWS CLI | Local infrastructure management |

| PowerShell | Lambda packaging and deployment |

| Git and GitHub | Version control and project documentation |

---

## Project Structure

```text

local-serverless-image-pipeline/

|

|-- lambda/

|   |-- lambda_function.py

|   |-- requirements.txt

|

|-- scripts/

|   |-- deploy.ps1

|

|-- test_images/

|   |-- sample.jpg

|

|-- build/

|   |-- lambda/

|   |-- lambda.zip

|

|-- docs/

|   |-- architecture.png

|   |-- input-image.png

|   |-- output-small.png

|   |-- output-medium.png

|   |-- output-large.png

|   |-- terminal-output.png

|

|-- .env

|-- .gitignore

|-- docker-compose.yml

|-- trust-policy.json

|-- notification.json

|-- README.md

|-- LICENSE

```

### Directory descriptions

| Directory / File | Description |

|---|---|

| `lambda/lambda_function.py` | Main image processing Lambda handler |

| `lambda/requirements.txt` | Lambda Python dependencies |

| `scripts/deploy.ps1` | Builds a Linux-compatible Lambda deployment package and deploys to LocalStack |

| `test_images/` | Sample images for pipeline testing |

| `build/` | Generated Lambda dependencies and deployment ZIP |

| `docs/` | Architecture diagram and demonstration screenshots |

| `.env` | Local environment variables and LocalStack authentication token |

| `.gitignore` | Prevents secrets and generated files from being committed |

| `docker-compose.yml` | LocalStack container configuration |

| `trust-policy.json` | IAM role trust policy |

| `notification.json` | S3-to-Lambda event notification configuration |

| `README.md` | Project documentation |

The `build/`, `output/` and `.localstack/` directories and the `.env` file should not be committed to GitHub.

---

## Prerequisites

Install the following software before starting.

| Software | Download |

|---|---|

| Docker Desktop | https://www.docker.com/products/docker-desktop/ |

| Python | https://www.python.org/downloads/ |

| Visual Studio Code | https://code.visualstudio.com/ |

| Git | https://git-scm.com/downloads |

| AWS CLI | https://aws.amazon.com/cli/ |

| LocalStack | https://www.localstack.cloud/ |

This guide uses Windows PowerShell. Docker Desktop should be running before starting LocalStack.

A LocalStack authentication token may be required, depending on the installed LocalStack version and distribution. Refer to the official LocalStack installation instructions.

---

## Installation and Setup

### 1. Clone the repository

```bash

git clone https://github.com/YOUR_USERNAME/local-serverless-image-pipeline.git

cd local-serverless-image-pipeline

```

Replace `YOUR_USERNAME` with your GitHub username after creating the repository.

### 2. Verify the required tools

Open PowerShell and run:

```powershell

docker --version

docker compose version

python --version

aws --version

```

All four commands should display version information.

### 3. Configure LocalStack

Create a `.env` file in the project root:

```env

LOCALSTACK_AUTH_TOKEN=YOUR_LOCALSTACK_AUTH_TOKEN

```

Replace the placeholder with your token if required by your LocalStack installation.

**Never commit your `.env` file or authentication token to GitHub.**

### 4. Start Docker and LocalStack

Open Docker Desktop, then run:

```powershell

docker compose up -d

```

Check the container:

```powershell

docker ps

```

Inspect the logs:

```powershell

docker logs localstack-image-pipeline

```

Check LocalStack's health endpoint:

```powershell

Invoke-RestMethod http://localhost:4566/_localstack/health

```

LocalStack's main gateway is available at:

```text

http://localhost:4566

```

### 5. Configure local AWS CLI credentials

LocalStack accepts dummy AWS credentials for local development.

In the current PowerShell session, run:

```powershell

$env:AWS_ACCESS_KEY_ID = "test"

$env:AWS_SECRET_ACCESS_KEY = "test"

$env:AWS_DEFAULT_REGION = "us-east-1"

```

These values are for LocalStack only. They are not real AWS credentials.

Always use the LocalStack endpoint with AWS CLI commands:

```powershell

aws --endpoint-url=http://localhost:4566 s3 ls

```

This prevents the commands in this guide from targeting the actual AWS cloud.

---

## Infrastructure Setup

### Step 1: Create S3 buckets

Create the input bucket:

```powershell

aws --endpoint-url=http://localhost:4566 s3 mb s3://image-input

```

Create the output bucket:

```powershell

aws --endpoint-url=http://localhost:4566 s3 mb s3://image-output

```

Verify:

```powershell

aws --endpoint-url=http://localhost:4566 s3 ls

```

Expected bucket names:

```text

image-input

image-output

```

### Step 2: Create the SNS topic

```powershell

aws --endpoint-url=http://localhost:4566 sns create-topic `

    --name image-processing-notifications

```

Verify:

```powershell

aws --endpoint-url=http://localhost:4566 sns list-topics

```

The topic ARN for the default LocalStack account and region is:

```text

arn:aws:sns:us-east-1:000000000000:image-processing-notifications

```

The Lambda function publishes processing results to this topic.

**Important:** Creating an SNS topic and publishing messages does not automatically deliver emails or SMS messages. A supported subscription and delivery configuration are required.

### Step 3: Create the Lambda execution role

The `trust-policy.json` file contains the Lambda service trust policy.

```json

{

  "Version": "2012-10-17",

  "Statement": [

    {

      "Effect": "Allow",

      "Principal": {

        "Service": "lambda.amazonaws.com"

      },

      "Action": "sts:AssumeRole"

    }

  ]

}

```

Create the role:

```powershell

aws --endpoint-url=http://localhost:4566 iam create-role `

    --role-name image-processing-role `

    --assume-role-policy-document file://trust-policy.json

```

For deployment to real AWS, the role would also require appropriately scoped S3, SNS and CloudWatch Logs permissions.

---

## Lambda Packaging

The Lambda function uses Pillow, which includes native dependencies.

To avoid Windows/Linux compatibility problems, the deployment package is built inside a Linux Docker container.

Run:

```powershell

powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1

```

The build script:

1. Creates a clean build directory.

2. Copies `lambda_function.py`.

3. Installs Linux-compatible Python dependencies.

4. Creates the Lambda deployment ZIP.

Expected output:

```text

build/

|-- lambda/

|   |-- lambda_function.py

|   |-- PIL/

|   |-- ...

|

|-- lambda.zip

```

The resulting ZIP is used to deploy the Lambda function to LocalStack.

---

## Deploy the Lambda Function

Create the Lambda function:

```powershell

aws --endpoint-url=http://localhost:4566 lambda create-function `

    --function-name image-processor `

    --runtime python3.12 `

    --handler lambda_function.lambda_handler `

    --role arn:aws:iam::000000000000:role/image-processing-role `

    --zip-file fileb://build/lambda.zip `

    --timeout 120 `

    --memory-size 1024 `

    --environment "Variables={OUTPUT_BUCKET=image-output,AWS_ENDPOINT_URL=http://host.docker.internal:4566,SNS_TOPIC_ARN=arn:aws:sns:us-east-1:000000000000:image-processing-notifications}"

```

Verify deployment:

```powershell

aws --endpoint-url=http://localhost:4566 lambda get-function `

    --function-name image-processor

```

Wait until the function is active:

```powershell

aws --endpoint-url=http://localhost:4566 lambda wait function-active-v2 `

    --function-name image-processor

```

The function is now available inside the local AWS environment.

---

## Configure the S3 Event Trigger

The input S3 bucket must be configured to invoke Lambda whenever a new object is created.

### 1. Grant S3 permission to invoke Lambda

```powershell

aws --endpoint-url=http://localhost:4566 lambda add-permission `

    --function-name image-processor `

    --statement-id s3-invoke `

    --action lambda:InvokeFunction `

    --principal s3.amazonaws.com `

    --source-arn arn:aws:s3:::image-input `

    --source-account 000000000000

```

### 2. Configure the bucket notification

The `notification.json` file contains:

```json

{

  "LambdaFunctionConfigurations": [

    {

      "Id": "image-processor-trigger",

      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:000000000000:function:image-processor",

      "Events": [

        "s3:ObjectCreated:*"

      ]

    }

  ]

}

```

Apply the configuration:

```powershell

aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration `

    --bucket image-input `

    --notification-configuration file://notification.json

```

Verify:

```powershell

aws --endpoint-url=http://localhost:4566 s3api get-bucket-notification-configuration `

    --bucket image-input

```

The event-driven pipeline is now configured.

---

## Image Processing

The Lambda function generates three JPEG images and one PDF for every valid uploaded image.

### Resized JPEG outputs

| Variant | Maximum dimensions | Format | JPEG quality |

|---|---|---|---|

| Small | 300 × 300 px | JPG | 70 |

| Medium | 600 × 600 px | JPG | 70 |

| Large | 1200 × 1200 px | JPG | 70 |

The application uses Pillow's `thumbnail()` method with LANCZOS resampling.

This preserves the original aspect ratio, so an image may not have exact square dimensions.

For example, a landscape image might produce a 300 × 200 px small output rather than a 300 × 300 px output.

Images smaller than the target dimensions are not automatically enlarged.

### PDF generation

The original image is converted into a PDF using Pillow.

The PDF can have a watermark independently of the three resized JPEG images.

PDF file size depends on the original image dimensions, image content and encoding. A smaller PDF is not guaranteed.

---

## Supported File Formats

The application is designed to process the following image formats:

| Extension | Supported |

|---|---|

| `.jpg` | Yes |

| `.jpeg` | Yes |

| `.png` | Yes |

| `.webp` | Yes |

| `.bmp` | Yes |

| `.tiff` | Yes |

| `.pdf` | No |

| `.txt` | No |

| `.zip` | No |

All supported input images are converted into RGB before JPEG and PDF generation.

Unsupported, empty or corrupted files are rejected and reported as processing failures.

---

## Testing the Pipeline

### Step 1: Prepare a test image

Place an image in:

```text

test_images/sample.jpg

```

![Original Input Image](docs/input-image.png)

### Step 2: Upload it to S3

Run:

```powershell

aws --endpoint-url=http://localhost:4566 s3 cp `

    test_images/sample.jpg `

    s3://image-input/

```

The upload creates an S3 event, which invokes the Lambda function automatically.

### Step 3: Inspect processing logs

```powershell

docker logs localstack-image-pipeline --tail 100

```

Example processing output:

```text

======================================================================

              IMAGE PROCESSING LAMBDA

======================================================================

Input bucket: image-input

Input object: sample.jpg

Original dimensions: 1920 x 1080

Creating small image...

Created: sample_small.jpg

Creating medium image...

Created: sample_medium.jpg

Creating large image...

Created: sample_large.jpg

Creating PDF...

Created: sample.pdf

SNS notification sent.

======================================================================

STATUS: SUCCESS

======================================================================

```

This is an illustrative example. Actual dimensions and log output depend on the uploaded image.

![Terminal Output](docs/terminal-output.png)

### Step 4: Check the output bucket

```powershell

aws --endpoint-url=http://localhost:4566 s3 ls `

    s3://image-output/

```

Expected files:

```text

sample_small.jpg

sample_medium.jpg

sample_large.jpg

sample.pdf

```

### Step 5: Download the results

Create a local output directory:

```powershell

New-Item -ItemType Directory -Force -Path output

```

Download all generated files:

```powershell

aws --endpoint-url=http://localhost:4566 s3 cp `

    s3://image-output/ `

    output/ `

    --recursive

```

The generated files will be available in the `output/` directory.

---

## Sample Results

The following screenshots demonstrate the intended image-processing output.

Replace the placeholder images with screenshots from your own successful pipeline run.

### Original image

![Original Image](docs/input-image.png)

### Small — 300 px maximum

![Small Output](docs/output-small.png)

### Medium — 600 px maximum

![Medium Output](docs/output-medium.png)

### Large — 1200 px maximum

![Large Output](docs/output-large.png)

### Output comparison

| Output | Maximum size | Format | Watermark |

|---|---|---|---|

| Small | 300 × 300 px | JPG | Configurable |

| Medium | 600 × 600 px | JPG | Configurable |

| Large | 1200 × 1200 px | JPG | Configurable |

| PDF | Based on source image | PDF | Independently configurable |

Actual file sizes depend on the uploaded image.

---

## SNS Notifications

The Lambda function publishes a notification when processing succeeds or fails.

### Success message

```text

Subject: Image Processing Successful

Image processing completed successfully.

Input: sample.jpg

Output bucket: image-output

Generated files:

- sample_small.jpg

- sample_medium.jpg

- sample_large.jpg

- sample.pdf

```

### Failure message

```text

Subject: Image Processing Failed

Image processing failed.

Error: Uploaded file is not a valid image.

```

SNS publishing is separate from message delivery. Receiving actual email or SMS notifications requires an appropriate subscription and a delivery mechanism supported by the LocalStack environment.

---

## Error Handling

The application includes image validation and exception handling.

| Scenario | Expected behavior |

|---|---|

| Valid image | Generate JPEGs and PDF |

| Unsupported file | Reject and report failure |

| Empty file | Reject and report failure |

| Corrupted image | Reject and report failure |

| Image processing exception | Log the error and publish a failure notification |

| S3 upload error | Log the failure |

| SNS publish error | Log the notification error |

For production deployments, additional improvements would include retry policies, dead-letter queues, object-size limits, idempotency and structured monitoring.

---

## LocalStack vs AWS

| Component | Local development | AWS deployment |

|---|---|---|

| Object storage | LocalStack S3 | Amazon S3 |

| Event trigger | Emulated S3 notification | S3 event notification |

| Compute | LocalStack Lambda | AWS Lambda |

| Notifications | LocalStack SNS | Amazon SNS |

| Identity | LocalStack IAM | AWS IAM |

| Runtime | Docker Desktop | AWS-managed infrastructure |

| Infrastructure management | AWS CLI with local endpoint | AWS CLI with AWS endpoint |

LocalStack is useful for development and integration testing, but it is not a substitute for validating deployment-specific behavior in a real AWS environment.

---

## Troubleshooting

### Docker is not running

Start Docker Desktop and verify:

```powershell

docker info

```

### LocalStack is not responding

Check:

```powershell

docker compose ps

```

Inspect the logs:

```powershell

docker compose logs localstack

```

Restart if necessary:

```powershell

docker compose down

docker compose up -d

```

### AWS CLI reports missing credentials

Configure dummy credentials in PowerShell:

```powershell

$env:AWS_ACCESS_KEY_ID = "test"

$env:AWS_SECRET_ACCESS_KEY = "test"

$env:AWS_DEFAULT_REGION = "us-east-1"

```

### Lambda cannot import Pillow

Rebuild the deployment package using Docker:

```powershell

powershell -ExecutionPolicy Bypass -File .\scripts\deploy.ps1

```

Ensure the build container uses a Python version and CPU architecture compatible with the Lambda runtime.

### S3 upload does not invoke Lambda

Verify the bucket notification:

```powershell

aws --endpoint-url=http://localhost:4566 s3api get-bucket-notification-configuration `

    --bucket image-input

```

Check that the Lambda function exists:

```powershell

aws --endpoint-url=http://localhost:4566 lambda get-function `

    --function-name image-processor

```

Also verify that S3 has permission to invoke the function.

### Output bucket is empty

Inspect the Lambda execution logs and check whether the function successfully downloaded and processed the uploaded image.

Confirm that the output bucket exists and the Lambda environment variable points to the correct bucket.

---

## Security Considerations

This project is intended for local development and learning.

- Do not commit LocalStack authentication tokens.

- Do not commit real AWS access keys.

- Keep `.env` in `.gitignore`.

- Use dummy AWS credentials for local testing.

- Do not expose LocalStack's gateway publicly without appropriate security controls.

- Use least-privilege IAM policies when deploying to actual AWS.

- Validate uploaded file types and enforce appropriate file-size limits.

---

## Future Enhancements

- [ ] Build a Streamlit or React image-upload interface.

- [ ] Display original and processed images side by side.

- [ ] Display before-and-after file sizes and compression percentages.

- [ ] Add image-processing execution time metrics.

- [ ] Add automated integration tests.

- [ ] Add batch image processing.

- [ ] Add SNS email notification integration.

- [ ] Add CloudWatch-compatible monitoring.

- [ ] Add Terraform infrastructure provisioning.

- [ ] Add a CI/CD pipeline using GitHub Actions.

- [ ] Deploy and validate the pipeline on actual AWS.

---

## Learning Outcomes

This project demonstrates practical experience with:

1. Event-driven and serverless architecture.

2. AWS-compatible cloud service integration.

3. S3 event notifications and Lambda invocation.

4. Docker-based local development.

5. Python image processing using Pillow.

6. Object storage and automated file generation.

7. SNS-based event notifications.

8. Infrastructure configuration using AWS CLI.

9. Error handling and application logging.

10. Git and GitHub project documentation.

---

## References

- [LocalStack Documentation](https://docs.localstack.cloud/)

- [Docker Documentation](https://docs.docker.com/)

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)

- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)

- [Amazon SNS Documentation](https://docs.aws.amazon.com/sns/)

- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

- [Pillow Documentation](https://pillow.readthedocs.io/)

---


**Built with Python, Docker, LocalStack and AWS-compatible serverless services.**
