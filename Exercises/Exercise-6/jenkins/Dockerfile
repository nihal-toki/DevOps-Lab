FROM docker:28-cli AS dockercli
FROM jenkins/jenkins:lts-jdk21
USER root
COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
RUN jenkins-plugin-cli --plugins workflow-aggregator pipeline-model-definition timestamper
COPY jenkins/init.groovy /usr/share/jenkins/ref/init.groovy.d/lab.groovy
USER jenkins
