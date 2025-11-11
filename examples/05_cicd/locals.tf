locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  pipeline_name = "${var.project_name}-pipeline"
}

