import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init
import json

init(autoreset=True)

def scan_sns(profile):
    print(f"[SNS] Scanning topics for public subscription policies and exposed endpoints using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    sns = session.client("sns")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    try:
        topics = sns.list_topics()["Topics"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to list SNS topics: {e}")
        return

    if not topics:
        print(f"{Fore.GREEN}No SNS topics found.")
        return

    for topic in topics:
        arn = topic["TopicArn"]
        name = arn.split(":")[-1]

        try:
            attrs = sns.get_topic_attributes(TopicArn=arn)["Attributes"]
            policy_str = attrs.get("Policy", "{}")
            policy = json.loads(policy_str)
            statements = policy.get("Statement", [])
            is_public = any(s.get("Principal") == "*" for s in statements)
        except (ClientError, json.JSONDecodeError):
            is_public = False

        try:
            subscriptions = sns.list_subscriptions_by_topic(TopicArn=arn)["Subscriptions"]
        except ClientError:
            subscriptions = []

        print(f"\n{Fore.YELLOW}{'=' * 60}")
        print(f"{Fore.YELLOW}Topic:             {name}")
        print(f"{Fore.CYAN}ARN:               {arn}")
        print(f"{Fore.RED if is_public else Fore.GREEN}Public Subscribe:   {'[YES]' if is_public else '[NO]'}")

        if subscriptions:
            print(f"{Fore.WHITE}Subscriptions:")
            for sub in subscriptions:
                protocol = sub.get("Protocol", "N/A")
                endpoint = sub.get("Endpoint", "N/A")
                print(f"  - {protocol:<10} → {endpoint}")
        else:
            print(f"{Fore.GREEN}No subscriptions found.")

        print(f"{Fore.YELLOW}{'=' * 60}")

