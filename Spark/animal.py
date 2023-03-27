# hdfs 디렉토릴 만들기
hdfs dfs -mkdir /animal

#hdfs에 csv 전송
hdfs dfs -put animal_data_img.csv /animal

# hdfs에 img directory 전송
hdfs dfs -put ./animal_images /animal

# hdfs 디렉토리 확인
hdfs dfs -ls /animal
 hdfs dfs -ls /animal/animal_images/animal_images



%spark.pyspark
from pyspark.sql.functions import col, split, concat_ws
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("ReadAnimalData").getOrCreate()

# 파일 url 변수
csv_file_path = "hdfs:///animal/animal_data_img.csv"
img_file_path =  "hdfs:///animal/animal_images/"

# csv 읽기
df_csv = spark.read.csv(csv_file_path, header=True, inferSchema=True)
df_csv = spark.read.format("csv").option("header", "true").load(csv_file_path)

# 데이터 프레임 변환
df_df_csv = spark.read.csv(img_file_path, header=True, inferSchema=True)
df_img = spark.read.format("binaryFile").option("header", "true").load(img_file_path)

# 조건에 해당하는 열에서 숫자만 추출하여 ImageFile 열 생성 
df_csv = df_csv.withColumn("ImageNumber", regexp_extract(df_csv["Image_File"], "\d+", 0))
df_img = df_img.withColumn("ImageNumber", regexp_extract(df_img["path"], "\d+", 0))

# join을 통해서 해당 열이 같으면 합병
df_combined = df_img.join(df_csv, df_img.ImageNumber == df_csv.ImageNumber, "inner")

# filter을 통해서 부적절한 행 제거
df_filtered = df_combined.filter(regexp_replace(col("Label"), "[^a-zA-Z0-9]+", "") != "")

# drop을 통해서 필요없는 열 제거
df = df_filtered.drop("modificationTime", "length", "content", "ImageNumber")

# hdfs에 csv형태로 저장
df.coalesce(1).write.format("com.databricks.spark.csv").option("header", "true").option("delimiter", ",").option("encoding", "UTF-8").mode("overwrite").save("/animal/animal.csv")

# hdfs에 저장된 csv파일 확인
hadoop fs -cat /animal/animal.csv/part-00000-74d463dc-cbe6-4c99-b289-0fb7af8f7322-c000.snappy.parquet

# 저장된 csv DataFrame으로 출력해보기
df_sample = spark.read.format("csv").option("header", "true").load("hdfs:///animal/animal.csv/part-00000-8c09b123-132d-4487-8a60-0ae07b5fb019-c000.csv")
df_sample.show()

# Spark에서 Kafka로 전송
from kafka import KafkaProducer
import json

df_json = df.toJSON()
producer = KafkaProducer(bootstrap_servers=['3.38.135.170:9092'],
                         value_serializer=lambda m: json.dumps(m).encode('ascii'))

for data in df_json:
    producer.send('animal', data)



docker run -d --name logstash \
  -p 5044:5044 \
  -v /path/to/logstash/config:/usr/share/logstash/config \
  -v /path/to/logstash/pipeline:/usr/share/logstash/pipeline \
  docker.elastic.co/logstash/logstash:7.7.1


/home/ubuntu/part-00000-8c09b123-132d-4487-8a60-0ae07b5fb019-c000.csv