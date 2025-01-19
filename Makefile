# Makefile

# Default target
.PHONY: start stop clean help

start:
	docker compose up --build

stop:
	docker compose down

clean:
	docker compose down -v

help:
	@echo "Available commands:"
	@echo "  start   - Build and start the Docker Compose services"
	@echo "  stop    - Stop the Docker Compose services"
	@echo "  clean   - Stop and remove the services, including volumes"