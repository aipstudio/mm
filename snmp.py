# import section
from pysnmp.hlapi import *

community_string = 'public'
ip_address_host = '192.168.1.101'
#OID = '1.3.6.1.2.1.1.5.0' #oid hostname
OID = '1.3.6.1.2.1.1.1.0' #oid uname -a
OID_SET = '1.1.1.1.1.1.1.1.1.1'
def GetOID(community,ip,OID):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
           CommunityData(community_string, mpModel=0),
           UdpTransportTarget((ip_address_host, 161)),
           ContextData(),
           ObjectType(ObjectIdentity(OID)))
)

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))

def SendOID(community,ip,OID_SET):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        sendNotification(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip, 162)),
            ContextData(),
            '',
            NotificationType(
                ObjectIdentity(OID_SET)
            )
        )
    )

    if errorIndication:
        print(errorIndication)

#SendOID(community_string,ip_address_host,OID_SET)
GetOID(community_string,ip_address_host,OID)