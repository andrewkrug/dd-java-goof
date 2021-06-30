export MAVEN_OPTS="-javaagent:dd-java-agent.jar -Ddd.profiling.enabled=true -XX:FlightRecorderOptions=stackdepth=256 -Ddd.service=javagoof -Ddd.env=lab -Ddd.version=.01"
