import json

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from kafka import KafkaProducer
from kafka.errors import KafkaError


def minEditDistance(word1, word2):
    if not word1:
        return len(word2 or '') or 0

    if not word2:
        return len(word1 or '') or 0

    size1 = len(word1)
    size2 = len(word2)

    last = 0
    tmp = [i for i in range(size2 + 1)]
    value = None

    for i in range(size1):
        tmp[0] = i + 1
        last = i
        for j in range(size2):
            if word1[i] == word2[j]:
                value = last
            else:
                value = 1 + min(last, tmp[j], tmp[j + 1])
            last = tmp[j+1]
            tmp[j+1] = value
    return value


def extractPasswd(cmd):
    cmd_list = cmd.split()
    for cmd in cmd_list:
        if cmd.startswith("-p"):
            cmd = cmd.replace("-p", "")
            if len(cmd) <= 0:
                return None
            else:
                return cmd.strip("\"\'")
    return None


weak_passwd_list = ["123456"]
def minDistance(passwd):
    distances = []
    for i in weak_passwd_list:
        distances.append(minEditDistance(i, passwd))
    return min(distances)


def updateDict(d, key, value):
    d[key] = value
    return d


def transformKafkaData(data):
    try:
        return json.loads(data)
    except:
        return None


def upload2Kafka(data):
    brokers = '192.168.169.25:9093,192.168.169.25:9094,192.168.169.25:9095'
    topic = 'test_topic'
    producer = KafkaProducer(bootstrap_servers=brokers)
    future = producer.send(topic, json.dumps(data).encode("utf-8"))
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


if __name__ == "__main__":
    sc = SparkContext(appName="streamingKafka", master="local[4]")
    sc.setLogLevel("warn")
    ssc = StreamingContext(sc, 10)
    brokers = '192.168.169.25:9093,192.168.169.25:9094,192.168.169.25:9095'
    topic = 'test_topic'

    kafka_streaming_rdd = KafkaUtils.createDirectStream(ssc, [topic], {'metadata.broker.list': brokers})
    lines_rdd = kafka_streaming_rdd.map(lambda x: transformKafkaData(x[1]))
    lines_filter = lines_rdd.filter(lambda x: type(x) == dict)
    lines_filter = lines_filter.filter(lambda x: ('cmd' in x.keys()) and ('-p' in x['cmd']) and ('mysql' == x['cmd'].split()[0]))
    lines_filter = lines_filter.map(lambda x: updateDict(x, "password", extractPasswd(x['cmd'])))
    lines_filter = lines_filter.filter(lambda x: x['password'] is not None)
    lines_filter = lines_filter.map(lambda x: updateDict(x, "distance", minDistance(x['password'])))
    lines_filter = lines_filter.filter(lambda x: x['distance'] < 5)
    lines_filter = lines_filter.map(lambda x: x['password'])
    lines_filter.foreachRDD(lambda x: x.foreach(upload2Kafka))
    lines_filter.pprint()
    ssc.start()
    ssc.awaitTermination()
