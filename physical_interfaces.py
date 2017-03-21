# Classes for testing devices in the network domain
import collections

VALID_SPEEDS = ["1000", "10000"]
VALID_CONNECTORS = ["COPPER", "FIBER"]

XC_Ports = collections.namedtuple('XC_Ports', 'matched notMatched')


# Device Types.  
DUT = 'Dut'
TRAFFIC_GENERATOR = "TrafficGenerator"
SERVER = "Server"
IXIA = "Ixia"
SAOS = "Saos"
LINUX = "Linux"
IXIAOS = "Ixos"
WINDOWS = "Windows"
# Depricated: DEFAULT_SAOS_PROMPT = ['{0}.*> '.format(deviceName)]
DEFAULT_LINUX_PROMPT = [r'[^\r\n:]+:[^\$#]+\$|# $']
DEFAULT_GENERIC_SERVER_PROMPT = [r'[^\r\n:]+:[^\$#]+\$|# $']
DEFAULT_VALIMAR_PROMPT = [r'[^\r\n:]+:[^\$#]+\$|# $']

class PhysicalInterface (object):
    __name__ = "PhysicalInterface"
   
    def __str__ (self):
        return ('%s: slot=%s, port=%s, speed=%s, phyType=%s' % (self.__name__, str(self.slot),
                                                                str(self.port), str(self.speed),
                                                                self.phyType))

    def __init__(self, *args, **kwargs):
        if len(args) == 4:
            self.slot = str(args[0])
            self.port = str(args[1])
            self.speed = self._validateSpeed (args[2])
            self.phyType = self._validatePhyType (args[3])
        else:
            self.chassisId = str(args[0])
            self.slot = str(args[1])
            self.port = str(args[2])
            self.speed = self._validateSpeed (args[3])
            self.phyType = self._validatePhyType (args[4])
        try:
            self.portType = kwargs['portType']
        except:
            self.portType = None

    def SmplAsString (self):
        if hasattr (self, "chassisId"):
            return "%s,%s,%s" % (self.chassisId, self.slot, self.port)
        else:
            return "%s,%s" % (self.slot, self.port)

    def SmplAsList (self):
        if hasattr (self, "chassisId"):
            return [self.chassisId, self.slot, self.port]
        else:
            return [self.slot, self.port]

    def FqAsString (self):
        if hasattr (self, "chassisId"):
            return "%s,%s,%s,%s" % (self.chassisId, self.slot, self.port, self.phyType.lower())
        else:
            return "%s,%s,%s" % (self.slot, self.port, self.phyType.lower())

    def FqAsList (self):
        if hasattr (self, "chassisId"):
            return [self.chassisId, self.slot, self.port, self.phyType.lower()]
        else:
            return [self.slot, self.port, self.phyType.lower()]

    def _validateSpeed (self, speed):
        if speed.upper() not in VALID_SPEEDS:
            raise RuntimeError ("Invalid speed - %s" % speed.upper())
        return speed.upper()
    
    def _validatePhyType (self, phyType):
        if phyType.upper() not in VALID_CONNECTORS:
            raise RuntimeError ("Invalid phyType - %s" % phyType.upper())
        return phyType.upper()

    def hwPortId (self):
        return self.device.hwPortId (self.port)    

