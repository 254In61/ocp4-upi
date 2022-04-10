
from doctest import OutputChecker
import os
import json
import time
from create_stacks import *
from pymodules.python_editable_vars import *


# VPC Varibles

class Vpc:
    def __init__(self,par1):
        self.__par1 = par1

    def process(self):
        # Create json file
        vpc_tmplt = [
            {"ParameterKey": "VpcCidr", "ParameterValue": VpcCidr },
            {"ParameterKey": "AvailabilityZoneCount", "ParameterValue": zone_count },
            {"ParameterKey": "SubnetBits", "ParameterValue": subnet_bits }
            ]

        write_to_json("files/jsons/vpc.json",vpc_tmplt)
        
        # Create vpc_stack
        stack_name = cluster_name + "-vpc"

        dict_x = create_stack(stack_name,"vpc","vpc")

        return dict_x
      
class Network:
    def __init__(self,vpc_dict):
        self.vpc_dict = vpc_dict

    def process(self):
        # Create json file
        net_tmplt= [
            {"ParameterKey": "ClusterName", "ParameterValue": cluster_name },
            {"ParameterKey": "InfrastructureName", "ParameterValue": infra_name()},
            {"ParameterKey": "HostedZoneId", "ParameterValue": hosted_zone()},
            {"ParameterKey": "HostedZoneName", "ParameterValue": hosted_zone_name },
            {"ParameterKey": "PublicSubnets", "ParameterValue": get_value("PublicSubnetIds",self.vpc_dict) },
            {"ParameterKey": "PrivateSubnets", "ParameterValue": get_value("PrivateSubnetIds",self.vpc_dict)},
            {"ParameterKey": "VpcId", "ParameterValue": get_value("VpcId",self.vpc_dict)}]

        # print(in_dict)
        write_to_json("files/jsons/network.json",net_tmplt)
        
        # Create vpc_stack
        stack_name = cluster_name + "-network"
        dict_x = create_stack(stack_name,"network","network")

        # print(dict_x)
        # print(dict_x["Stacks"][0]["Outputs"])

        return dict_x

class SecGrp:
    def __init__(self,vpc_dict):
        self.vpc_dict = vpc_dict

    def process(self):
        # Create json file
        sec_tmplt= [
            {"ParameterKey": "InfrastructureName", "ParameterValue": infra_name() },
            {"ParameterKey": "VpcCidr", "ParameterValue": VpcCidr },
            {"ParameterKey": "PrivateSubnets", "ParameterValue": get_value("PrivateSubnetIds",self.vpc_dict) },
            {"ParameterKey": "VpcId", "ParameterValue": get_value("VpcId",self.vpc_dict)}]

        # print(in_dict)
        write_to_json("files/jsons/sec.json",sec_tmplt)
        
        # Create vpc_stack
        stack_name = cluster_name + "-secgrp"
        dict_x = create_stack(stack_name,"sec","sec")

        # print(dict_x)
        # print(dict_x["Stacks"][0]["Outputs"])

        return dict_x


class BootStrap:
    def __init__(self,vpc_dict,net_dict,sec_dict):
        self.vpc_dict = vpc_dict
        self.net_dict = net_dict
        self.sec_dict = sec_dict

    def process(self):
        # Create json file
        print("\nCreate an s3 bucket to hold the bootstrap.ign ignition config file for the cluster.............")
        cmd = "aws s3 mb s3://{}-infra".format(cluster_name)
        print("COMMAND : ", cmd)
        print(os.system(cmd),"\n")

        print("\nUpload the bootstrap.ign Ignition config file to the bucket..............")
        cmd = "aws s3 cp {}/bootstrap.ign s3://{}-infra/bootstrap.ign".format(install_dir,cluster_name)
        print("COMMAND : ", cmd)
        print(os.system(cmd),"\n")

        print("\nVerify that the file is uploaded .......")
        cmd = "aws s3 ls s3://{}-infra/".format(cluster_name)
        print("COMMAND : ", cmd)
        print(os.system(cmd),"\n")

        boot_tmplt = [
        {"ParameterKey": "InfrastructureName", "ParameterValue": infra_name()},
        {"ParameterKey": "RhcosAmi", "ParameterValue": rhcos_ami },
        {"ParameterKey": "AllowedBootstrapSshCidr", "ParameterValue": "0.0.0.0/0" },
        {"ParameterKey": "PublicSubnet", "ParameterValue": get_value("PublicSubnetIds",self.vpc_dict).split(",")[0] },
        {"ParameterKey": "MasterSecurityGroupId", "ParameterValue": get_value("MasterSecurityGroupId",self.sec_dict)},
        {"ParameterKey": "VpcId", "ParameterValue": get_value("VpcId",self.vpc_dict)},
        {"ParameterKey": "BootstrapIgnitionLocation", "ParameterValue": "s3://{}-infra/bootstrap.ign".format(cluster_name) },
        {"ParameterKey": "AutoRegisterELB", "ParameterValue": "yes" },
        {"ParameterKey": "RegisterNlbIpTargetsLambdaArn", "ParameterValue": get_value("RegisterNlbIpTargetsLambda",self.net_dict) },
        {"ParameterKey": "ExternalApiTargetGroupArn", "ParameterValue": get_value("ExternalApiTargetGroupArn",self.net_dict)},
        {"ParameterKey": "InternalApiTargetGroupArn", "ParameterValue": get_value("InternalApiTargetGroupArn",self.net_dict)},
        {"ParameterKey": "InternalServiceTargetGroupArn", "ParameterValue": get_value("InternalServiceTargetGroupArn",self.net_dict) }
        ]
        
        # In bootstrap.yml validation for PublicIPSubetIds is for only 1, unlike network.yml which validates a list.



        # print(in_dict)
        write_to_json("files/jsons/bootstrap.json",boot_tmplt)
        
        # Create vpc_stack
        stack_name = cluster_name + "-bootstrap"
        dict_x = create_stack(stack_name,"bootstrap","bootstrap")

        # print(dict_x)
        return dict_x

