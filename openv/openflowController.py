import logging
import requests
import json

class OpenFlowController():


    def __init__(self,url):
        self._url_ = url

    def _getDPIDs(self):
        dpids = requests.get(self._url_+"/stats/switches").json()
        return dpids

    def getListOfSwitches(self):
        """Get a list with all descriptions of connected switches
        :return: a list containing description in json dict.
        :ref: https://ryu.readthedocs.io/en/latest/app/ofctl_rest.html#get-the-desc-stats
        """
        dpids = self._getDPIDs()
        listOfSwitches = list()
        for i in dpids:
            desc = requests.get(self._url_+"/stats/desc/"+str(i)).json()
            listOfSwitches.append(desc)
        return listOfSwitches

    def deleteAllFlowRules(self, dpid=None):
        """Delete all flow rules from switch with a give datapath, default deletes all rules on all switches.
        :param dpid: datapath id, identifying switch, defaults to None
        :type dpid: int, optional
        """
        if dpid == None:
            dpids = self._getDPIDs()
            print(dpids)
            for dp in dpids:
                self.deleteAllFlowRules(dpid = dp)
        else:
            print(dpid)
            requests.delete(self._url_+"/stats/flowentry/clear/"+str(dpid))

    def addFlowRule(self, rule):
        logging.info("ADD FLOW RULE " + json.dumps(rule))
        requests.post(self._url_+"/stats/flowentry/add",data=json.dumps(rule))

    def getPathID(self, producer, serial):
        los = self.getListOfSwitches()
        for entry in los:
            for key in entry:
                if (entry[key]["mfr_desc"] == producer) and (entry[key]["serial_num"] == serial):
                    return key
        return -1

    def deployConfig(self, dpid, config):
        logging.info("DPID " + str(dpid))
        for entry in config:
            entry["dpid"] = dpid
            entry["priority"] = 11111
            entry["table_id"] = 0
            entry["idle_timeout"] = 3600
            entry["hard_timeout"] = 3600
            entry["flags"] = 1
            print(entry)
            self.addFlowRule(entry)

    def deployJSONConfiguration(self, jsonConfig):
        self.deleteAllFlowRules()
        for entry in jsonConfig:
            if entry["ovs_sw_active"]:
                
                dpid = entry["ovs_sw_data"]["dpid"]
                if dpid == -1:
                    logging.error("can't find switch with dpid: "+entry["ovs_sw_data"]["dpid"])
                else:
                    self.deployConfig(dpid,entry["ovs_config"])
                    logging.info("deploy new config to:" + entry["uuid"])