import json
from time import time
from kafka import KafkaConsumer
from qlearning_module.VNF_Placement import VNFPlacement


class SONAgent(object):

    def __init__(self, *args, **kwargs):
        pass

    def get_son_metrics(self):
        consumer = KafkaConsumer('pm_job', bootstrap_servers=['10.0.1.241:9092'])
        for msg in consumer:
            print('====================================')
            a = msg.value.decode('utf-8')
            a = json.loads(a)
            node_resource = a['node']['10.0.1.241']
            nodes = a['node']
            node_list = list(nodes.keys())
            node_resource_list = list(nodes.values())

            vnf_resource = a['pod']

            node_resource = {
                'cpu': 8,
                'mem': 16000,
                'BW': 1000
            }
            vnf_placement = VNFPlacement(vnf_resource_dict=vnf_resource, number_of_node=1, limit_W=node_resource, nodes=nodes)
            train_start_time = time()
            Q = vnf_placement.q_learning(num_episodes=1000, discount_factor=0.9, alpha=0.3, epsilon=0.25)
            train_finish_time = time()
            print("==============training time==========")
            print(train_finish_time - train_start_time)
            print("==============Q table================")
            print(vnf_placement.limit_W)
            print(vnf_placement.resource_list)
            print(Q)

            get_result_start_time = time()
            vnf_placement_result = vnf_placement.get_vnf_placement()
            get_result_finish_time = time()
            print("==============result time==========")
            print(get_result_finish_time - get_result_start_time)
            print("==============result==========")
            print(vnf_placement_result)

            print('++++++++++++++++++++++++++++++++++++')


if __name__ == '__main__':
    son_agent = SONAgent()
    son_agent.get_son_metrics()
