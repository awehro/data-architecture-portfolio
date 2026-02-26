module "network" {
  source      = "../../modules/network"
  environment = "dev"
  vpc_cidr    = "10.1.0.0/16"
}

module "storage" {
  source         = "../../modules/storage"
  environment    = "dev"
  retention_days = 7
}

module "compute" {
  source        = "../../modules/compute"
  environment   = "dev"
  instance_size = "small"
}
