#!/bin/bash -e

# Update system
sysctl -w vm.max_map_count=262144
sysctl -w fs.file-max=65536
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
echo "fs.file-max=65536" >> /etc/sysctl.conf

export KAFKA_LOG_DIR="/home/ec2-user/kafkalogs"

# Create a directory for Kafkalogs to be exported to (may be done in Kafka container)
# If missing from Kafka compose - add into volume mapping: - /home/ec2-user/kafkalogs:/opt/kafka/logs
mkdir $KAFKA_LOG_DIR
chmod 777 $KAFKA_LOG_DIR

docker pull docker.elastic.co/elasticsearch/elasticsearch:7.5.1
docker pull docker.elastic.co/kibana/kibana:7.5.1
docker pull docker.elastic.co/beats/filebeat:7.5.1

# Start Elasticsearch
docker run -p 9200:9200 -p 9300:9300 --name "elastic" --ulimit nofile=65536:65536 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.5.1 &

# Start Kibana
docker run --link elastic:elasticsearch -p 5601:5601 --name "kibana" docker.elastic.co/kibana/kibana:7.5.1 &

#Create Kibana dashboards
docker run --name "filebeat" docker.elastic.co/beats/filebeat:7.5.1 setup -E setup.kibana.host=172.31.20.86:5601 -E output.elasticsearch.hosts=["172.31.20.86:9200"] &
sleep 30
docker rm filebeat
sudo docker run --name "filebeat" --volume="filebeat2.docker.yml:/usr/share/filebeat/filebeat.yml" --volume="kafka.yml:/usr/share/filebeat/modules.d/kafka.yml" --volume="/var/lib/docker/containers:/var/lib/docker/containers:ro" --volume="/var/run/docker.sock:/var/run/docker.sock:ro" --volume="$KAFKA_LOG_DIR:/opt/kafka/logs" docker.elastic.co/beats/filebeat:7.5.1 filebeat -e -strict.perms=false   -E setup.kibana.host=172.31.20.86:5601   -E output.elasticsearch.hosts=["172.31.20.86:9200"] &  

