terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

variable "region" {
  default = "us-east-1"
}

variable "image_tag" {
  default = "latest"
}

variable "deepseek_api_key" {
  type      = string
  sensitive = true
}

variable "gemini_api_key" {
  type      = string
  sensitive = true
}

provider "aws" {
  region = var.region
}

locals {
  name = "aistylist"
}

# ponytail: default VPC + public subnets, add a dedicated VPC with private subnets/NAT when needed
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_ecr_repository" "app" {
  for_each     = toset(["api", "web"])
  name         = "${local.name}-${each.key}"
  force_delete = true
}

resource "aws_ssm_parameter" "deepseek_key" {
  name  = "/${local.name}/deepseek_api_key"
  type  = "SecureString"
  value = var.deepseek_api_key
}

resource "aws_ssm_parameter" "gemini_key" {
  name  = "/${local.name}/gemini_api_key"
  type  = "SecureString"
  value = var.gemini_api_key
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${local.name}"
  retention_in_days = 14
}

# --- IAM ---

resource "aws_iam_role" "execution" {
  name = "${local.name}-ecs-execution"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "sts:AssumeRole", Principal = { Service = "ecs-tasks.amazonaws.com" } }]
  })
}

resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "read_secret" {
  role = aws_iam_role.execution.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "ssm:GetParameters", Resource = [aws_ssm_parameter.deepseek_key.arn, aws_ssm_parameter.gemini_key.arn] }]
  })
}

# --- network ---

resource "aws_security_group" "alb" {
  name   = "${local.name}-alb"
  vpc_id = data.aws_vpc.default.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "task" {
  name   = "${local.name}-task"
  vpc_id = data.aws_vpc.default.id
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ponytail: HTTP only, add an ACM cert + 443 listener once there's a domain
resource "aws_lb" "app" {
  name            = local.name
  subnets         = data.aws_subnets.default.ids
  security_groups = [aws_security_group.alb.id]
  idle_timeout    = 300 # agent runs can pause between SSE events
}

resource "aws_lb_target_group" "web" {
  name        = "${local.name}-web"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.aws_vpc.default.id
  health_check {
    path = "/"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

# --- ECS ---

resource "aws_ecs_cluster" "app" {
  name = local.name
}

# One task, two containers: nginx (web) proxies /api to uvicorn over localhost.
resource "aws_ecs_task_definition" "app" {
  family                   = local.name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.execution.arn
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64" # matches images built on Apple Silicon
  }

  container_definitions = jsonencode([
    {
      name         = "web"
      image        = "${aws_ecr_repository.app["web"].repository_url}:${var.image_tag}"
      essential    = true
      portMappings = [{ containerPort = 80 }]
      dependsOn    = [{ containerName = "api", condition = "START" }]
      logConfiguration = {
        logDriver = "awslogs"
        options   = { awslogs-group = aws_cloudwatch_log_group.app.name, awslogs-region = var.region, awslogs-stream-prefix = "web" }
      }
    },
    {
      name      = "api"
      image     = "${aws_ecr_repository.app["api"].repository_url}:${var.image_tag}"
      essential = true
      secrets = [
        { name = "DEEPSEEK_API_KEY", valueFrom = aws_ssm_parameter.deepseek_key.arn },
        { name = "GEMINI_API_KEY", valueFrom = aws_ssm_parameter.gemini_key.arn },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options   = { awslogs-group = aws_cloudwatch_log_group.app.name, awslogs-region = var.region, awslogs-stream-prefix = "api" }
      }
    },
  ])
}

resource "aws_ecs_service" "app" {
  name            = local.name
  cluster         = aws_ecs_cluster.app.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.task.id]
    assign_public_ip = true # needed to pull images without a NAT gateway
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.web.arn
    container_name   = "web"
    container_port   = 80
  }

  depends_on = [aws_lb_listener.http]
}

output "url" {
  value = "http://${aws_lb.app.dns_name}"
}

output "ecr" {
  value = { for k, r in aws_ecr_repository.app : k => r.repository_url }
}
