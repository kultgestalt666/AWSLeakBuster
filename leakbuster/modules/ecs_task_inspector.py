import boto3
from botocore.exceptions import ClientError
from botocore import UNSIGNED
from botocore.config import Config
from colorama import Fore, init

init(autoreset=True)

def scan_ecs(profile):
    print(f"[ECS] Inspecting ECS tasks using profile '{profile}'...")
    session = boto3.Session(profile_name=profile)
    ecs = session.client("ecs")
    secretsmanager = session.client("secretsmanager")
    ssm = session.client("ssm")

    try:
        clusters_arns = ecs.list_clusters()["clusterArns"]
    except Exception as e:
        print(f"{Fore.RED}Failed to list clusters: {e}")
        return

    for cluster_arn in clusters_arns:
        cluster_name = cluster_arn.split("/")[-1]
        try:
            cluster_details = ecs.describe_clusters(clusters=[cluster_arn])["clusters"][0]
            exec_enabled = any(s.get("name") == "executeCommand" and s.get("value") == "true"
                               for s in cluster_details.get("settings", []))
        except Exception:
            exec_enabled = None

        try:
            services = ecs.list_services(cluster=cluster_arn)["serviceArns"]
        except Exception:
            continue

        for service_arn in services:
            try:
                service = ecs.describe_services(cluster=cluster_arn, services=[service_arn])["services"][0]
                task_def_arn = service["taskDefinition"]
                task_def = ecs.describe_task_definition(taskDefinition=task_def_arn)["taskDefinition"]

                for container_def in task_def.get("containerDefinitions", []):
                    print(f"\n{Fore.YELLOW}{'=' * 60}")
                    print(f"{Fore.YELLOW}Cluster:         {cluster_name}")
                    print(f"{Fore.CYAN}Service:         {service['serviceName']}")
                    print(f"{Fore.CYAN}Task Definition: {task_def_arn.split('/')[-1]}")
                    print(f"{Fore.CYAN}Container:       {container_def.get('name')}")
                    print(f"{Fore.CYAN}Image:           {container_def.get('image')}")
                    print(f"{Fore.CYAN}IAM Role:        {task_def.get('taskRoleArn', 'N/A')}")

                    if exec_enabled is True:
                        print(f"{Fore.RED}Exec Enabled:    [YES]")
                    elif exec_enabled is False:
                        print(f"{Fore.GREEN}Exec Enabled:    [NO]")
                    else:
                        print(f"{Fore.YELLOW}Exec Enabled:    [?]")

                    log_cfg = container_def.get("logConfiguration")
                    if log_cfg:
                        driver = log_cfg.get("logDriver", "unknown")
                        print(f"{Fore.RED}Logging:         [YES] ({driver})")
                    else:
                        print(f"{Fore.GREEN}Logging:         [NO]")

                    env_vars = container_def.get("environment", [])
                    secrets = container_def.get("secrets", [])

                    if env_vars:
                        print(f"{Fore.WHITE}Env Vars:")
                        for env in env_vars:
                            print(f"  {env['name']} = {env.get('value', '')}")

                    if secrets:
                        print(f"{Fore.BLUE}Secrets (Resolved):")
                        for sec in secrets:
                            name = sec.get('name')
                            ref = sec.get('valueFrom', '')
                            print(f"  {name} ({ref})")
                            if ':parameter/' in ref:
                                param_name = ref.split(':parameter/')[-1]
                                try:
                                    value = ssm.get_parameter(Name=param_name, WithDecryption=True)["Parameter"]["Value"]
                                    print(f"    Value: {value}")
                                except ClientError:
                                    print(f"{Fore.RED}    Access Denied or Decryption Failed")
                            elif ':secret:' in ref:
                                secret_arn = ref
                                try:
                                    value = secretsmanager.get_secret_value(SecretId=secret_arn)["SecretString"]
                                    print(f"    Value: {value}")
                                except ClientError:
                                    print(f"{Fore.RED}    Access Denied or Decryption Failed")
                            else:
                                print(f"{Fore.YELLOW}    Unknown source")
                    print(f"{Fore.YELLOW}{'=' * 60}")
            except Exception as e:
                print(f"{Fore.RED}Failed to inspect service {service_arn}: {e}")

