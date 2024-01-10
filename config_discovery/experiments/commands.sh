#############################################
# Prerequisites
#############################################
yum install docker
systemctl restart docker


#############################################
# docker image
#############################################
docker login -u amagidevops -p beefed0108
docker pull amagidevops/tardis:fr_0.16.4_switcher_imitext_v1
docker images


#############################################
# Manual trigger
#############################################

############
# docker run
############
#docker run --name tt1 --net host --privileged -v $PWD/amagi.env:/etc/amagi_env/amagi.env -v $PWD/tardis.cfg:/home/root/configs/config.ini --entrypoint /lib/systemd/systemd -d amagidevops/tardis:fr_0.16.4_switcher_imitext_v1
docker run --name tt1 --net host --privileged -v $PWD/tardis.cfg:/home/root/configs/config.ini --entrypoint /lib/systemd/systemd -d amagidevops/tardis:fr_0.16.4_switcher_imitext_v1

#############
# docker exec
#############
docker exec -it tt1 /bin/bash


#############################################
# Service discovery trigger
#############################################

############
# docker run
############
docker run --name tt1 --net host --privileged -v $PWD/../config_discovery:/mnt/config_discovery -e ORKY_MODE=K8S -e CONFIG_KEY=tardis --entrypoint /lib/systemd/systemd -d amagidevops/tardis:fr_0.16.4_switcher_imitext_v1

#############
# docker exec
#############
docker exec -it tt1 /bin/bash

#########
# install
#########
pip install -r /mnt/config_discovery/dependencies/configFileStoreClient/requirements.txt

#############################################
# update startup application
#############################################
# STEP 1: Edit /usr/local/amagi/scripts/entrypoint.sh
(
mkdir -p /home/root/configs
export $(cat /proc/1/environ | xargs --null echo)
python3 /mnt/config_discovery/discoverConfigs.py
)

#############################################
# start application
#############################################
systemctl restart amagi_init.service

