import os
from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_logs as logs,
    aws_ssm as ssm,
)
from aws_cdk.aws_ecr_assets import DockerImageAsset

VERSION = "1.0"
APPLICATION_NAME = "javaGoof"
DD_TAGS = "app:goofapp,team:moarwaffles"
DD_SERVICE = APPLICATION_NAME.lower()
DD_ENV = "testing"

DATADOG_AGENT_VARS = dict(
    LOCALDOMAIN="service.local",
    DD_ENV=DD_ENV,
    DD_VERSION=VERSION,
    DD_TAGS=DD_TAGS,
    DD_SERVICE=DD_SERVICE,
    DD_APM_ENABLED="true",
    DD_APM_NON_LOCAL_TRAFFIC="true",
    ECS_FARGATE="true",
    DD_LOGS_INJECTION="true"
)

APP_ENV_VARS = dict(
    LOCALDOMAIN="service.local",
    DD_ENV="testing",
    DD_VERSION=VERSION,
    DD_TAGS=DD_TAGS,
    DD_SERVICE=DD_SERVICE,
    DD_PROFILING_ENABLED="true",
    MAVEN_OPTS="-javaagent:dd-java-agent.jar -XX:FlightRecorderOptions=stackdepth=256",
)


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

        vpc = ec2.Vpc(self, f"{APPLICATION_NAME}VPC", max_azs=3)
        cluster = ecs.Cluster(self, f"{APPLICATION_NAME}Cluster", vpc=vpc)

        app_task = ecs.FargateTaskDefinition(
            self,
            f"{APPLICATION_NAME}-task",
            family=f"{APPLICATION_NAME}-family",
            cpu=512,
            memory_limit_mib=2048,
        )

        dd_api_key = ssm.StringParameter.value_for_string_parameter(
            self, "/datadog/snyk_demo/dd_api_key"
        )

        DATADOG_AGENT_VARS["DD_API_KEY"] = dd_api_key

        java_service_container = app_task.add_container(
            f"{APPLICATION_NAME}-java-app",
            image=ecs.ContainerImage.from_docker_image_asset(dockerImageAsset),
            essential=True,
            docker_labels={
                "com.datadoghq.ad.instances": '[{"host": "%%host%%", "port": 6379}]',
                "com.datadoghq.ad.check_names": '["tomcat"]',
                "com.datadoghq.ad.init_configs": "[{}]",
            },
            environment=APP_ENV_VARS,
            logging=ecs.LogDrivers.firelens(
                options={
                    "Name": "datadog",
                    "Host": "http-intake.logs.datadoghq.com",
                    "TLS": "on",
                    "apikey": dd_api_key,
                    "dd_service": DD_SERVICE,
                    "dd_source": "tomcat",
                    "dd_tags": DD_TAGS,
                    "provider": "ecs",
                }
            ),
        )

        datadog_agent_container = app_task.add_container(
            f"{APPLICATION_NAME}-datadog-agent",
            image=ecs.ContainerImage.from_registry(name="datadog/agent:latest"),
            essential=True,
            environment=DATADOG_AGENT_VARS,
        )

        # Port exposure for the containerized app
        java_service_container.add_port_mappings(
            ecs.PortMapping(container_port=8080, host_port=8080)
        )

        # Mandatory port exposure for the Datadog agent
        datadog_agent_container.add_port_mappings(
            ecs.PortMapping(container_port=8126, host_port=8126)
        )

        app_task_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self,
            id=f"{APPLICATION_NAME}-service",
            service_name=f"{APPLICATION_NAME}",
            cluster=cluster,  # Required
            cpu=512,  # Default is 256
            desired_count=1,  # Default is 1
            task_definition=app_task,
            memory_limit_mib=2048,  # Default is 512
            listener_port=80,
            public_load_balancer=True,
            health_check_grace_period=core.Duration.seconds(120),
        )

        # Security Group to allow load balancer to communicate with ECS Containers.
        app_task_service.service.connections.allow_from_any_ipv4(
            ec2.Port.tcp(8080), f"{APPLICATION_NAME} app inbound"
        )