class DeviceBase (object):
    __name__ = "DeviceBase"

    def getatts(self):
        import inspect
        ret = "%s: " % self.__name__
        for a in dir(self):
            if not a.startswith("_"):
                if not inspect.ismethod(getattr(self, a)):
                    if ret:
                        ret += ", "
                    ret += "%s=%s" % (a, getattr(self, a))
        return ret

    def __str__(self):
        return self.getatts()

    def __init__(self, *args, **kwargs):
        self.ports = self.getPorts()
        self.reboot = "reboot"
        for name, value in kwargs.items():
            setattr (self, name, value)

    def getPorts (self):
        """Get a list of PhysicalInterface objects defined in the class.

        Target devices are defined in a setup file.  They consist of zero or more
        port definitions as PhysicalInterface objects.  To maintain backwards
        compatability with the existing CI infrastructure, port definitions
        are added as individual attribures instead of a list.  By convention,
        each attribute of type PhysicalInterface defines a single port.  Thus
        to create a list of ports associated with this device, I simply gather
        all the attributes of type PhysicalInterface.

        :returns: A list of PhysicalInterface objects sorted by *port.name*.
        """
        ports = []
        portNames = []
        deviceDef = self
        for attributeName in dir(deviceDef):
            if not attributeName.startswith("_"):
                attributeObj = getattr(deviceDef, attributeName) 
                try:
                    if attributeObj.__name__ == "PhysicalInterface":
                        if "%s" % attributeObj in portNames:
                            self.ctfLogVInfo ("Duplicate port def '%s' in %s" % ("%s" % attributeObj,
                                                                                 attributeName))
                            return None
                        attributeObj.name = attributeName
                        attributeObj.deviceName = self.deviceName
                        attributeObj.deviceType = self.deviceType
                        attributeObj.osType = self.osType
                        attributeObj.device = deviceDef
                        ports.append(attributeObj)
                   
                        portNames.append("%s" % attributeObj)
                except:
                    pass
        return ports

    def getSimplePortListAsLoS (self, whichPorts=[]):
        """Generate a list of simple port descriptions as a list of strings.

        A simple port desc has the form: {chassisId, slot, port}. Differs from a fully qualified
        port desc in that it does not includes the physicial description.

        :param whichPorts: A list of port names for which the portList is generated. i.e.:
          ["port1", "port4"]
        :returns: A list of port definitions in the form of a sting.  The string is formated
          as a Tcl list of lists: i.e: {1,1,2 1,1,3}. Each string is defined
          as *"<chassisId>","<bus>","<port>"*.
        """
        portList = []

        # whichPorts probably contains ints. Need to wchPorts = [str(x) for x in whichPorts]
        if whichPorts:
            ports = []
            for p in self.ports:
                if p in whichPorts:
                    ports.append(p)
        else:
            ports = self.ports 
        for port in ports:
            portList.append(port.SmplAsString())
        return portList

    def getFQPortListAsLoS (self, whichPorts=[]):
        """Generate a list of fully qualified port descriptions as a list of lists.

        A fully qualified port desc has the form: {chassisId, slot, port, phy}. Differs from simple
        port desc in that it includes the physicial description.

        :param whichPorts: A list of port objects from which the portList is generated.
        :returns: A list of port definitions in the form of a sting.  The string is formated
          as a Tcl list of lists: i.e: {1,1,2,copper 1,1,3,fiber}. Each sublist is defined
          as *"<chassisId>","<bus>","<port>","<phy-type>"*.
        """
        portList = []
        if whichPorts:
            ports = []
            for p in self.ports:
                if p in whichPorts:
                    ports.append(p)
        else:
            ports = self.ports 
        for port in ports:
            portList.append(port.FqAsString())
        return portList

    def getSimplePortListAsLoL (self, whichPorts=[]):
        """Generate a list of simple port descriptions as a list of lists.

        A simple port desc has the form: {chassisId, slot, port}. Differs from a fully qualified
        port desc in that it does not includes the physicial description.

        :param whichPorts: A list of port objects from which the portList is generated.
        :returns: A list of port definitions in the form of a sting.  The string is formated
          as a Tcl list of lists: i.e: {{1 1 2} {1 1 3}}. Each sublist is defined
          as *{<chassisId> <bus> <port>}*.
        """
        portList = []
        if whichPorts:
            ports = []
            for p in self.ports:
                if p in whichPorts:
                    ports.append(p)
        else:
            ports = self.ports 
        for port in ports:
            portList.append(port.SmplAsList())
        return portList

    def getFQPortListAsLoL (self, whichPorts=[]):
        """Generate a list of fully qualified port descriptions as a list of lists.

        A fully qualified port desc has the form: {chassisId, slot, port, phy}. Differs from simple
        port desc in that it includes the physicial description.

        :param whichPorts: A list of port objects from which the portList is generated.
        :returns: A list of port definitions in the form of a sting.  The string is formated
          as a Tcl list of lists: i.e: {{1 1 2 copper} {1 1 3 fiber}}. Each sublist is defined
          as *{<chassisId> <bus> <port> <phy-type>}*.
        """
        portList = []
        if whichPorts:
            ports = []
            for p in self.ports:
                if p in whichPorts:
                    ports.append(p)
        else:
            ports = self.ports 

        for port in ports:
            portList.append(port.FqAsList())
        return portList

    def hwPortId (self, logicalPortId):
        """Returns a given hardware port id based on a logicalPortId.
        """

        if hasattr (self, "hwIdPortMap"):
            try:
                return self.hwIdPortMap [logicalPortId]
            except KeyError:
                return logicalPortId
        else:
            return logicalPortId

