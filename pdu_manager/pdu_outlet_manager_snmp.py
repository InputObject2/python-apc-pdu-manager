from pysnmp.hlapi import getCmd, setCmd, CommunityData, SnmpEngine, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

class PDUOutletManagerSNMP():
    def __init__(self) -> None:
        pass

    async def get_outlet_status(ip, community, oid):
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),  # Use SNMP v2c
            UdpTransportTarget((ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        if errorIndication:
            print(errorIndication)
            return None
        else:
            for varBind in varBinds:
                return varBind[1]  # Returns the value of the OID

    async def set_outlet_state(ip, community, oid, state_value):
        errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),  # Use SNMP v2c
            UdpTransportTarget((ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid), state_value)
        )

        if errorIndication:
            print(errorIndication)
            return False
        else:
            return True
