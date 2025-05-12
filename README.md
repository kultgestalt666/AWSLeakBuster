# AWSLeakBuster

**AWSLeakBuster** is a command-line tool for scanning AWS accounts for potentially sensitive data that is often overlooked or unintentionally exposed.

It focuses on identifying risky content in:

- AWS Systems Manager Parameter Store (SSM)
- AWS Secrets Manager
- Lambda environment variables and function code
- EC2 User Data
- (More coming soon...)

## 🔍 Purpose

AWSLeakBuster helps penetration testers, auditors, and cloud engineers spot misconfigurations and secrets left in AWS services that may expose sensitive data.  
It uses the AWS CLI configuration (`~/.aws/credentials`) to connect via named profiles.

## ⚙️ Features

- Modular architecture (easy to extend)
- CLI with selective scan options
- Designed for offline/whitebox use
- Simple text output (machine-readable export planned)

## 🚀 Usage

```bash
python cli.py --profile <aws-profile> --scan ssm-parameters
```

Scan multiple sources at once:

```bash
python cli.py --profile <aws-profile> --scan ssm-parameters ec2
```

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kultgestalt666/AWSLeakBuster.git
   cd AWSLeakBuster
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📦 Supported Scan Modules

| Module           | Description                                                                |
|------------------|----------------------------------------------------------------------------|
| `ssm-parameters` | Scan SSM Parameters for sensitive or exposed values                        |
| `ssm-documents`  | Analyze SSM Documents for insecure automation or hardcoded credentials     |
| `secrets`        | Extract readable secrets from Secrets Manager                              |
| `ec2`            | Read EC2 UserData scripts for embedded secrets                             |
| `lambda-env`     | Dump Lambda environment variables                                          |
| `lambda-code`    | Download Lambda function code archives                                     |
| `s3`             | Check bucket public access, write access, and cleartext settings           |
| `ecs`            | Inspect ECS tasks for environment secrets, exec access, and logging        |
| `beanstalk`      | Read Elastic Beanstalk environment variables                               |
| `snapshots`      | Identify publicly exposed EBS and RDS snapshots                            |
| `cloudformation` | List IAM roles passed to CloudFormation stacks                             |
| `glue-env`       | Extract Glue job settings and linked secrets                               |
| `glue-code`      | Download Glue job scripts from S3                                          |
| `codebuild`      | Analyze CodeBuild projects for privilege escalation and secrets            |
| `cognito`        | List Cognito Identity Pools with unauthenticated access enabled            |
| `sqs`            | Analyze SQS queue policies and optionally dump readable messages           |
| `sns`            | Review SNS topic access and subscription exposure                          |
| `apigateway`     | Check API Gateway stages for public exposure                               |
| `eventbridge`    | List EventBridge rules and targets for leak potential                      |


## 🧪 Project Status

This is a **personal project in early development**.  
Basic modules work, more are in progress. Functionality and stability will improve over time.

## 🙋‍♂️ Disclaimer

I'm not a professional developer – just someone who enjoys breaking cloud things in a responsible way.

This tool is built for fun and learning. I can’t guarantee it works perfectly in all environments or provide deep support for special edge cases.  
**Use at your own risk. Pull requests and feedback are welcome.**

## 📄 License

MIT License – free to use, modify, and share.
