import argparse
from leakbuster.core import LeakbusterCore

def main():
    parser = argparse.ArgumentParser(
        description="AWSLeakBuster – Scan AWS for exposed secrets and sensitive data."
    )

    parser.add_argument(
        "--profile",
        required=True,
        help="Name of AWS CLI profile to use"
    )

    parser.add_argument(
        "--scan",
        choices=["ssm-parameters", "ssm-documents", "ec2", "secrets", "lambda-env", "lambda-code", "s3", "ecs", "beanstalk", "snapshots", "cloudformation", "glue-env", "glue-code", "codebuild", "cognito", "sqs", "sns", "apigateway", "eventbridge"],
        nargs="+",
        help="Modules to scan (can be used multiple times)"
    )

    parser.add_argument(
        "--output-dir",
        help="Output directory for lambda-code (default: ./lambda) and glue-code (default: ./glue)"
    )

    args = parser.parse_args()

    core = LeakbusterCore(profile=args.profile, output_dir=args.output_dir)

    if args.scan:
        for scan_type in args.scan:
            core.run_scan(scan_type)
    else:
        print("[!] No scan module selected. Use --scan with at least one module.")

if __name__ == "__main__":
    main()

