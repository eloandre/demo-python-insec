# Insecure IaC - Terraform para AWS (EXEMPLO)
provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "insecure_sg" {
  name        = "insecure-sg-py"
  description = "Security group inseguro com portas abertas"

  ingress {
    description = "Porta da aplicação aberta para o mundo"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Porta do banco de dados aberta para o mundo"
    from_port   = 3306
    to_port     = 3306
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

resource "aws_instance" "insecure_app" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"
  key_name      = "hardcoded-ssh-key-py"

  vpc_security_group_ids = [aws_security_group.insecure_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              curl -sL https://rpm.nodesource.com/setup_20.x | bash -   # exemplo apenas
              EOF

  tags = {
    Name = "InsecureAppInstancePy"
  }
}

resource "aws_db_instance" "insecure_db" {
  identifier           = "insecure-db-py"
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t2.micro"
  username             = "admin"
  password             = "Admin123!"
  publicly_accessible  = true
  skip_final_snapshot  = true

  vpc_security_group_ids = [aws_security_group.insecure_sg.id]
}

