from qlearning_module.VNF_Placement import VNFPlacement
from son_agent.son_agent import SONAgent
from son_scheduler.son_scheduler import SONScheduler

if __name__ == '__main__':
    son_agent = SONAgent()
    son_agent.get_son_metrics()
    # s = SONScheduler()
    # s.migrate_pod('hello-deployment-65868c5b4b-sfxn7', 'jianqun-239')
