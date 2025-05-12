import boto3
import base64
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

init(autoreset=True)

def scan_ec2_userdata(profile):
    print(f"[EC2] Scanning UserData for EC2 instances using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    ec2 = session.client("ec2")
    sts = session.client("sts")

    try:
        account_id = sts.get_caller_identity()["Account"]
        reservations = ec2.describe_instances()["Reservations"]
    except ClientError as e:
        print(f"Failed to describe instances: {e}")
        return

    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            region = ec2.meta.region_name
            arn = f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}"

            try:
                response = ec2.describe_instance_attribute(
                    InstanceId=instance_id,
                    Attribute="userData"
                )
                raw = response.get("UserData", {}).get("Value", "")
                if raw:
                    decoded = base64.b64decode(raw).decode("utf-8", errors="replace")
                    lines = decoded.strip().splitlines()
                else:
                    lines = []

                # Output formatting
                print(f"\n{Fore.YELLOW}{'=' * 60}")
                print(f"{Fore.YELLOW}Instance: {instance_id}")
                print(f"{Fore.CYAN}ARN:      {arn}\n")

                if lines:
                    for line in lines:
                        print(f"  {Fore.WHITE}{line}")
                else:
                    print(f"  {Fore.LIGHTBLACK_EX}<no user-data>")

                print(f"{Fore.YELLOW}{'=' * 60}")

            except ClientError as e:
                code = e.response['Error']['Code']
                print(f"{Fore.RED}{instance_id}: <error: {code}>")
            except Exception as e:
                print(f"{Fore.RED}{instance_id}: <unexpected error: {str(e)}>")

