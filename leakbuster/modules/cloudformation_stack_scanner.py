import boto3
from botocore.exceptions import ClientError
from colorama import Fore, init

init(autoreset=True)

def scan_cloudformation(profile):
    print(f"[CloudFormation] Scanning stack parameters and outputs using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    cf = session.client("cloudformation")
    sts = session.client("sts")

    account_id = sts.get_caller_identity()["Account"]
    region = session.region_name

    try:
        stacks = cf.describe_stacks()["Stacks"]
    except ClientError as e:
        print(f"{Fore.RED}Failed to list stacks: {e}")
        return

    for stack in stacks:
        stack_name = stack["StackName"]
        stack_id = stack["StackId"]
        stack_status = stack.get("StackStatus", "Unknown")
        stack_arn = f"arn:aws:cloudformation:{region}:{account_id}:stack/{stack_name}/{stack_id.split('/')[-1]}"

        visible_params = []
        output_values = []

        # Parameters
        params = stack.get("Parameters", [])
        for param in params:
            key = param.get("ParameterKey", "")
            val = param.get("ParameterValue", "")
            no_echo = param.get("NoEcho", False)
            if not no_echo and val:
                visible_params.append(f"  {key} = {val}")

        # Outputs
        outputs = stack.get("Outputs", [])
        for out in outputs:
            key = out.get("OutputKey", "")
            val = out.get("OutputValue", "")
            if val:
                output_values.append(f"  {key} = {val}")

        if visible_params or output_values:
            print(f"\n{Fore.YELLOW}{'=' * 60}")
            print(f"{Fore.YELLOW}Stack:      {stack_name}")
            print(f"{Fore.CYAN}ARN:        {stack_arn}")
            print(f"{Fore.CYAN}Status:     {stack_status}")

            if visible_params:
                print(f"{Fore.WHITE}Visible Parameters:")
                for line in visible_params:
                    print(Fore.WHITE + line)

            if output_values:
                print(f"{Fore.BLUE}Stack Outputs:")
                for line in output_values:
                    print(Fore.BLUE + line)

            print(f"{Fore.YELLOW}{'=' * 60}")

