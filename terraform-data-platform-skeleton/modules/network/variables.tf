variable "environment" {
  description = "Deployment environment (dev/prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the virtual network"
  type        = string
  default     = "10.0.0.0/16"
}
