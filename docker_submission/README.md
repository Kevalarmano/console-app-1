# Task Manager – Console App (Dockerised)

A fully interactive, file-backed task manager built in Python and containerised with Docker.

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running

## Build the image locally
```bash
docker build -t kevalarmano/console-app .
```

## Run the container
The app requires interactive terminal input, so always use the `-it` flags:
```bash
docker run -it kevalarmano/console-app
```

## Pull and run directly from Docker Hub
```bash
docker run -it kevalarmano/console-app
```

## Default login
- Username: `admin`
- Password: `password`

## Features
- Login / register users
- Add tasks assigned to any user
- View all tasks or only your own
- Mark tasks as complete or edit due dates

## Files
| File | Purpose |
|---|---|
| `task_manager.py` | Main application |
| `Dockerfile` | Container build instructions |
| `docker1.txt` | Docker Hub repository link |
| `user.txt` | User credentials (seeded with admin) |
| `tasks.txt` | Task data store |
