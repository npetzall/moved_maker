locals {
  common_tags = {
    Project     = var.cluster_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  cluster_name = "${var.cluster_name}-${var.environment}"
}

