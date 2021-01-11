import logging
import os
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
    aws_secretsmanager as sm,
)
from aws_cdk.aws_ecr_assets import DockerImageAsset


APPLICATION_NAME = "JavaGoof"


logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


class CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        dockerImageAsset = DockerImageAsset(
            self,
            f"{APPLICATION_NAME}",
            directory="../",
            file="Dockerfile",
            exclude=["cdk/node_modules", ".git", "cdk/cdk.out"],
        )

        logger.info(
            f"Created a docker image and pushed to AWS ECR. ImageName: {dockerImageAsset}"
        )
        vpc = ec2.Vpc(self, f"{APPLICATION_NAME}VPC", max_azs=3)
        cluster = ecs.Cluster(self, f"{APPLICATION_NAME}Cluster", vpc=vpc)


        app_task = ecs.FargateTaskDefinition(
            self, f"{APPLICATION_NAME}-task", cpu=512, memory_limit_mib=2048,
        )

        dd_api_key = sm.Secret.from_secret_name(
            self, secret_name="datadog/java_goof_app_api_key", id="AWSCURRENT"
        )


        app_task.add_container(
            f"{APPLICATION_NAME}",
            image=ecs.ContainerImage.from_docker_image_asset(dockerImageAsset),
            essential=True,
            environment={
                "LOCALDOMAIN": "service.local",
                "DD_PROFILING_ENABLED": "true",
                "DD_ENV": "testing",
                "DD_VERSION": "1.0",
                "DD_TAGS": "app:goofapp,team:moarwaffles",
                "DD_SERVICE": "goof-frontend",
                "DD_API_KEY": ecs.Secret.from_secrets_manager(dd_api_key)
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="FrontendContainer",
                log_retention=logs.RetentionDays.ONE_WEEK,
            ),
        ).add_port_mappings(ecs.PortMapping(container_port=8080, host_port=8080))
        print('wheee')
        app_task_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self,
            id=f"{APPLICATION_NAME}-service",
            service_name=f"{APPLICATION_NAME}",
            cluster=cluster,  # Required
            cpu=512,  # Default is 256
            desired_count=2,  # Default is 1
            task_definition=app_task,
            memory_limit_mib=2048,  # Default is 512
            listener_port=80,
            public_load_balancer=True,
            health_check_grace_period=core.Duration.seconds(120),
        )

        app_task_service.service.connections.allow_from_any_ipv4(
            ec2.Port.tcp(8080), f"{APPLICATION_NAME} app inbound"
        )
