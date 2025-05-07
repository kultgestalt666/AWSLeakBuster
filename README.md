# AWSLeakBuster

**AWSLeakBuster** is a command-line tool for scanning AWS accounts for potentially sensitive data that is often overlooked or unintentionally exposed.  
It focuses on identifying risks in services like:

- AWS Systems Manager Parameter Store (SSM)
- AWS Secrets Manager
- Lambda environment variables and function code
- EC2 User Data
- (and more to come)

## ⚙️ Features

- Uses AWS CLI profiles (`~/.aws/credentials`)
- Modular structure: easy to extend with new scanners
- CLI interface with optional scan filters
- Clear, human-readable output (and machine-friendly exports coming soon)

## 🚀 Usage

```bash
python cli.py --profile <aws-profile> --scan ssm

You can scan multiple modules at once:
python cli.py --profile <aws-profile> --scan ssm secrets lambda

## 🔍 Purpose

AWSLeakBuster helps penetration testers, auditors, and cloud engineers spot misconfigurations and secrets left in AWS services that may expose sensitive data.  
It uses the AWS CLI configuration (`~/.aws/credentials`) to connect via named profiles.

---
## 📁 Example Output

/my-app/config/password: <secure string – access denied>
/prod/lambda/API_KEY=abcd1234

## 📦 Installation

1. Clone this repository:

git clone https://github.com/<your-username>/AWSLeakBuster.git
cd AWSLeakBuster

2. Install dependencies:

pip install -r requirements.txt

## 🧪 Status

This project is still in early development. Basic functionality works, and new modules are being added step-by-step.

🙋‍♂️ Disclaimer

I'm not a professional software engineer – just someone with a strong interest in AWS security and automation.
This tool is developed and maintained as a learning project, and while I'm doing my best to keep it clean and useful, I may not be able to provide in-depth support for all edge cases or environments.
Use at your own discretion. Contributions welcome! 😊

## 📄 License

MIT License – free to use, modify, and share.
