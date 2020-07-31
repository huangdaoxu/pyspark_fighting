from kafka import KafkaProducer
from kafka.errors import KafkaError


if __name__ == "__main__":
    producer = KafkaProducer(
        bootstrap_servers=['192.168.169.25:9093', '192.168.169.25:9094',
                           '192.168.169.25:9095']
    )

    for _ in range(0, 300000, 1):
        future = producer.send("test_topic", b'hello world!!!')
        # try:
        #     record_metadata = future.get(timeout=10)
        #     # Successful result returns assigned partition and offset
        #     print(record_metadata.topic)
        #     print(record_metadata.partition)
        #     print(record_metadata.offset)
        # except KafkaError as e:
        #     print(e)

    for _ in range(0, 30, 1):
        future = producer.send("test_topic", b'{"cmd": "mysql -uroot -h10.30.0.25 -P3006 -pqwe123456"}')
        # try:
        #     record_metadata = future.get(timeout=10)
        #     # Successful result returns assigned partition and offset
        #     print(record_metadata.topic)
        #     print(record_metadata.partition)
        #     print(record_metadata.offset)
        # except KafkaError as e:
        #     print(e)

    producer.flush()
    producer.close()