class ControlPlane:
    def __init__(self,vpc_dict,net_dict,sec_dict,boot_dict):
        self.vpc_dict = vpc_dict
        self.net_dict = net_dict
        self.sec_dict = sec_dict
        self.boot_dict = boot_dict

    def process(self):
        # Create json file
        private_hosted_zone_name = cluster_name + "." + hosted_zone_name
        ignition_location,certificate_authority = master_ign()
        controlplane_tmplt = [
        {"ParameterKey": "InfrastructureName", "ParameterValue": infra_name()},
        {"ParameterKey": "RhcosAmi", "ParameterValue": rhcos_ami },
        {"ParameterKey": "AutoRegisterDNS", "ParameterValue": "yes" },
        {"ParameterKey": "PrivateHostedZoneId", "ParameterValue": get_value("PrivateHostedZoneId",self.net_dict) },
        {"ParameterKey": "PrivateHostedZoneName", "ParameterValue": private_hosted_zone_name},
        {"ParameterKey": "Master0Subnet", "ParameterValue": get_value("PrivateSubnetIds",self.vpc_dict).split(",")[0]},
        {"ParameterKey": "Master1Subnet", "ParameterValue": get_value("PrivateSubnetIds",self.vpc_dict).split(",")[1]},
        {"ParameterKey": "Master2Subnet", "ParameterValue": get_value("PrivateSubnetIds",self.vpc_dict).split(",")[2]},
        {"ParameterKey": "MasterSecurityGroupId", "ParameterValue": get_value("MasterSecurityGroupId",self.sec_dict)},
        {"ParameterKey": "IgnitionLocation", "ParameterValue": ignition_location},
        {"ParameterKey": "CertificateAuthorities", "ParameterValue": certificate_authority},
        {"ParameterKey": "MasterInstanceProfileName", "ParameterValue": get_value("MasterInstanceProfile",self.sec_dict)},
        {"ParameterKey": "MasterInstanceType","ParameterValue": "m5.xlarge"},
        {"ParameterKey": "AutoRegisterELB", "ParameterValue": "yes" },
        {"ParameterKey": "RegisterNlbIpTargetsLambdaArn", "ParameterValue": get_value("RegisterNlbIpTargetsLambda",self.net_dict) },
        {"ParameterKey": "ExternalApiTargetGroupArn", "ParameterValue": get_value("ExternalApiTargetGroupArn",self.net_dict)},
        {"ParameterKey": "InternalApiTargetGroupArn", "ParameterValue": get_value("InternalApiTargetGroupArn",self.net_dict)},
        {"ParameterKey": "InternalServiceTargetGroupArn", "ParameterValue": get_value("InternalServiceTargetGroupArn",self.net_dict) }
        ]
        
        # print(in_dict)
        write_to_json("files/jsons/controlplane.json",controlplane_tmplt)
        
        # Create vpc_stack
        stack_name = cluster_name + "-controlplane"
        dict_x = create_stack(stack_name,"controlplane","controlplane")

        # print(dict_x)
        return dict_x

