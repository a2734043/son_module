import os
import re
import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException


# TODO: pod binding流程
class SONScheduler(object):
    def __init__(self):
        self.kubernetes_client = client
        self.kubeconfig = os.path.expanduser("~/.kube/config")
        config.load_kube_config(config_file=self.kubeconfig)
        kube_config_loader = config.kube_config._get_kube_config_loader_for_yaml_file(self.kubeconfig)
        self.core_v1 = self.kubernetes_client.CoreV1Api()
        self.app_v1 = self.kubernetes_client.AppsV1Api()

    def get_deployment(self):
        deployment_list = list()
        response = self.app_v1.list_namespaced_deployment("default")
        for deployment in response.items:
            deployment_list.append(deployment.metadata.name)
        return deployment_list

    def binding_pod(self, pod_name, node_name):
        target = self.kubernetes_client.V1ObjectReference(kind="Node", name=node_name)
        meta = self.kubernetes_client.V1ObjectMeta(name=pod_name)
        body = self.kubernetes_client.V1Binding(metadata=meta, target=target)

        try:
            ret = self.core_v1.create_namespaced_pod_binding(pod_name, 'default', body, _preload_content=False)
            print(ret)
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_pod_binding: %s\n" % e)

    def get_pending_pod(self):
        ret = self.core_v1.list_namespaced_pod('default')
        pod_list = list()
        for i in ret.items:
            if i.status.phase == "Pending" and i.spec.scheduler_name == "my-scheduler":
                pod_list.append(i.metadata.name)
        return pod_list

    def delete_pod(self, pod_name):
        response = self.core_v1.delete_namespaced_pod(pod_name, 'default')
        print(response)

    def migrate_pod(self, pod_name, node_name):
        self.delete_pod(pod_name)
        time.sleep(1)
        reg_pod_name = pod_name.split('-')
        reg_pod_name.pop()
        reg_pod_name = '-'.join(reg_pod_name)
        pending_pods = self.get_pending_pod()
        print(pending_pods)
        print(reg_pod_name)
        for pending_pod in pending_pods:
            if re.match(reg_pod_name, pending_pod):
                self.binding_pod(pending_pod, node_name)
                break


if __name__ == '__main__':
    son_scheduler = SONScheduler()
    # delete_pod_list = son_scheduler.get_pending_pod()
    # for pod in delete_pod_list:
    #     son_scheduler.delete_pod(pod)
    #     son_scheduler.binding_pod(pod)
    for pod in son_scheduler.get_pending_pod():
        son_scheduler.migrate_pod(pod, 'jianqun-238')
