import json
from time import time, sleep
from kafka import KafkaConsumer
from qlearning_module.VNF_Placement import VNFPlacement
from son_scheduler.son_scheduler import SONScheduler


class SONAgent(object):

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def node_ip_to_name(ip):
        number = ip.split('.')[-1]
        return "jianqun-{number}".format(number=number)

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
            vnf_placement = VNFPlacement(vnf_resource_dict=vnf_resource,
                                         number_of_node=len(nodes),
                                         limit_W=node_resource,
                                         nodes=nodes)
            train_start_time = time()
            Q = vnf_placement.q_learning(num_episodes=1000, discount_factor=0.9, alpha=0.5, epsilon=0.01)
            train_finish_time = time()
            print("==============training time==========")
            print(train_finish_time - train_start_time)
            print("==============Q table================")
            print(vnf_placement.limit_W)
            print(vnf_placement.resource_list)
            print(Q)

            get_result_start_time = time()
            optimal_stat, vnf_list, current_stat, node_name_list = vnf_placement.get_vnf_placement()
            get_result_finish_time = time()
            print("==============result time==========")
            print(get_result_finish_time - get_result_start_time)
            print("==============result==========")
            print(optimal_stat, vnf_list, current_stat, node_name_list)

            print('++++++++++++++++++++++++++++++++++++')

            optimal_vnf_list = dict()
            for key, node in enumerate(optimal_stat):
                for pod in node:
                    optimal_vnf_list[vnf_list[pod][0]] = node_name_list[key]
            print(optimal_vnf_list)

            son_scheduler = SONScheduler()
            for vnf in vnf_list:
                pod_name, location = vnf
                optimal_location = optimal_vnf_list.get(pod_name)
                if optimal_location != location:
                    print("{pod} is in {location} need to migrate to {optimal}".format(pod=pod_name,
                                                                                       location=location,
                                                                                       optimal=optimal_location))
                    if location == 'pending':
                        son_scheduler.binding_pod(pod_name, self.node_ip_to_name(optimal_location))
                    else:
                        son_scheduler.migrate_pod(pod_name, self.node_ip_to_name(optimal_location))
                # # son_scheduler.migrate_pod(pod_name, 'jianqun-238')
                # sleep(5)


if __name__ == '__main__':
    son_agent = SONAgent()
    son_agent.get_son_metrics()
