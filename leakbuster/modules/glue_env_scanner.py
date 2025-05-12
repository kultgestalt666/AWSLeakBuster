import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def scan_glue_jobs(profile):
    print(f"[Glue] Scanning Glue job configurations using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    glue = session.client("glue")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    try:
        jobs = glue.get_jobs()["Jobs"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to list Glue jobs: {e}")
        return

    for job in jobs:
        name = job["Name"]
        role = job.get("Role", "N/A")
        script_location = job.get("Command", {}).get("ScriptLocation", "N/A")
        language = job.get("Command", {}).get("Language", "python")
        default_args = job.get("DefaultArguments", {})
        arn = f"arn:aws:glue:{region}:{account_id}:job/{name}"

        print(f"\n{Fore.YELLOW}{'=' * 60}")
        print(f"{Fore.YELLOW}Job:            {name}")
        print(f"{Fore.CYAN}ARN:            {arn}")
        print(f"{Fore.CYAN}Language:       {language}")
        print(f"{Fore.CYAN}IAM Role:       {role}")
        print(f"{Fore.CYAN}ScriptLocation: {script_location}")

        if default_args:
            print(f"{Fore.WHITE}Default Arguments:")
            for key, val in default_args.items():
                print(f"  {key} = {val}")
        else:
            print(f"{Fore.GREEN}No default arguments found.")

        print(f"{Fore.YELLOW}{'=' * 60}")

