#!/bin/bash
wget -O dd-java-agent.jar https://dtdg.co/latest-java-tracer
source ./mvn_opts.sh
/usr/bin/mvn tomcat7:run
