import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

init(autoreset=True)

def scan_lambda_env(profile):
    print(f"[Lambda] Scanning environment variables using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    client = session.client("lambda")

    try:
        paginator = client.get_paginator("list_functions")
        for page in paginator.paginate():
            for fn in page["Functions"]:
                name = fn["FunctionName"]
                arn = fn["FunctionArn"]
                try:
                    config = client.get_function_configuration(FunctionName=name)
                    env = config.get("Environment", {}).get("Variables", {})

                    # Section header
                    print(f"\n{Fore.YELLOW}{'=' * 60}")
                    print(f"{Fore.YELLOW}Function: {name}")
                    print(f"{Fore.CYAN}ARN:      {arn}\n")

                    # Environment variables
                    if env:
                        for key, value in env.items():
                            print(f"  {Fore.WHITE}{key}={value}")
                    else:
                        print(f"  {Fore.LIGHTBLACK_EX}<no environment variables>")

                    print(f"{Fore.YELLOW}{'=' * 60}")

                except ClientError as e:
                    code = e.response["Error"]["Code"]
                    print(f"{Fore.RED}{name}: <error: {code}>")
                except Exception as e:
                    print(f"{Fore.RED}{name}: <unexpected error: {str(e)}>")
    except ClientError as e:
        print(f"Error while listing functions: {e}")

