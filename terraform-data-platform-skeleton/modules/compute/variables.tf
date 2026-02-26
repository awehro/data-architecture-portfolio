variable "environment" {
  type = string
}

variable "instance_size" {
  type    = string
  default = "small"
  validation {
    condition     = contains(["small", "medium", "large"], var.instance_size)
    error_message = "Must be small, medium, or large."
  }
}
