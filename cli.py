import argparse

def main():
    parser = argparse.ArgumentParser(
        prog="AWSLeakBuster",
        description="Scan AWS environments for potentially sensitive or exposed resources.",
        epilog="Example usage:\n"
               "  python3 cli.py --profile my-profile --scan ssm-parameters secrets\n\n"
               "Available scan modules:\n"
               "  ssm-parameters   Scan SSM Parameters for sensitive values\n"
               "  ssm-documents    Scan SSM Documents for insecure scripts\n"
               "  secrets          Scan Secrets Manager for readable secrets\n"
               "  ec2              Extract EC2 UserData for secrets\n"
               "  lambda-env       Dump Lambda environment variables\n"
               "  lambda-code      Download Lambda code archives\n"
               "  s3               Analyze S3 bucket permissions and exposure\n"
               "  ecs              Inspect ECS tasks, secrets, and exec settings\n"
               "  beanstalk        Dump Beanstalk environment variables\n"
               "  snapshots        Check EBS/RDS snapshots for public exposure\n"
               "  cloudformation   Identify roles passed to CloudFormation\n"
               "  glue-env         Dump Glue job configurations and secrets\n"
               "  glue-code        Download Glue job script files\n"
               "  codebuild        Review CodeBuild env + privilege settings\n"
               "  cognito          Dump Cognito Identity Pool configuration\n"
               "  sqs              Inspect SQS queue access and read messages\n"
               "  sns              Inspect SNS topic policies and subscriptions\n"
               "  apigateway       List API Gateway stages and exposure\n"
               "  eventbridge      Check EventBridge targets for leak paths\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--profile", required=True, help="AWS CLI profile name to use (from ~/.aws/credentials)")

    parser.add_argument(
        "--scan",
        nargs="+",
        choices=[
            "ssm-parameters", "ssm-documents", "ec2", "secrets", "lambda-env", "lambda-code",
            "s3", "ecs", "beanstalk", "snapshots", "cloudformation", "glue-env", "glue-code",
            "codebuild", "cognito", "sqs", "sns", "apigateway", "eventbridge"
        ],
        help="One or more scanner modules to run (space-separated)"
    )

    parser.add_argument("--output-dir", help="Optional output directory for downloaded data (code, messages, etc.)")

    args = parser.parse_args()

    from leakbuster import core
    lb = core.LeakbusterCore(profile=args.profile, output_dir=args.output_dir)

    if args.scan:
        for scan_type in args.scan:
            lb.run_scan(scan_type)
    else:
        print("No scan type specified. Use --scan to select modules.")

if __name__ == "__main__":
    main()