class Ixia (DeviceBase, object):
    __name__ = "Ixia"
    deviceName = 'Ixia'
    deviceType = TRAFFIC_GENERATOR
    osType = IXIA
    prompt = [r".*~# "]
    interface = "telnet"
   
    def __str__(self):
        return self.getatts()

    def __init__(self, *args, **kwargs):

        super(Ixia, self).__init__(*args, **kwargs)
        for port in self.ports:
            if not hasattr (port, "chassisId"):
               port.chassisId = '1'
            port.deviceType = self.deviceType
            port.deviceName = self.deviceName
            port.osType = self.osType
 
    def getHandle(self):
        """Derive and return a handle for ETHTBXh functions.

        :returns: A handle (string) as *IXIA.<chassisId>,<bus>,<port>[-].<chassisId>,<bus>,<port>*
           i.e.: *IXIA.1,1,2-1,1,3*.
        """
        handle = ""
        for port in self.ports:
            if handle:
                handle += '-'
            handle += port.SmplAsString()
        return "IXIA" + "." + handle

class CrossConnect (object):
    __name__ = "CrossConnect"
    
    def __str__(self):
        import inspect
        ret = "%s: " % self.__name__
        for a in dir(self):
            if not a.startswith("_"):
                if not inspect.ismethod(getattr(self, a)):
                    if ret:
                        ret += ", "
                    ret += "%s=%s" % (a, getattr(self, a))
        return ret

    def __init__(self, port1, port2):
        self.port1 = port1
        self.port2 = port2
        
    def portsByType(self, deviceType=None):
        """Returns a list of ports associated with devices of a certain type.

        Valid deviceType values are a list of "TrafficGenerator", "Dut", "Server", 
        and/or None.

        Typically a script designates roles to certain cross connections.  For instance,
        a vlan might set things up so that the dut receives traffic on one connection and
        transmit on another.  In order to configure the vlan and traffic generator you need
        to know what ports are associated with which devices.  Often you do not need to know
        more about the device than whether it is a traffic generator or not.  The deviceType
        gives you that info.

        :param deviceType: A device type identifier or list of identifiers.  Valid values
            are "TrafficGenerator", "Dut", "Server", or None.  If None, return all ports.
        :returns: An list of matched ports
        """

        def selectPort (ports, port, deviceType):
            if deviceType == port.deviceType:
                ports.append(port)

        ports = []

        if deviceType:
            selectPort (ports, self.port1, deviceType)
            selectPort (ports, self.port2, deviceType)
        else:
            ports.append(self.port1)
            ports.append(self.port2)

        return ports

    def portsByName(self, deviceName=None):
        """Get a tuple of a list of ports in the cross connection associated with and are not
        associated with the device identified by deviceName.

        Typically a script designates roles to certain cross connections.  For instance,
        a vlan might be set things up so that the dut receives traffic on one connection and
        transmit on another.  In order to configure the vlan and traffic generator you need
        to know what ports are associated with which devices.

        :param deviceName: A device name like "Ixia".  If None, return all ports.
        :returns: A tuple: The first element of which is a list of ports that are associated with
            the named device. The second element being all the devices that are not associated with
            the named device.
        """
        def selectPort (ports, port, deviceName):
            if deviceName == port.deviceName:
                ports.append(port)

        ports = []

        if deviceName:
            selectPort (ports, self.port1, deviceName)
            selectPort (ports, self.port2, deviceName)
        else:
            ports.append(self.port1)
            ports.append(self.port2)

        return ports

