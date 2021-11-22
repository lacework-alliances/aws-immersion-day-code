# Demo App

[![CIS](https://app.soluble.cloud/api/v1/public/badges/025cc02c-25bf-4011-8a8e-416ac05a700a.svg)](https://app.soluble.cloud/repos/details/github.com/jefferyfry/lacework-aws-immersion-day-app-pipeline)  [![IaC](https://app.soluble.cloud/api/v1/public/badges/79ea6b5e-8acb-487a-9a14-59e059aef0e1.svg)](https://app.soluble.cloud/repos/details/github.com/jefferyfry/lacework-aws-immersion-day-app-pipeline)  

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 10.1.7.

![demo-app](https://drive.google.com/uc?export=view&id=1GBfyMHdmEh1QgJmmPSOEzMvz5d6921Cq)

## Build and Run Docker Image Locally

```
$ docker build -t demo-app . 
$ docker run -p 443:443 -p 80:80 docker.io/library/demo-app
```

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).
