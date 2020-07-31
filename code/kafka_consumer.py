from kafka import KafkaConsumer


if __name__ == "__main__":
    # To consume latest messages and auto-commit offsets
    consumer = KafkaConsumer(
        'test_topic',
        group_id='my-group',
        bootstrap_servers=['192.168.169.25:9093', '192.168.169.25:9094',
                           '192.168.169.25:9095']
    )

    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                             message.offset, message.key,
                                             message.value))

    consumer.close()