class Topology (object):
    __name__ = "Topology"
    
    def getatts(self):
        import inspect
        ret = ""
        for a in dir(self):
            if not a.startswith("_"):
                if not inspect.ismethod(getattr(self, a)):
                    if ret:
                        ret += ", "
                    ret += "%s=%s" % (a, getattr(self, a))
        return ret

    def __str__(self):
        return self.getatts()

    def __init__(self):
        self.xCons = self.getXCons()

    def getXCons (self):
        """Get a dict of the cross connections defined in the class.

        :returns: A dict of cross connections in topology definition.
        """

        xcons = {}
        deviceDef = self
        for attributeName in dir(deviceDef):
            if not attributeName.startswith("_"):
                attributeObj = getattr(deviceDef, attributeName) 
                if attributeObj.__name__ == "CrossConnect":
                    xcons[attributeName] = attributeObj
        return xcons

    def portsByDevType(self, xcon, deviceType=None):
        """Returns a XC_Ports object that contains a list of matched and notMatched ports.

        Valid deviceType values are a list of "TrafficGenerator", "Dut", "Server", 
        and/or None.

        Typically a script designates roles to certain cross connections.  For instance,
        a vlan might set things up so that the dut receives traffic on one connection and
        transmit on another.  In order to configure the vlan and traffic generator you need
        to know what ports are associated with which devices.  Often you do not need to know
        more about the device than whether it is a traffic generator or not.  The deviceType
        gives you that info.


        :param xcon: An object of type CrossConnection.
        :param deviceType: A device type identifier or list of identifiers.  Valid values
            are "TrafficGenerator", "Dut", "Server", or None.
        :returns: An enumberated list where matched=list of matched ports, notMatched contains
            a list of not matching ports.
        """
        def selectPort (ports, notPorts, port, deviceType):
            if deviceType == port.deviceType:
                ports.append(port)
            else:
                notPorts.append(port)

        ports = []
        notPorts = []

        if deviceType:
            selectPort (ports, notPorts, xcon.port1, deviceType)
            selectPort (ports, notPorts, xcon.port2, deviceType)
        else:
            ports.append(xcon.port1)
            ports.append(xcon.port2)
        return XC_Ports(matched=ports, notMatched=notPorts)

    def portsByDevName(self, xcon, deviceName=None):
        """Returns a XC_Ports object that contains a list of matched and notMatched ports.

        Typically a script designates roles to certain cross connections.  For instance,
        a vlan might be set things up so that the dut receives traffic on one connection and
        transmit on another.  In order to configure the vlan and traffic generator you need
        to know what ports are associated with which devices.


        :param xcon: An object of type CrossConnection.
        :param deviceName: A device name like "Ixia".
        :returns: A tuple: The first element of which is a list of ports that are associated with
            the named device. The second element being all the devices that are not associated with
            the named device.
        """
        def selectPort (ports, notPorts, port, deviceName):
            if deviceName == port.deviceName:
                ports.append(port)
            else:
                notPorts.append(port)

        ports = []
        notPorts = []
        if deviceName:
            selectPort (ports, notPorts, xcon.port1, deviceName)
            selectPort (ports, notPorts, xcon.port2, deviceName)
        else:
            ports.append(xcon.port1)
            ports.append(xcon.port2)
        return XC_Ports(matched=ports, notMatched=notPorts)

class LinuxServer (DeviceBase, object):
    __name__ = 'LinuxServer'
    deviceName = 'unknown'
    deviceType = SERVER
    osType = LINUX
    #prompt = [r'[0-9]\> ']
    prompt = DEFAULT_LINUX_PROMPT
    interface = 'ssh'
   
class GenericServer (DeviceBase, object):
    __name__ = 'GenericServer'
    deviceName = 'unknown'
    deviceType = SERVER
    osType = LINUX
    prompt = DEFAULT_GENERIC_SERVER_PROMPT
    interface = 'ssh'

class SaosDut (object):
    deviceType = DUT
    osType = SAOS
    userName = 'gss'
    password = 'pureethernet'
    interface = 'telnet'

class ValimarDut (object):
    deviceType = DUT
    osType = LINUX
    userName = 'diag'
    password = 'diag'
    prompt = DEFAULT_VALIMAR_PROMPT
    interface = 'valimar-ssh'
    suToRoot = True
    dfltRootPassword = 'ciena123'
    dfltSuPassword = 'wwpciena'
    ypshellPort = 22
    ypshellUserName = 'user'
    ypshellPassword = 'ciena123'
    ypshellPrompt = [r'user.*\> $']


