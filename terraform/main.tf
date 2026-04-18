terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Fetch the latest Amazon Linux 2023 AMI dynamically
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# Define the Security Group firewall rules
resource "aws_security_group" "fastapi_sg" {
  name        = "fastapi-web-sg"
  description = "Allow inbound SSH and HTTP traffic"

  # SSH Access for remote deployment commands
  ingress {
    description = "Allow SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Application Access for the FastAPI service
  ingress {
    description = "Allow application traffic"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound Internet Access for downloading dependencies
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Provision the EC2 Instance
resource "aws_instance" "fastapi_server" {
  ami             = data.aws_ami.amazon_linux_2023.id
  instance_type   = "t3.micro"
  vpc_security_group_ids = [aws_security_group.fastapi_sg.id]
  
  # The SSH key pair name
  key_name        = "fastapi-key" 

  # Bootstrapping script to install Docker via cloud-init
  user_data = <<-EOF
              #!/bin/bash
              # Update package repository using DNF
              dnf update -y
              
              # Install Docker directly from the AL2023 repository
              dnf install -y docker
              
              # Start and enable the Docker service to persist across reboots
              systemctl start docker
              systemctl enable docker
              
              # Grant the default user permissions to run Docker commands without sudo
              usermod -aG docker ec2-user
              EOF

  tags = {
    Name = "FastAPI-Production-Server"
  }
}

# Output the public IP address for downstream CI/CD utilization
output "server_public_ip" {
  value = aws_instance.fastapi_server.public_ip
}