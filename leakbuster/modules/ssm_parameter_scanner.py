import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

init(autoreset=True)

def scan_ssm(profile):
    print(f"[SSM] Scanning SSM Parameters using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    ssm = session.client("ssm")

    paginator = ssm.get_paginator("describe_parameters")
    for page in paginator.paginate():
        for param in page["Parameters"]:
            name = param["Name"]
            type_ = param["Type"]

            if type_ == "SecureString":
                type_str = f"{Fore.CYAN}(SecureString)"
            else:
                type_str = f"{Fore.GREEN}(String)"

            try:
                value = ssm.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]
            except ClientError as e:
                code = e.response['Error']['Code']
                if code == "AccessDeniedException":
                    value = f"{Fore.RED}<access denied>"
                elif code == "ParameterNotFound":
                    value = f"{Fore.RED}<not found>"
                else:
                    value = f"{Fore.RED}<error: {code}>"
            except Exception as e:
                value = f"{Fore.RED}<unexpected error: {str(e)}>"

            print(f"{type_str} {Fore.YELLOW}{name}: {Fore.WHITE}{value}\n")

