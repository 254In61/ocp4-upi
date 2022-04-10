SUMMARY
--------
- Code helps in automating the building of OCP4 cluster through User Provisioned Infrastructure (UPI)

UPI INSTALLATION SUMMARY STEPS
------------------------------
    1) configure an AWS account.
    2) Add your AWS keys and region to your local AWS profile by running aws configure.
    3) Generate the Ignition config files for your cluster.
    4) Create and configure AWS Virtual Private Cloud (VPC) and associated subnets in AWS.
    5) Create and configure Networking and load balancing components [ DNS, load balancers, and listeners in AWS.]
    6) Create security groups and roles required for your cluster in AWS.
    7) Create OpenShift Container Platform bootstrap node
    8) Create OpenShift Container Platform control plane nodes
    9) Create the OpenShift Container Platform compute/worker nodes.
    10) start the bootstrap sequence that initializes the OpenShift Container Platform control plane
    11) install the OpenShift CLI (oc) to interact with OpenShift Container Platform from a command-line interface. 
    12) Logging in to the cluster by using the CLI
    13) Approve the certificate signing requests for your machines
    14) Initial Operator configuration
    15) Image registry storage configuration
    16) Delete the bootstrap resources
    17) Creating the Ingress DNS Records
    18) Logging in to the cluster by using the web console
    19) Telemetry access for OpenShift Container Platform
    20) Deploy an application to test?



SCRIPTS
---------
1) set_baselines.yml: Ansible playbook. Sets the baselines for ocp4 installation.

2) create_stacks.py: Python script which creates the stacks needed for ocp4 setup.


HOW TO USE
------------

Prerequisites
---------------

1) Have your RED HAT & AWS credentials stored in a file i.e creds.yml
** After the first login into AWS, the AWS credentials are saved in ~/.aws/credentials. But you can still save them in the creds.yml file too.**

2) Download all needed artifacts into the ~/Downloads/ directory. This will be the source of truth for the script run.
   - Download installer provisioned infrastructure binary from here : https://console.redhat.com/openshift/install/aws
   - Download the OpenShift client (oc) from here : https://access.redhat.com/downloads/content/290
   - Download the pull_secret from https://console.redhat.com/openshift/install/pull-secret and save it in <your_home>/Downloads directory.
   ** This pull secret allows you to authenticate with the services that are provided by the included authorities, including Quay.io, 
      which serves the container images for OpenShift Container Platform components.



Implementation Steps
--------------------

STEP 1) Run the ansible-script , set_baselines.yml

        $ansible-playbook set_baselines.yml -e "@../../ansible/common/creds.yml"

STEP 2) Run the python-script, create_stacks.py

       $python3 create_stacks.py

STEP 3) Initializing the bootstrap sequence on AWS 

       $ openshift-install wait-for bootstrap-complete --dir <installation_directory> --log-level=info 

STEP 4) Set the environment variable for KUBEADMIN & test the login + health of cluster using 'oc'

       $ export KUBECONFIG=< the install directory name>/auth/kubeconfig

    *** Cannot be set/reset in the same shell session as the script is running.
    *** It won't be registered for the subsequent script actions within the same shell sessions.

    Example:
       $ export KUBECONFIG=<installation_directory>/auth/kubeconfig
       
       $ echo $KUBECONFIG 
       
         ocp4-apse2-07/auth/kubeconfig
         
       $ oc get clusterversion
       
       $ oc get nodes


REFERENCES
------------

https://docs.openshift.com/container-platform/4.10/installing/installing_aws/installing-aws-user-infra.html#installation-generate-aws-user-infra-install-config_installing-aws-user-infra

