import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def scan_codebuild(profile):
    print(f"[CodeBuild] Scanning CodeBuild projects using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    codebuild = session.client("codebuild")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    try:
        projects = codebuild.list_projects()["projects"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to list CodeBuild projects: {e}")
        return

    if not projects:
        print(f"{Fore.GREEN}No CodeBuild projects found.")
        return

    try:
        details = codebuild.batch_get_projects(names=projects)["projects"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to fetch CodeBuild project details: {e}")
        return

    for project in details:
        name = project["name"]
        arn = project["arn"]
        role = project.get("serviceRole", "N/A")
        privileged = project.get("environment", {}).get("privilegedMode", False)
        source_type = project.get("source", {}).get("type", "N/A")
        source_location = project.get("source", {}).get("location", "N/A")
        env_vars = project.get("environment", {}).get("environmentVariables", [])

        print(f"\n{Fore.YELLOW}{'=' * 60}")
        print(f"{Fore.YELLOW}Project:        {name}")
        print(f"{Fore.CYAN}ARN:            {arn}")
        print(f"{Fore.CYAN}IAM Role:       {role}")
        print(f"{Fore.RED if privileged else Fore.GREEN}Privileged:     {'[YES]' if privileged else '[NO]'}")
        print(f"{Fore.CYAN}Source:         {source_type} ({source_location})")

        if env_vars:
            print(f"{Fore.WHITE}Environment Variables:")
            for var in env_vars:
                key = var.get("name")
                val = var.get("value")
                print(f"  {key} = {val}")
        else:
            print(f"{Fore.GREEN}No environment variables found.")

        print(f"{Fore.YELLOW}{'=' * 60}")

