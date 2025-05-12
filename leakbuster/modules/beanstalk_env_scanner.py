import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def scan_beanstalk(profile):
    print(f"[Beanstalk] Scanning environments using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    eb = session.client("elasticbeanstalk")

    try:
        apps = eb.describe_applications()["Applications"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to list applications: {e}")
        return

    for app in apps:
        app_name = app["ApplicationName"]

        try:
            envs = eb.describe_environments(ApplicationName=app_name)["Environments"]
        except ClientError as e:
            print(f"{Fore.RED}Failed to list environments for {app_name}: {e}")
            continue

        for env in envs:
            env_name = env["EnvironmentName"]
            region = session.region_name
            platform = env.get("PlatformArn", "Unknown")
            solution = env.get("SolutionStackName", "Unknown")
            env_id = env["EnvironmentId"]

            try:
                settings = eb.describe_configuration_settings(
                    ApplicationName=app_name,
                    EnvironmentName=env_name
                )["ConfigurationSettings"][0]["OptionSettings"]
            except ClientError as e:
                print(f"{Fore.RED}Failed to get config for {env_name}: {e}")
                continue

            env_vars = []
            iam_profile = "N/A"

            for opt in settings:
                ns = opt.get("Namespace", "")
                if ns == "aws:elasticbeanstalk:application:environment":
                    env_vars.append((opt["OptionName"], opt["Value"]))
                elif ns == "aws:autoscaling:launchconfiguration" and opt["OptionName"] == "IamInstanceProfile":
                    iam_profile = opt["Value"]

            print(f"\n{Fore.YELLOW}{'=' * 60}")
            print(f"{Fore.YELLOW}App:        {app_name}")
            print(f"{Fore.CYAN}Env:        {env_name}")
            print(f"{Fore.CYAN}Region:     {region}")
            print(f"{Fore.CYAN}Platform:   {platform}")
            print(f"{Fore.CYAN}Solution:   {solution}")
            print(f"{Fore.CYAN}IAM Role:   {iam_profile}")

            if env_vars:
                print(f"{Fore.WHITE}Env Vars:")
                for name, value in env_vars:
                    print(f"  {name} = {value}")
            else:
                print(f"{Fore.GREEN}No environment variables found.")

            print(f"{Fore.YELLOW}{'=' * 60}")

