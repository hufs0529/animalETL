FROM docker.elastic.co/logstash/logstash:7.7.1

# Copy the Logstash configuration file and pipeline files into the container
COPY config/logstash.yml /usr/share/logstash/config/
COPY config/logstash.conf /usr/share/logstash/pipeline/

# Set the environment variables
ENV XPACK_MONITORING_ELASTICSEARCH_URL=http://{es-1},{es-2},{es-3}
ENV ELASTICSEARCH_HOST=http://{es-1},{es-2},{es-3}
ENV LS_JAVA_OPTS=-Xms256m-Xmx256m

# Expose the Logstash port
EXPOSE 5044

# Start Logstash
CMD ["logstash", "-f", "/usr/share/logstash/pipeline/logstash.conf"]
