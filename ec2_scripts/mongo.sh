yum -y install docker
amazon-linux-extras install docker
service docker start
usermod -a -G docker ec2-user
docker run --name wmata_mongo -d mongo:latest

docker run -d --name wmata_mongo \
      -e MONGO_INITDB_ROOT_USERNAME=ks_admin \
      -e MONGO_INITDB_ROOT_PASSWORD=ks_password \
      -p 27017:27017 \
      mongo:latest
