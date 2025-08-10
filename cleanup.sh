docker compose down

docker rmi $(docker images -q) -f

docker volume rm $(docker volume ls -q) -f