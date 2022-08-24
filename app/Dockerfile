FROM public.ecr.aws/ews-network/amazoncorretto:8

LABEL maintainer="jeff.fry@lacework.net"

COPY target/spring-petclinic-2.0.0.BUILD-SNAPSHOT.jar /home/spring-petclinic-2.0.0.BUILD-SNAPSHOT.jar

CMD ["java","-jar","/home/spring-petclinic-2.0.0.BUILD-SNAPSHOT.jar"]
