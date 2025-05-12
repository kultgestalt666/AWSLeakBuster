import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init
import os
import json

init(autoreset=True)

def scan_sqs(profile, output_dir=None):
    print(f"[SQS] Scanning SQS queues for public access and read permissions using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    sqs = session.client("sqs")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    try:
        response = sqs.list_queues()
        queue_urls = response.get("QueueUrls", [])
    except ClientError as e:
        print(f"{Fore.RED}Failed to list SQS queues: {e}")
        return

    if not queue_urls:
        print(f"{Fore.GREEN}No SQS queues found.")
        return

    download = input("Download messages to files? (y/N): ").strip().lower() == "y"
    if download and output_dir:
        os.makedirs(output_dir, exist_ok=True)

    for url in queue_urls:
        try:
            attrs = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["All"])["Attributes"]
            arn = attrs.get("QueueArn", "N/A")
            name = url.split("/")[-1]
            policy = attrs.get("Policy", "{}")
            is_public = '"Principal":"*"' in policy.replace(" ", "").replace("\n", "")
        except ClientError as e:
            print(f"{Fore.RED}Failed to get attributes for {url}: {e}")
            continue

        can_receive = False
        messages = []

        try:
            while True:
                response = sqs.receive_message(
                    QueueUrl=url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=0,
                    AttributeNames=["All"],
                    MessageAttributeNames=["All"]
                )
                msgs = response.get("Messages", [])
                if not msgs:
                    break
                messages.extend(msgs)
        except ClientError:
            pass

        can_receive = len(messages) > 0

        print(f"\n{Fore.YELLOW}{'=' * 60}")
        print(f"{Fore.YELLOW}Queue:           {name}")
        print(f"{Fore.CYAN}ARN:             {arn}")
        print(f"{Fore.CYAN}URL:             {url}")
        print(f"{Fore.RED if is_public else Fore.GREEN}Public Access:   {'[YES]' if is_public else '[NO]'}")
        print(f"{Fore.RED if can_receive else Fore.GREEN}Receivable:      {'[YES]' if can_receive else '[NO]'}")

        if download and can_receive:
            file_path = os.path.join(output_dir, f"{name}.txt")
            with open(file_path, "w") as f:
                for i, msg in enumerate(messages, 1):
                    f.write(f"--- Message {i} ---\n")
                    f.write(f"MessageId: {msg.get('MessageId', '')}\n")
                    f.write("Body:\n")
                    f.write(msg.get("Body", "") + "\n")
                    f.write("Attributes:\n")
                    for k, v in msg.get("Attributes", {}).items():
                        f.write(f"  {k}: {v}\n")
                    f.write("\n")
            print(f"{Fore.YELLOW}Messages saved to: {file_path}")

        print(f"{Fore.YELLOW}{'=' * 60}")

