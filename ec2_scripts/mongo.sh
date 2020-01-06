# Install Docker
yum -y install docker
amazon-linux-extras install docker
service docker start

# Setup docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Run mongo instance    
usermod -a -G docker ec2-user
docker run --name wmata_mongo -d mongo:latest

docker run -d --name wmata_mongo \
      -e MONGO_INITDB_ROOT_USERNAME=ks_admin \
      -e MONGO_INITDB_ROOT_PASSWORD=ks_password \
      -p 27017:27017 \
      mongo:latest
