# Real-Time Data Streaming Pipeline

A comprehensive real-time data engineering project that demonstrates streaming data from an external API through Apache Kafka, processing it with Apache Spark, and storing it in Apache Cassandra, all orchestrated by Apache Airflow.

## 📊 Real-Time Data Streaming - Visual Architecture

### 🏗️ High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          REAL-TIME DATA STREAMING PIPELINE                      │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EXTERNAL API  │───▶│    AIRFLOW      │───▶│     KAFKA       │───▶│     SPARK       │
│  Random User    │    │  (Orchestrator) │    │   (Streaming)   │    │  (Processing)   │
│   Generator     │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                 │                        │                        │
                                 ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   POSTGRESQL    │    │   ZOOKEEPER     │    │ CONTROL CENTER  │    │   CASSANDRA     │
│ (Airflow Meta)  │    │ (Coordination)  │    │  (Monitoring)   │    │   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🖥️ Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              WINDOWS HOST MACHINE                               │
│                          c:\Users\hakka\Documents\...                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐                    ┌─────────────────────────────────────┐ │
│  │  LOCAL PYTHON   │                    │           DOCKER COMPOSE            │ │
│  │   ENVIRONMENT   │                    │                                     │ │
│  │                 │                    │  ┌─────────────────┐                │ │
│  │ spark_stream.py │◀──────────────────▶│  │ Spark Master    │                │ │
│  │                 │ spark://localhost: │  │ :7077, :9090    │                │ │
│  │ Virtual Env     │      7077          │  └─────────────────┘                │ │
│  │ C:\hadoop\      │                    │                                     │ │
│  └─────────────────┘                    │  ┌─────────────────┐                │ │
│                                         │  │ Spark Worker    │                │ │
│                                         │  │ :8081           │                │ │
│                                         │  └─────────────────┘                │ │
│                                         │                                     │ │
│                                         │  ┌─────────────────┐                │ │
│                                         │  │ Kafka Broker    │                │ │
│                                         │  │ :9092, :29092   │                │ │
│                                         │  └─────────────────┘                │ │
│                                         │                                     │ │
│                                         │  ┌─────────────────┐                │ │
│                                         │  │ Cassandra       │                │ │
│                                         │  │ :9042           │                │ │
│                                         │  └─────────────────┘                │ │
│                                         │                                     │ │
│                                         │  ┌─────────────────┐                │ │
│                                         │  │ Airflow         │                │ │
│                                         │  │ :8080           │                │ │
│                                         │  └─────────────────┘                │ │
│                                         └─────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 🔄 Data Flow Sequence Diagram

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Random User │   │   Airflow   │   │    Kafka    │   │    Spark    │   │  Cassandra  │
│     API     │   │     DAG     │   │   Broker    │   │  Streaming  │   │  Database   │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │                 │                 │
   ①   │◀────GET────────│                 │                 │                 │
       │                 │                 │                 │                 │
   ②   │─────JSON────────▶│                 │                 │                 │
       │                 │                 │                 │                 │
   ③   │                 │──PRODUCE MSG───▶│                 │                 │
       │                 │                 │                 │                 │
   ④   │                 │                 │◀──CONSUME───────│                 │
       │                 │                 │                 │                 │
   ⑤   │                 │                 │                 │──WRITE BATCH───▶│
       │                 │                 │                 │                 │
   ⑥   │                 │                 │─────ACK────────▶│◀──CONFIRMATION──│
       │                 │                 │                 │                 │
```

## 📊 Data Flow Diagram

This section has been replaced by the comprehensive visual architecture above showing the detailed system interaction and deployment structure.

## 🛠️ Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Orchestration** | Apache Airflow | 2.6.0 | Workflow management and scheduling |
| **Message Broker** | Apache Kafka | 7.4.0 | Real-time data streaming |
| **Stream Processing** | Apache Spark | 3.5.1 | Distributed data processing |
| **Database** | Apache Cassandra | latest | NoSQL database for scalable storage |
| **Coordination** | Apache Zookeeper | 7.4.0 | Kafka cluster coordination |
| **Monitoring** | Confluent Control Center | 7.4.0 | Kafka cluster monitoring |
| **Metadata DB** | PostgreSQL | 14.0 | Airflow metadata storage |
| **Containerization** | Docker Compose | - | Service orchestration |

## 🏛️ Architecture Components

### 1. **Data Ingestion Layer (Apache Airflow)**
- **File**: `dags/kafka_stream.py`
- **Purpose**: Orchestrates the data pipeline
- **Functionality**:
  - Fetches random user data from `randomuser.me` API
  - Formats and structures the data
  - Publishes data to Kafka topic every minute for 1 hour
  - Runs daily as scheduled DAG

### 2. **Message Streaming Layer (Apache Kafka)**
- **Configuration**: `docker-compose.yml`
- **Components**:
  - **Zookeeper**: Manages Kafka cluster coordination
  - **Broker**: Handles message publishing and consumption
  - **Schema Registry**: Manages data schemas
  - **Control Center**: Provides monitoring interface
- **Topic**: `user_created`

### 3. **Stream Processing Layer (Apache Spark)**
- **File**: `spark_stream.py`
- **Architecture**:
  - **Master Node**: Coordinates job execution
  - **Worker Nodes**: Execute distributed processing tasks
- **Functionality**:
  - Connects to Kafka stream
  - Processes real-time data using structured streaming
  - Applies schema validation and transformation
  - Writes processed data to Cassandra

### 4. **Storage Layer (Apache Cassandra)**
- **Purpose**: Persistent storage for processed data
- **Schema**:
  ```sql
  CREATE TABLE user_data.users (
      id UUID PRIMARY KEY,
      first_name TEXT,
      last_name TEXT,
      gender TEXT,
      address TEXT,
      post_code TEXT,
      email TEXT,
      username TEXT,
      dob TEXT,
      registered_date TEXT,
      phone TEXT,
      picture TEXT
  )
  ```

## 🔧 Project Structure

```
RealTimeDataStreaming/
├── docker-compose.yml          # Docker services configuration
├── requirements.txt            # Python dependencies
├── spark_stream.py            # Spark streaming application
├── checkpoints/               # Spark streaming checkpoints
│   └── user_data/
├── dags/                      # Airflow DAGs
│   └── kafka_stream.py        # Data ingestion pipeline
├── script/                    # Setup scripts
│   └── entrypoint.sh         # Airflow initialization script
├── env/                       # Virtual environment
└── hadoop/                    # Hadoop binaries (Windows)
```

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose installed
- Python 3.9+ with virtual environment
- Windows: Hadoop binaries in `C:\hadoop`

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hakkache/Real-Time-Data-Streaming.git
   cd Real-Time-Data-Streaming
   ```

