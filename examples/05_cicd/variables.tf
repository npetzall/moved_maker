variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "repository_name" {
  description = "Name of the CodeCommit repository"
  type        = string
}

variable "branch_name" {
  description = "Branch name to build from"
  type        = string
  default     = "main"
}

variable "buildspec_file" {
  description = "Path to buildspec file"
  type        = string
  default     = "buildspec.yml"
}

variable "build_compute_type" {
  description = "CodeBuild compute type"
  type        = string
  default     = "BUILD_GENERAL1_SMALL"
}

variable "build_image" {
  description = "CodeBuild image"
  type        = string
  default     = "aws/codebuild/standard:5.0"
}

variable "deployment_bucket" {
  description = "S3 bucket name for deployment"
  type        = string
}

