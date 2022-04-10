# Variables file for Python script

cluster_name = "ocp4-apse2-07" # Cluster name
install_dir = cluster_name
base_domain = "lab-aws.ldcloud.com.au."
hosted_zone_name = "lab-aws.ldcloud.com.au" # The Route53 zone to register the targets with, such as example.com. Omit the trailing period.

VpcCidr = "10.7.0.0/16"
zone_count = "3"
subnet_bits = "12"

rhcos_ami = "ami-0386d15994420ed12" 