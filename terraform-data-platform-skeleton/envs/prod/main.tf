module "network" {
  source      = "../../modules/network"
  environment = "prod"
  vpc_cidr    = "10.0.0.0/16"
}

module "storage" {
  source         = "../../modules/storage"
  environment    = "prod"
  retention_days = 365
}

module "compute" {
  source        = "../../modules/compute"
  environment   = "prod"
  instance_size = "large"
}