# Ciena VNF
class Ciena0804 (ValimarDut, DeviceBase, object):
    __name__ = 'Ciena0804'
    deviceName = '0804'
    hwIdPortMap = {'1':'4', '2':'3', '3':'2', '4':'1'}

    def __init__(self, *args, **kwargs):
        super (Ciena0804, self).__init__(*args, **kwargs)

class Ciena0904 (ValimarDut, DeviceBase, object):
    __name__ = 'Ciena0904'
    deviceName = '0904'
    hwIdPortMap = {'1':'4', '2':'3', '3':'2', '4':'1'}

    def __init__(self, *args, **kwargs):
        super (Ciena0904, self).__init__(*args, **kwargs)

class Ciena0905 (ValimarDut, DeviceBase, object):
    __name__ = 'Ciena0905'
    deviceName = '0905'

    def __init__(self, *args, **kwargs):
        super (Ciena0905, self).__init__(*args, **kwargs)

class Ciena0906 (ValimarDut, DeviceBase, object):
    __name__ = 'Ciena0906'
    deviceName = '0906'

    def __init__(self, *args, **kwargs):
        super (Ciena0906, self).__init__(*args, **kwargs)

class Ciena0908 (ValimarDut, DeviceBase, object):
    __name__ = 'Ciena0908'
    deviceName = '0908'
    hwIdPortMap = {'1':'4', '2':'3', '3':'2', '4':'1'}

    def __init__(self, *args, **kwargs):
        super (Ciena0908, self).__init__(*args, **kwargs)

class Ciena3902 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3902'
    deviceName = '3902'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3902, self).__init__(*args, **kwargs)

class Ciena3906 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3906'
    deviceName = '3906'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3906, self).__init__(*args, **kwargs)

class Ciena3906s (ValimarDut, DeviceBase, object):
    __name__ = 'Ciena3906s'
    deviceName = '3906s'

    def __init__(self, *args, **kwargs):
        super (Ciena3906s, self).__init__(*args, **kwargs)

class Ciena3911 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3911'
    deviceName = '3911'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3911, self).__init__(*args, **kwargs)

class Ciena3916 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3916'
    deviceName = '3916'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3916, self).__init__(*args, **kwargs)

class Ciena3920 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3920'
    deviceName = '3920'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3920, self).__init__(*args, **kwargs)

class Ciena3930 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3930'
    deviceName = '3930'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3930, self).__init__(*args, **kwargs)

class Ciena3931 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3931'
    deviceName = '3931'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3931, self).__init__(*args, **kwargs)

class Ciena3932 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3932'
    deviceName = '3932'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3932, self).__init__(*args, **kwargs)

class Ciena3938 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3938'
    deviceName = '3938'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3938, self).__init__(*args, **kwargs)

class Ciena3940 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3940'
    deviceName = '3940'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3940, self).__init__(*args, **kwargs)

class Ciena3942 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3942'
    deviceName = '3942'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3942, self).__init__(*args, **kwargs)

class Ciena3960 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena3960'
    deviceName = '3960'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena3960, self).__init__(*args, **kwargs)

class Ciena5140 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena5140'
    deviceName = '5140'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena5140, self).__init__(*args, **kwargs)

class Ciena5142 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena5142'
    deviceName = '5142'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena5142, self).__init__(*args, **kwargs)

class Ciena5150 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena5150'
    deviceName = '5150'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena5150, self).__init__(*args, **kwargs)

class Ciena5160 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena5160'
    deviceName = '5160'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena5160, self).__init__(*args, **kwargs)

class Ciena5410 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena5410'
    deviceName = '5410'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena5410, self).__init__(*args, **kwargs)

class Ciena6500 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena6500'
    deviceName = '6500'
    prompt = [r'[0-9a-zA-Z]+\# ', r'[0-9a-zA-Z]+\> ', r'[0-9a-zA-Z]+\>']
    userName = 'admin'
    password = 'ADMIN'

    def __init__(self, *args, **kwargs):
        super (Ciena6500, self).__init__(*args, **kwargs)

class Ciena8700 (SaosDut, DeviceBase, object):
    __name__ = 'Ciena8700'
    deviceName = '8700'
    prompt = ['{0}.*> '.format(deviceName)]

    def __init__(self, *args, **kwargs):
        super (Ciena8700, self).__init__(*args, **kwargs)

