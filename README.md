# AWS Immersion Day with Lacework Application and Infrastructure Code

This repository contains the application and infrastructure code for [AWS Immersion Day with Lacework](https://lacework-alliances.github.io/aws-immersion-day-with-lacework/). The application and infrastructure code support the following instruction modules.

* Advanced Cloud Security Posture Management (CSPM+)
* Vulnerability & Workload Protection (DevSecOps) with CodePipeline, CodeBuild, ECR & EKS
* Vulnerability & Workload Protection (DevSecOps) with CodePipeline, CodeBuild, ECR & ECS
* SIEM: AWS Security Hub and Lacework
* Seamless Multi-Account Security: Lacework with AWS Control Tower

## Demo Application Code

Some of the instruction modules use an NPM demo app. The application code is located in the app directory.

### Build and Run Docker Image Locally

```
$ cd app
$ aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
$ docker build -t demo-app . 
$ docker run -p 443:443 -p 80:80 docker.io/library/demo-app
```

### Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

### Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

### Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

### Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

### Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

### Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).

## CloudFormation Infrastructure Code

The AWS infrastructure that is required for the instruction modules are provision using CloudFormation templates that are located in the templates directory. A resources.py Lambda function is used in for resource cleanup and is located in the functions directory. K8s manifests for EKS are located in the manifests directory.

### CloudFormation Templates

#### Master Template

* setup-master.template.yml - This is the master template that initiates the infrastructure provisioning.

#### Nested Templates

* setup-bastion-eks.template.yml - Creates the bastion host, the EKS cluster, installs the Lacework Agent for EKS, creates agent tokens in Lacework, sets up ECR scanning with Lacework and sets up inline scanning with Lacework.
* setup-ecs.template.yml - Creates an ECS cluster, service and task definition. Sets up the Lacework sidecar agent.
* setup-lambdas.template.yml - Creates the ResourcesFunction Lambda to assist in resources cleanup.
* setup-pipelines.template.yml - Creates the CodePipeline pipelines for EKS and EKS. Creates the CodeBuild projects for building and deploying the demo app. Creates the ECR and S3 resources.
* setup-vpc.template.yml - Creates the main VPC for all the infrastructure.


### Deploy the Infrastructure

Use the following CloudFormation Launch button to launch the master template in your CloudFormation console. The following CloudFormation parameters are required.

* LaceworkAccountName - Your Lacework account name. ie. <account name>.lacework.net.
* LaceworkAccessKeyID - Lacework API Access Key ID contains alphanumeric characters and symbols only.
* LaceworkSecretKey - Lacework API Secret Key contains alphanumeric characters and symbols only.
* KeyName - The EC2 Key Pair to allow SSH access to the bastion host.

To generate a Lacework API Access Key/Secret, navigate to **Settings > API Keys** in the Lacework console. Click **+ Create New**. Enter a name for the key and an optional description and click **Save**. To get the secret key, download the generated API key file and open it in an editor.

The CloudFormation deployment process will take 30-60 minutes.
<a href="https://console.aws.amazon.com/cloudformation/home?#/stacks/create/review?templateURL=https://lacework-alliances.s3.us-west-2.amazonaws.com/awsimmersionday/templates/setup-master.template.yml"><img src="https://dmhnzl5mp9mj6.cloudfront.net/application-management_awsblog/images/cloudformation-launch-stack.png"></img></a>
