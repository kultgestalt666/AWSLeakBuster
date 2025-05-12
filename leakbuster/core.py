class LeakbusterCore:
    def __init__(self, profile, output_dir=None):
        self.profile = profile
        self.output_dir = output_dir

    def run_scan(self, scan_type):
        if scan_type == "ssm-parameters":
            from leakbuster.modules import ssm_parameter_scanner
            ssm_parameter_scanner.scan_ssm(self.profile)

        elif scan_type == "ssm-documents":
            from leakbuster.modules import ssm_document_scanner
            ssm_document_scanner.scan_ssm_documents(self.profile)

        elif scan_type == "secrets":
            from leakbuster.modules import secrets_scanner
            secrets_scanner.scan_secrets(self.profile)

        elif scan_type == "ec2":
            from leakbuster.modules import ec2_userdata_scanner
            ec2_userdata_scanner.scan_ec2_userdata(self.profile)

        elif scan_type == "lambda-env":
            from leakbuster.modules import lambda_env_scanner
            lambda_env_scanner.scan_lambda_env(self.profile)

        elif scan_type == "lambda-code":
            from leakbuster.modules import lambda_code_downloader
            output_dir = self.output_dir or "lambda"
            lambda_code_downloader.scan_lambda_code(self.profile, output_dir)

        elif scan_type == "glue-env":
            from leakbuster.modules import glue_env_scanner
            glue_env_scanner.scan_glue_jobs(self.profile)

        elif scan_type == "s3":
            from leakbuster.modules import s3_scanner
            s3_scanner.scan_s3(self.profile)

        elif scan_type == "ecs":
            from leakbuster.modules import ecs_task_inspector
            ecs_task_inspector.scan_ecs(self.profile)

        elif scan_type == "beanstalk":
            from leakbuster.modules import beanstalk_env_scanner
            beanstalk_env_scanner.scan_beanstalk(self.profile)

        elif scan_type == "snapshots":
            from leakbuster.modules import snapshot_exposure_scanner
            snapshot_exposure_scanner.scan_snapshots(self.profile)

        elif scan_type == "cloudformation":
            from leakbuster.modules import cloudformation_stack_scanner
            cloudformation_stack_scanner.scan_cloudformation(self.profile)

        elif scan_type == "glue-code":
            from leakbuster.modules import glue_code_downloader
            output_dir = self.output_dir or "glue"
            glue_code_downloader.download_glue_scripts(self.profile, output_dir)

        elif scan_type == "codebuild":
            from leakbuster.modules import codebuild_scanner
            codebuild_scanner.scan_codebuild(self.profile)

        elif scan_type == "cognito":
            from leakbuster.modules import cognito_scanner
            cognito_scanner.scan_cognito_identity_pools(self.profile)

        elif scan_type == "sqs":
            from leakbuster.modules import sqs_scanner
            sqs_scanner.scan_sqs(self.profile)

        elif scan_type == "sns":
            from leakbuster.modules import sns_scanner
            sns_scanner.scan_sns(self.profile)

        elif scan_type == "apigateway":
            from leakbuster.modules import api_gateway_scanner
            api_gateway_scanner.scan_api_gateway(self.profile)

        elif scan_type == "eventbridge":
            from leakbuster.modules import eventbridge_scanner
            eventbridge_scanner.scan_eventbridge(self.profile)

        else:
            print(f"[!] Unknown scan type: {scan_type}")

