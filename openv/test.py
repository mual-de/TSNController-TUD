from openflowController import OpenFlowController
import json
ovs = OpenFlowController("http://localhost:8080")
print(ovs.getListOfSwitches())
rule = json.loads("""{
    "dpid": 1,
    "cookie": 1,
    "cookie_mask": 1,
    "table_id": 0,
    "idle_timeout": 30,
    "hard_timeout": 30,
    "priority": 11111,
    "flags": 1,
    "match":{
        "in_port":1
    },
    "actions":[
        {
            "type":"OUTPUT",
            "port": 2
        }
    ]
 }""")
ovs.addFlowRule(rule)