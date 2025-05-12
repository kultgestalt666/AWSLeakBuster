import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument(
        "--scan",
        nargs="+",
        choices=[
            "ssm-parameters", "ssm-documents", "ec2", "secrets", "lambda-env", "lambda-code",
            "s3", "ecs", "beanstalk", "snapshots", "cloudformation", "glue-env", "glue-code",
            "codebuild", "cognito", "sqs", "sns", "apigateway", "eventbridge"
        ],
        help="One or more scanners to run"
    )
    parser.add_argument("--output-dir", help="Optional output directory for file-based results")
    args = parser.parse_args()

    # 👉 Jetzt erst importieren!
    from leakbuster import core

    lb = core.LeakbusterCore(profile=args.profile, output_dir=args.output_dir)

    if args.scan:
        for scan_type in args.scan:
            lb.run_scan(scan_type)
    else:
        print("No scan type specified. Use --scan to select modules.")

if __name__ == "__main__":
    main()