2. **Start the infrastructure**
   ```bash
   docker-compose up -d
   ```

3. **Verify services**
   ```bash
   docker-compose ps
   ```

4. **Set up Python environment**
   ```bash
   python -m venv env
   .\env\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Run Spark streaming**
   ```bash
   python spark_stream.py
   ```

## 🌐 Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| **Airflow Web UI** | http://localhost:8080 | Workflow management |
| **Spark Master UI** | http://localhost:9090 | Spark cluster monitoring |
| **Kafka Control Center** | http://localhost:9021 | Kafka cluster monitoring |
| **Kafka Broker** | localhost:9092 | Kafka client connections |
| **Cassandra** | localhost:9042 | Database connections |

### Default Credentials
- **Airflow**: admin / admin
- **Cassandra**: cassandra / cassandra

## 📈 Monitoring & Observability

### Airflow Monitoring
- Access DAG execution status and logs
- Monitor task dependencies and scheduling
- View data lineage and execution history

### Spark Monitoring
- Track job execution and resource utilization
- Monitor streaming query progress
- View executor status and performance metrics

### Kafka Monitoring
- Monitor topic throughput and consumer lag
- Track broker health and partition distribution
- Observe message flow and processing rates

## 🔍 Data Schema

The pipeline processes user data with the following structure:

```json
{
  "id": "uuid4-string",
  "first_name": "string",
  "last_name": "string", 
  "gender": "string",
  "address": "formatted-address-string",
  "post_code": "string",
  "email": "email-string",
  "username": "string",
  "dob": "iso-datetime-string",
  "registered_date": "iso-datetime-string", 
  "phone": "string",
  "picture": "url-string"
}
```

## 🔧 Configuration Details

### Spark Configuration
- **Master URL**: `spark://localhost:7077`
- **Executor Memory**: 1GB per executor
- **Executor Cores**: 2 cores per executor
- **Checkpoint Location**: `./checkpoints/user_data`

### Kafka Configuration
- **Bootstrap Servers**: `broker:29092`
- **Topic**: `user_created`
- **Starting Offset**: `earliest`
- **Processing Trigger**: Every 10 seconds

### Cassandra Configuration
- **Keyspace**: `user_data`
- **Replication**: SimpleStrategy with factor 1
- **Table**: `users` with UUID primary key

## 🚨 Troubleshooting

### Common Issues

1. **Spark Connection Issues**
   - Ensure Docker containers are running
   - Check Spark master UI at http://localhost:9090
   - Verify network connectivity between components

2. **Kafka Connection Issues**
   - Check broker health: `docker logs broker`
   - Verify topic creation in Control Center
   - Ensure Zookeeper is healthy

3. **Cassandra Connection Issues**
   - Check container logs: `docker logs cassandra`
   - Verify port 9042 accessibility
   - Ensure keyspace and table creation

## 🎯 Performance Considerations

- **Batch Size**: Spark processes data in 10-second intervals
- **Parallelism**: 2 Spark workers with 2 cores each
- **Checkpointing**: Enabled for fault tolerance
- **Memory**: 1GB allocated per Spark executor

## 🔮 Future Enhancements

- [ ] Add data validation and quality checks
- [ ] Implement real-time dashboards with Grafana
- [ ] Add machine learning pipelines
- [ ] Integrate with cloud services (AWS, Azure, GCP)
- [ ] Add data partitioning strategies
- [ ] Implement schema evolution support

## 🏗️ Deployment Architecture

### Development Environment
- Local Docker containers
- Windows-based Spark driver
- Local file system checkpoints

### Production Considerations
- Distributed Spark cluster
- Kafka cluster with multiple brokers
- Cassandra cluster with replication
- Monitoring and alerting systems

## 📚 Learning Resources

This project demonstrates key concepts in:
- Real-time data streaming
- Event-driven architecture
- Microservices with Docker
- Big data processing with Spark
- NoSQL database design
- Workflow orchestration

---

## 🙏 Acknowledgments

**Special thanks to [CodeWithYu](https://www.youtube.com/@CodeWithYu) for the excellent tutorial that inspired this project!**

📺 **Tutorial Video**: [Real-Time Data Streaming | End-to-End Data Engineering Project](https://www.youtube.com/watch?v=GqAcTrqKcrY&t=4890s)

This implementation is based on the comprehensive data engineering tutorial by CodeWithYu, which provides excellent insights into building production-ready real-time streaming pipelines.

---

## 📄 License

This project is for educational purposes and follows the tutorial structure provided by CodeWithYu.