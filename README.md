# RabbitMQ + Docker

## Microservices Overview

This project showcases a microservice architecture using Python, RabbitMQ, and Docker. It consists of four main services that work together to process data, make predictions, log metrics, and generate visualizations.

## Components

1. **RabbitMQ**: Acts as the message broker facilitating communication between services.
2. **Features Service**: Generates and sends feature data and true labels to RabbitMQ queues.
3. **Model Service**: Consumes feature data, makes predictions using a pre-trained model, and sends predictions to RabbitMQ.
4. **Metric Service**: Consumes true labels and predictions, calculates metrics, and logs them to a CSV file.
5. **Plot Service**: Reads the metrics log and generates visualizations.

## Structure

```
microservice_architecture/
├── docker-compose.yml
├── features/
│   ├── src/
│   │   └── features.py
│   ├── Dockerfile
│   └── requirements.txt
├── model/
│   ├── src/
│   │   ├── model.py
│   │   └── myfile.pkl
│   ├── Dockerfile
│   └── requirements.txt
├── metric/
│   ├── src/
│   │   └── metric.py
│   ├── Dockerfile
│   └── requirements.txt
├── plot/
│   ├── src/
│   │   └── plot.py
│   ├── Dockerfile
│   └── requirements.txt
└── logs/
    ├── metric_log.csv
    └── error_distribution.png
```

## Running the Project

   Use Docker Compose to build the Docker images and start all services:

   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build Docker images for each service.
   - Start RabbitMQ with management UI accessible at `http://localhost:15672` (Username: `guest`, Password: `guest`).
   - Launch all microservices and establish communication via RabbitMQ.

## Logs & Plots

- **Metrics Log**: `logs/metric_log.csv`
- **Error Distribution Plot**: `logs/error_distribution.png`

These files are stored in the `logs` directory, which is mounted as a Docker volume to ensure data persistence.

## Stopping the Services

To stop all running services, press `CTRL+C` in the terminal where Docker Compose is running, or run:

```bash
docker-compose down
```

This command will stop and remove all containers defined in the `docker-compose.yml`.

