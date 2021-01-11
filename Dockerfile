FROM maven:3-jdk-8-slim

RUN mkdir /usr/src/goof
RUN mkdir /tmp/extracted_files
ADD . /usr/src/goof/
ADD ./start-script.sh /usr/src/goof
WORKDIR /usr/src/goof
RUN chmod u+x start-script.sh
RUN mvn install
RUN apt-get update && apt-get install wget -y

# Add Datadog Java Agent required for profiling
RUN wget -O dd-java-agent.jar 'https://repository.sonatype.org/service/local/artifact/maven/redirect?r=central-proxy&g=com.datadoghq&a=dd-java-agent&v=LATEST'

EXPOSE 8080

CMD /usr/src/goof/start-script.sh