class WorkerNode:
    def __init__(self,vpc_dict,net_dict,sec_dict,boot_dict):
        self.vpc_dict = vpc_dict
        self.net_dict = net_dict
        self.sec_dict = sec_dict
        self.boot_dict = boot_dict

    def process(self):
        # Create json file
        ignition_location,certificate_authority = master_ign()
        workernode_tmplt = [
        {"ParameterKey": "InfrastructureName", "ParameterValue": infra_name()},
        {"ParameterKey": "RhcosAmi", "ParameterValue": rhcos_ami },
        {"ParameterKey": "Subnet", "ParameterValue": get_value("PrivateSubnetIds",self.vpc_dict).split(",")[0]},
        {"ParameterKey": "WorkerSecurityGroupId", "ParameterValue": get_value("WorkerSecurityGroupId",self.sec_dict)},
        {"ParameterKey": "IgnitionLocation", "ParameterValue": ignition_location},
        {"ParameterKey": "CertificateAuthorities", "ParameterValue": certificate_authority},
        {"ParameterKey": "WorkerInstanceProfileName", "ParameterValue": get_value("WorkerInstanceProfile",self.sec_dict)},
        {"ParameterKey": "WorkerInstanceType", "ParameterValue": "m4.2xlarge"}
        ]
        
        # print(in_dict)
        write_to_json("files/jsons/workernode.json",workernode_tmplt)
        
        # Create vpc_stack
        stack_name = cluster_name + "-workernode"
        dict_x = create_stack(stack_name,"workernode","workernode")

        # print(dict_x)
        return dict_x

def create_stack(stack_name,yaml_file,json_file):
    print("\nCreating stack : ", stack_name)
    cmd1 = "aws cloudformation create-stack --stack-name {} --template-body file://files/yamls/{}.yaml --parameters file://files/jsons/{}.json --capabilities CAPABILITY_NAMED_IAM".format(stack_name,yaml_file,json_file)
    print("COMMAND : ",cmd1)
    print(os.system(cmd1),"\n")

    #time.sleep(60) # Time for stack to create

    # Pass a command that extracts json data about the created stack.
    # Since os.system(cmd) direct output cannot be used as a variable, I write it on a text file, files/cmd_output first.
    # I read the file as a json data string and convert it to dictionary.
    print("\nRead stack details and write output to files/cmd_output...........")
    cmd2 = "aws cloudformation describe-stacks --stack-name {} > files/cmd_output".format(stack_name)
    print("COMMAND : ",cmd2)
    print(os.system(cmd2),"\n")
    
    with open("files/cmd_output") as in_file:
        dict_x = json.load(in_file)
    
    # Return a list item with encapulated dictionaries

    try:
        return dict_x["Stacks"][0]["Outputs"]
    except KeyError:
        print("Stack info not yet extracted")
        return {}

def write_to_json(json_file_name,list_tmplt):
    # Function to write the different list of dictionaries templates of values/variables into the jsons/<stack_name>.json files.
    # The list of dictionary template is converted to json data string first and then written onto the file and saved.
    # You cannot write a string directly to a file itself.
    # This .json file serves as an input to the "aws cloudformation create-stack --stack-name" command.
    json_str = json.dumps(list_tmplt)
    f = open(json_file_name,"w")
    f.write(json_str)
    f.close()

def get_value(key,d):
    # Function to run search and return the value for a given key in a given dictionary.
    # Dictionary are extracted from the "Outputs" section of the created stacks
    for item in d:
        if item['OutputKey'] == key:
            print(item['OutputKey']," : ",item['OutputValue'])
            value = item['OutputValue']

    return value


def master_ign():
    # Function to extract values for different sections of the master.ign file.
    # These values are needed as parameters for creating the control plane machines in AWS
    # I read the master.ign , found in the install directory , as json file then convert the json string into a dictionary.
    
    in_file = install_dir + "/master.ign"
    with open(in_file) as in_file:
        dict_x = json.load(in_file)
    
    # Created dictionary has structure like below:
    # {
    # 'ignition': 
    # {
    # 'config': {'merge': [{'source': 'https://api-int.ocp4-apse2-07.lab-aws.ldcloud.com.au:22623/config/master'}]}, 
    # 'security': {'tls': {'certificateAuthorities': [{'source': 'data:text/plain;charset=utf-8;base64,LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURFRENDQWZpZ0F3SUJ'}]}}, 
    # 'version': '3.2.0'
    # }
    # }
    ignition_location = dict_x['ignition']['config']['merge'][0]['source']
    certificate_authority = dict_x['ignition']['security']['tls']['certificateAuthorities'][0]['source']

    return ignition_location,certificate_authority
    