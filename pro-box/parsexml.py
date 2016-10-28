# -*- coding: utf-8 -*-
import xmltodict;
import sys

try:
    import json
except:
    import simplejson as json

class FileOp:
    def __init__(self):
        pass
    
    @classmethod
    def parseFileOpConfig(cls,data,plugin_Dir):
        configFile = plugin_Dir + "etc/file_op.rules"
        for (k,v) in  data.items():
            if k == "fileAudit":
            # if k == "fileAudit" or k == "fileCheck":
                output = open(configFile, 'w')
                for (k1,v1) in v.items(): 
                    for i in  v1:
                        for (k2,v2) in i.items():
                            output.write(v2)
                output.write("\n")
                output.close()
        
# if __name__ == '__main__':
#     file_object = open('客户端审计.xml')
#     try:
#         all_the_text = file_object.read()
#     finally:
#         file_object.close()
#     print all_the_text
    
#     convertedDict = xmltodict.parse(all_the_text);
#     data =  convertedDict['root']
#     policyId =  data['@policyId']
#     data.pop('@policyId')
#     policyType =  data['@policyType']
#     data.pop('@policyType')
#     policyName =  data['@policyName']
#     data.pop('@policyName')
#     fp = FileOp
#     fp.parseFileOpConfig(data,"./")
    # print policyId, policyType, policyName
    # output = open(policyName, 'w')
    
    # for (k,v) in  data.items():
    #     if k == "fileAudit":
    #         output = open(k, 'w')
    #     if k == "fileCheck":
    #         pass
            
    #     output.write(k)
    #     for (k1,v1) in v.items(): 
    #         print k1,v1
    #         for i in  v1:
    #             for (k2,v2) in i.items():
    #                 print v2
    #     output.write("\n")
    # output.close()
#     <?xml version="1.0" encoding="UTF-8" ?> 
# - <root policyId="e4212c949c74472abb6a932a0845e562" policyType="7" policyName="test2">
#   </root>