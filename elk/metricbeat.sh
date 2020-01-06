#!/bin/bash -e

# Assumes filebeat was run first
docker pull docker.elastic.co/beats/metricbeat:7.5.1

# Change permissions on Kafka
# /opt/kafka/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=172.31.20.86:2181 --add --allow-principal User:'*' --operation Read --topic '*'
# /opt/kafka/bin/kafka-acls.sh --authorizer-properties zookeeper.connect=172.31.20.86:2181 --add --allow-principal User:'*' --operation Describe --group '*'

docker run --name "metricbeat" docker.elastic.co/beats/metricbeat:7.5.1 setup -E setup.kibana.host=172.31.20.86:5601 -E output.elasticsearch.hosts=["172.31.20.86:9200"] &
sleep 30
docker rm metricbeat
docker run --name "metricbeat" --volume="metricbeat.docker.yml:/usr/share/metricbeat/metricbeat.yml" --volume="metricbeat.kafka.yml:/usr/share/metricbeat/modules.d/kafka.yml" --volume="/var/lib/docker/containers:/var/lib/docker/containers:ro" --volume="/var/run/docker.sock:/var/run/docker.sock:ro" docker.elastic.co/beats/metricbeat:7.5.1 metricbeat -e -strict.perms=false   -E setup.kibana.host=172.31.20.86:5601   -E output.elasticsearch.hosts=["172.31.20.86:9200"] &  

