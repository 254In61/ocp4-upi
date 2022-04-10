> When I use become = yes , I kept getting 
fatal: [localhost]: FAILED! => {"changed": false, "msg": "json and boto/boto3 is required."}
- This could be because script is being run as root and those packages are not installed for root, but for just user, amaseghe.




PENDING??
---------

> Can I create my own install-config.yml through a template??.. And then run it!!??... Avoid the prompts and human aspects thing.
 **If this works, am set!!..he he he.. 
 **But how do I copy the pull-secret thing in an automated way??
> How do I do it on UPI?? After completing IPI.....
> Then I can look at optimization and other things.


LIGHTBULBS!
===========

> Deleting of the stack!
 $ aws cloudformation delete-stack --stack-name ocp4-upi-254-network-stack