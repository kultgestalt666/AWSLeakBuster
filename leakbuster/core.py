from leakbuster.modules import (
    ssm_parameter_scanner,
    ssm_document_scanner,
    secrets_scanner,
    ec2_userdata_scanner,
    lambda_env_scanner,
    lambda_code_downloader,
    s3_scanner,
    ecs_task_inspector,
    beanstalk_env_scanner,
    snapshot_exposure_scanner,
    cloudformation_stack_scanner,
    glue_env_scanner,
    glue_code_downloader,
    codebuild_scanner,
    cognito_scanner,
    sqs_scanner,
    sns_scanner,
    api_gateway_scanner,
    eventbridge_scanner
)

class LeakbusterCore:
    def __init__(self, profile, output_dir=None):
        self.profile = profile
        self.output_dir = output_dir

    def run_scan(self, scan_type):
        if scan_type == "ssm-parameters":
            ssm_parameter_scanner.scan_ssm(self.profile)

        elif scan_type == "ssm-documents":
            ssm_document_scanner.scan_ssm_documents(self.profile)

        elif scan_type == "secrets":
            secrets_scanner.scan_secrets(self.profile)

        elif scan_type == "ec2":
            ec2_userdata_scanner.scan_ec2_userdata(self.profile)

        elif scan_type == "lambda-env":
            lambda_env_scanner.scan_lambda_env(self.profile)

        elif scan_type == "lambda-code":
            output_dir = self.output_dir or "lambda"
            lambda_code_downloader.scan_lambda_code(self.profile, output_dir)

        elif scan_type == "glue-env":
            glue_env_scanner.scan_glue_jobs(self.profile)

        elif scan_type == "s3":
            s3_scanner.scan_s3(self.profile)

        elif scan_type == "ecs":
            ecs_task_inspector.scan_ecs(self.profile)

        elif scan_type == "beanstalk":
            beanstalk_env_scanner.scan_beanstalk(self.profile)

        elif scan_type == "snapshots":
            snapshot_exposure_scanner.scan_snapshots(self.profile)
        
        elif scan_type == "cloudformation":
            cloudformation_stack_scanner.scan_cloudformation(self.profile)

        elif scan_type == "glue-code":
            output_dir = self.output_dir or "glue"
            glue_code_downloader.download_glue_scripts(self.profile, output_dir)

        elif scan_type == "codebuild":
            codebuild_scanner.scan_codebuild(self.profile)

        elif scan_type == "cognito":
            cognito_scanner.scan_cognito_identity_pools(self.profile)

        elif scan_type == "sqs":
            sqs_scanner.scan_sqs(self.profile)

        elif scan_type == "sns":
            sns_scanner.scan_sns(self.profile)

        elif scan_type == "apigateway":
            api_gateway_scanner.scan_api_gateway(self.profile)

        elif scan_type == "eventbridge":
            eventbridge_scanner.scan_eventbridge(self.profile)

        else:
            print(f"[!] Unknown scan type: {scan_type}")

