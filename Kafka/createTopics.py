from kafka import KafkaAdminClient
from kafka.admin import NewTopic


def main():
    admin = KafkaAdminClient(bootstrap_servers='localhost:9092')

    topic_ff = NewTopic(name='seg_firefox', num_partitions=1, replication_factor=1)
    topic_wn = NewTopic(name='seg_windows', num_partitions=1, replication_factor=1)
    topic_ph = NewTopic(name='seg_iphone', num_partitions=1, replication_factor=1)

    admin.create_topics([topic_ff, topic_wn, topic_ph])

if __name__ == "__main__":
    main()
