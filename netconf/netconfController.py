from ncclient import manager
from .netconfConfig import NetConfConfig
import xml.etree.ElementTree as ET
import logging
from .bindings.tsnrepo import TNsysrepo
import xml.etree.ElementTree as ET
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONDecoder
from pyangbind.lib.serialise import pybindIETFXMLEncoder
import time

class NetConfController():
    """This class controls als connections to Netconf Servers and provide access to necessary informations.

    :author: Alexander Mueller
    """

    def __init__(self, listOfSwitches=None):
        self.listOfSwitchManagers = dict()
        if listOfSwitches != None:
            for switch in listOfSwitches:
                pass

    def deployConfigurationToSwitch(self, switchUUID, configurationXML):
        """Copy a configuration to target configuration datastore.
        :param switchUUID: uuid to specify target switch
        :param configurationXML: configuration for target in xml format.
        """
        if switchUUID in self.listOfSwitchManagers.keys():
            self.listOfSwitchManagers[switchUUID].edit_config(target='candidate', config=configurationXML, default_operation="replace")
            logging.info("SET configuration of Switch: " + switchUUID +" TO: " + configurationXML)
            return True
        else:
            logging.error("Switch with uuid:" + switchUUID + " is not known!")
            return False

    def addSwitch(self, switch, uuid):
        print(switch)
        logging.info("Try to connect to switch with uuid:" + uuid)
        logging.info("HOST: " + str(switch["host"]))
        logging.info("PORT: " + str(switch["port"]))
        m = manager.connect(host=switch["host"], port=int(switch["port"]), username=switch["username"], hostkey_verify=False, password = switch["password"],device_params={'name':'default'})
        if m != None:
            self.listOfSwitchManagers[uuid] = m
            logging.info("Successfully connected to switch with uuid:" + uuid)
            return True
        else:
            logging.error("Can't connect to switch with uuid:" + uuid + " @ " + str(switch["host"]))
            return False

    def getActualConfigFrom(self, uuid):
        """Get actual running configuration from a switch.
        :param uuid: UUID of switch.
        :return: None if connection not established or an xml fragment containing the whole configuration.
        """
        if uuid in self.listOfSwitchManagers.keys():
            return self.listOfSwitchManagers[uuid].get_config(source='running').data_xml
        else:
            logging.error("Switch with uuid:" + uuid+ " is not known!")
            return None


    def commitCandidatesToRunning(self):
        """Change deployed configurations to running configuration on all associated switches.
        """
        print(self.listOfSwitchManagers)
        for key in self.listOfSwitchManagers.keys():
            self.listOfSwitchManagers[key].commit()



    def closeConnection(self, uuid):
        """Close connection to a netconf server, identified by its uuid.
        """
        logging.info("Try to close connection to switch with: " + uuid)
        if uuid in self.listOfSwitchManagers.keys():
            try:
                answer = self.listOfSwitchManagers[uuid].close()
                # del self.listOfSwitchManagers[uuid]
                logging.info("Successfully disconnect from switch with uuid:" + uuid)
                logging.info(answer)
            except:
                logging.info("Something annoying happened!")
        else:
            logging.error("Switch with uuid:" + uuid + " is not known!")
            return None

    def closeAll(self):
        """Close all connections to netconf deployJSONConfiguration(config)servers.
        """
        for switch in self.listOfSwitchManagers.keys():
            self.closeConnection(switch)

    def deployJSONConfiguration(self, jsonConfig):
        for entry in jsonConfig:
            if entry["fpga_sw_active"]:
                self.addSwitch(entry["fpga_sw_data"], entry["uuid"])
                xmlStr = self._getConfigXML_(entry)
                self.deployConfigurationToSwitch(entry["uuid"],xmlStr)
        time.sleep(0.02)
        self.commitCandidatesToRunning()
        time.sleep(0.02)
        self.closeAll()

    def _getConfigXML_(self, jsonConfig):
        if jsonConfig["fpga_sw_data"]["sw_type"] == "trustnodev1":
            tsnTmp = TNsysrepo()
            pybindJSONDecoder.load_json(jsonConfig["fpga_config"],None, None, obj=tsnTmp)
            xmlStr = pybindIETFXMLEncoder.serialise(tsnTmp)
            logging.info("FPGA CONFIG XML:" + xmlStr)
            return xmlStr
        return None
