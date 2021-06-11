from kafka import KafkaConsumer

class SONAgent(object):

    def __init__(self, *args, **kwargs):
        pass

    def get_son_metrics(self):
        consumer = KafkaConsumer('pm_job', bootstrap_servers= ['10.0.1.241:9092'])
        for msg in consumer:
            print('====================================')
            print(type(msg.value))
            a = msg.value.decode('utf-8')
            print(type(a))
            print(a)
            print('====================================')


if __name__ == '__main__':
    son_agent = SONAgent()
    son_agent.get_son_metrics()