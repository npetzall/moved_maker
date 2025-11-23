output "dev_instance_ids" {
  description = "Development environment instance IDs"
  value       = module.development.instance_ids
}

output "staging_instance_ids" {
  description = "Staging environment instance IDs"
  value       = module.staging.instance_ids
}

output "prod_instance_ids" {
  description = "Production environment instance IDs"
  value       = module.production.instance_ids
}

output "dev_database_endpoint" {
  description = "Development database endpoint"
  value       = module.development.database_endpoint
  sensitive   = true
}

output "staging_database_endpoint" {
  description = "Staging database endpoint"
  value       = module.staging.database_endpoint
  sensitive   = true
}

output "prod_database_endpoint" {
  description = "Production database endpoint"
  value       = module.production.database_endpoint
  sensitive   = true
}

output "shared_s3_bucket" {
  description = "Shared S3 bucket name"
  value       = module.shared_resources.bucket_name
}

output "shared_log_group" {
  description = "Shared CloudWatch log group name"
  value       = module.shared_resources.log_group_name
}
