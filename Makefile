all:
	sudo docker compose up -d 

debug: 
	sudo docker compose up --build

stop: 
	sudo docker compose down