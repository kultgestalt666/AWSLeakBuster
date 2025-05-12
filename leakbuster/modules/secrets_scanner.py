import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

init(autoreset=True)

def scan_secrets(profile):
    print(f"[Secrets] Scanning AWS Secrets Manager using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    client = session.client("secretsmanager")

    paginator = client.get_paginator("list_secrets")
    for page in paginator.paginate():
        for secret in page["SecretList"]:
            name = secret["Name"]
            try:
                response = client.get_secret_value(SecretId=name)
                if "SecretString" in response:
                    value = response["SecretString"]
                elif "SecretBinary" in response:
                    value = f"{Fore.LIGHTBLACK_EX}<binary secret>"
                else:
                    value = f"{Fore.RED}<unknown format>"
            except ClientError as e:
                code = e.response["Error"]["Code"]
                if code == "AccessDeniedException":
                    value = f"{Fore.RED}<access denied>"
                elif code == "ResourceNotFoundException":
                    value = f"{Fore.RED}<not found>"
                else:
                    value = f"{Fore.RED}<error: {code}>"
            except Exception as e:
                value = f"{Fore.RED}<unexpected error: {str(e)}>"

            print(f"{Fore.YELLOW}{name}: {Fore.WHITE}{value}\n")

