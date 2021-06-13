import os
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

    def binding_pod(self, delete_pod_list, target_node_list, namespace, target_node):
        target = self.kubernetes_client.V1ObjectReference(kind="Node", name="jianqun-238")
        meta = self.kubernetes_client.V1ObjectMeta(name=pod_name)
        body = self.kubernetes_client.V1Binding(metadata=meta, target=target)

        try:
            ret = self.core_v1.create_namespaced_pod_binding(pod_name, namespace, body, _preload_content=False)
            print(ret)
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_pod_binding: %s\n" % e)

    def get_pending_pod(self, namespace):
        ret = self.core_v1.list_namespaced_pod(namespace)
        for i in ret.items:
            print(i.status.phase)
            print(i.spec.scheduler_name)
            if i.status.phase == "Pending" and i.spec.scheduler_name == "my-scheduler":
                print("123")
                return i.metadata.name
        return None

    def delete_pod_list(self, delete_pod_list):
        for pod_name in delete_pod_list:
            self.core_v1.delete_namespaced_pod(pod_name, 'default')
