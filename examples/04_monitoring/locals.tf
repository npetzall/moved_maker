locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  alert_topic_arn = aws_sns_topic.alerts.arn
}

