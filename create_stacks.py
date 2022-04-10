# Python script to do the work for me! 
# Ansible script become too complex.

from doctest import OutputChecker
import os
import json
from pymodules.ocp4_packages import *
from pymodules.python_editable_vars import *
import time


# https://ap-southeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-southeast-2#ImageDetails:imageId=ami-0386d15994420ed12


def command_run(cmd):
    print("COMMAND : ",cmd)
    output = os.system(cmd)
    # print(output)
    return output

def infra_name():
    print("\nObtain infrastructure name ......")
    cmd = "jq -r .infraID {}/metadata.json > files/cmd_output".format(install_dir)
    print("COMMAND : ", cmd)
    output = os.system(cmd)
    print(output)

    print("infrastructure name : ",open("files/cmd_output","r").read().rstrip())
    return open("files/cmd_output","r").read().rstrip()

def hosted_zone():
    # Function to obtain hosted zone ID
    print("\nObtain hosted zone ID value....")
    cmd = "aws route53 list-hosted-zones-by-name --dns-name {} > files/cmd_output".format(base_domain)
    print("COMMAND : ", cmd)
    output = os.system(cmd)
    print(output,"\n")
    
    with open("files/cmd_output") as in_file:
        dict_x = json.load(in_file)
  
    # print(dict_x)
    
    for item in dict_x['HostedZones']:
        if item["Name"] == base_domain:
            print("domain_name = ", base_domain, " : hosted_zone_id = ",item["Id"].replace("/hostedzone/",""))
    
    return item["Id"].replace("/hostedzone/","")


    
def main():
    print("\n*******CREATING A VPC IN AWS*****************\n")
    vpc_dict = Vpc("random").process()
    print("\n")
    #print(vpc_dict)
    
    print("\n******CREATING NETWORKING AND LOAD BALANCING COMPONENTS****************\n")
    net_dict = Network(vpc_dict).process()
    print(net_dict)

    print("\n******CREATING SECURITY GROUPS***********************\n")
    sec_dict = SecGrp(vpc_dict).process()
    print(sec_dict)

    print("\n******CREATING THE BOOTSTRAP***********************\n")
    boot_dict = BootStrap(vpc_dict,net_dict,sec_dict).process()
    print(boot_dict)

    print("\n******CREATING THE CONTROL PLANE NODES***********************\n")
    controlplane_dict = ControlPlane(vpc_dict,net_dict,sec_dict,boot_dict).process()
    print(controlplane_dict)

    print("\n******CREATING THE WORKER NODES***********************\n")
    workernode_dict = WorkerNode(vpc_dict,net_dict,sec_dict,boot_dict).process()
    print(workernode_dict)


if __name__ == "__main__":
    main()
