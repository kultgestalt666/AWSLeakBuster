import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def scan_eventbridge(profile):
    print(f"[EventBridge] Scanning rules and targets using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    events = session.client("events")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    try:
        rules = events.list_rules()["Rules"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to list EventBridge rules: {e}")
        return

    if not rules:
        print(f"{Fore.GREEN}No EventBridge rules found.")
        return

    for rule in rules:
        name = rule["Name"]
        arn = rule["Arn"]
        state = rule["State"]
        description = rule.get("Description", "N/A")
        event_pattern = rule.get("EventPattern", "N/A")
        schedule = rule.get("ScheduleExpression", "N/A")

        try:
            targets = events.list_targets_by_rule(Rule=name)["Targets"]
        except ClientError:
            targets = []

        print(f"\n{Fore.YELLOW}{'=' * 60}")
        print(f"{Fore.YELLOW}Rule:            {name}")
        print(f"{Fore.CYAN}ARN:             {arn}")
        print(f"{Fore.CYAN}State:           {state}")
        print(f"{Fore.CYAN}Description:     {description}")
        if schedule != "N/A":
            print(f"{Fore.CYAN}Schedule:        {schedule}")
        if event_pattern != "N/A":
            print(f"{Fore.CYAN}Event Pattern:   (defined)")

        if targets:
            print(f"{Fore.WHITE}Targets:")
            for tgt in targets:
                tgt_id = tgt.get("Id", "N/A")
                tgt_arn = tgt.get("Arn", "N/A")
                print(f"  - {tgt_id} → {tgt_arn}")
        else:
            print(f"{Fore.GREEN}No targets found.")

        print(f"{Fore.YELLOW}{'=' * 60}")

