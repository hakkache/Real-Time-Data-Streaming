import logging
import os
from datetime import datetime
from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType
import os


import os

# Hadoop for Windows fix
os.environ['HADOOP_HOME'] = r"C:\hadoop"
os.environ['PATH'] += os.pathsep + r"C:\hadoop\bin"

# Ensure checkpoints folder exists
os.makedirs(r"C:\TempSpark\checkpoints\user_data", exist_ok=True)
venv_python = os.path.join(os.getenv("VIRTUAL_ENV"), "Scripts", "python.exe")
os.environ["PYSPARK_PYTHON"] = venv_python
os.environ["PYSPARK_DRIVER_PYTHON"] = venv_python

# Optional: change working dir to avoid spaces
os.chdir("C:\\TempSpark")  # create this folder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_keyspace(session):
    session.execute("""CREATE KEYSPACE IF NOT EXISTS user_data  
                       WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };""")
    logging.info("Keyspace created successfully")   

def create_table(session):
    session.execute("""CREATE TABLE IF NOT EXISTS user_data.users (
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
                        picture TEXT)""")
    logging.info("Table created successfully")

def create_spark_connection():
    """
    Creates a Spark connection that submits jobs to the Spark cluster running in Docker.
    The script runs locally on Windows but connects to spark://localhost:7077
    """
    s_conn = None
    try:
        logging.info("Connecting to Spark cluster at localhost:7077...")
        
        s_conn = SparkSession.builder \
            .appName('SparkDataStreaming') \
            .master("spark://localhost:7077") \
            .config("spark.jars.packages",
                    "com.datastax.spark:spark-cassandra-connector_2.12:3.5.1,"
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
            .config('spark.cassandra.connection.host', 'host.docker.internal') \
            .config('spark.cassandra.connection.port', '9042') \
            .config('spark.sql.extensions', 'com.datastax.spark.connector.CassandraSparkExtensions') \
            .config('spark.sql.streaming.checkpointLocation', './checkpoints') \
            .config('spark.submit.deployMode', 'client') \
            .config('spark.driver.host', 'host.docker.internal') \
            .config('spark.driver.bindAddress', '0.0.0.0') \
            .config('spark.executor.memory', '1g') \
            .config('spark.executor.cores', '2') \
            .getOrCreate()
        
        s_conn.sparkContext.setLogLevel("ERROR")
        logging.info("✓ Spark connection created successfully")
        logging.info(f"✓ Spark Master UI: http://localhost:9090")
        executor_status = s_conn.sparkContext._jsc.sc().getExecutorMemoryStatus()
        executor_count = executor_status.size()
        logging.info(f"✓ Connected to Spark cluster with {executor_count} executors")

    except Exception as e:
        logging.error(f"✗ Error creating Spark connection: {e}")
        logging.error("Make sure Spark cluster is running: docker-compose ps")
        raise
    
    return s_conn      

def connect_to_kafka(s_conn):
    spark_df = None
    try:
        logging.info("Connecting to Kafka at localhost:9092...")
        spark_df = s_conn.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "broker:29092") \
            .option("subscribe", "user_created") \
            .option("startingOffsets", "earliest") \
            .option("failOnDataLoss", "false") \
            .load()
        logging.info("✓ Connected to Kafka topic 'user_created' successfully")       

    except Exception as e:
        logging.error(f"✗ Error connecting to Kafka topic: {e}")
        raise
    
    return spark_df

def create_cassandra_connection():
    try:
        logging.info("Connecting to Cassandra at localhost:9042...")
        cluster = Cluster(['localhost'], port=9042)
        cas_session = cluster.connect() 
        logging.info("✓ Cassandra connection created successfully")
        return cas_session
    
    except Exception as e:
        logging.error(f"✗ Error creating Cassandra connection: {e}")
        logging.error("Make sure Cassandra is running: docker logs cassandra")
        return None
    
def create_selection_df_from_kafka(spark_df):
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("address", StringType(), True),
        StructField("post_code", StringType(), True),
        StructField("email", StringType(), True),
        StructField("username", StringType(), True),
        StructField("dob", StringType(), True),
        StructField("registered_date", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("picture", StringType(), True)
    ])
    
    selection_df = spark_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")
    
    logging.info("✓ Selection DataFrame created from Kafka stream")
    return selection_df

   
if __name__ == "__main__":
    print("="*70)
    print("  Spark Streaming Application - Kafka to Cassandra")
    print("="*70)
    logging.info("Starting Spark Streaming Application...")
    logging.info("This script runs locally but connects to Spark cluster in Docker")
    print()
    
    # Create Spark connection to the cluster
    spark_conn = create_spark_connection()
    
    if spark_conn is not None:
        # Connect to Kafka
        spark_df = connect_to_kafka(spark_conn)
        
        # Create selection DataFrame
        selection_df = create_selection_df_from_kafka(spark_df)
        
        # Create Cassandra connection and setup
        session = create_cassandra_connection()
        
        if session is not None:
            create_keyspace(session)
            create_table(session)
            
            print()
            logging.info("="*70)
            logging.info("Starting streaming query...")
            logging.info("Jobs will be distributed across Spark workers in Docker")
            logging.info("Monitor progress at: http://localhost:9090")
            logging.info("="*70)
            print()
            
            # Write stream to Cassandra
            streaming_query = (selection_df.writeStream
                .format("org.apache.spark.sql.cassandra") 
                .option("checkpointLocation", "./checkpoints/user_data")
                .option("keyspace", "user_data") 
                .option("table", "users")
                .trigger(processingTime='10 seconds') 
                .start())
            
            logging.info("✓ Streaming query started successfully!")
            logging.info("✓ Waiting for data from Kafka topic 'user_created'...")
            logging.info("Press Ctrl+C to stop the application")
            print()
            
            # Wait for termination
            streaming_query.awaitTermination()