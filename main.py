
import time
from flask import Flask
from flask import request
from flask import jsonify
import logging         
from netconf.netconfController import NetConfController
from openv.openflowController import OpenFlowController
import json

restserver = Flask(__name__)
restserver.config['JSON_SORT_KEY'] = False


def flaskThread():
    restserver.run(debug=True, host='0.0.0.0', port = 9090, use_reloader=True)

@restserver.route("/actualStatus", methods=["GET"])
def getActualStatus():
    return jsonify({'status':'ok'}), 201

@restserver.route("/setConfiguration", methods=["POST"])
def setConfiguration():
    config = request.json
    print(config)
    logging.info("incomming configuration")
    logging.info(json.dumps(config))
    nc = NetConfController()
    ovs = OpenFlowController("http://localhost:8080")
    print("DEPLOY NETCONF")
    nc.deployJSONConfiguration(config)
    print("DEPLOY OVS")
    ovs.deployJSONConfiguration(config)
    return jsonify({'status':'ok'}), 201

@restserver.route("/getSwitches/ovs", methods=["GET"])
def getOVSSwitches():
    ovs = OpenFlowController("http://localhost:8080")
    return jsonify(ovs.getListOfSwitches()), 201


logging.basicConfig(level=logging.INFO, filename="log/networkController.log")
flaskThread()