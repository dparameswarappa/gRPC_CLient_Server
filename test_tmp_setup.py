from ctf.libs.physical_interfaces import PhysicalInterface as PI
from ctf.libs.physical_interfaces import CrossConnect as XC
from ctf.libs.physical_interfaces import Ixia, Topology, DeviceBase
from ctf.libs.physical_interfaces import Ciena0904

ftp = type("ftp", (Ciena0904, object), dict (
    __str__ = Ciena0904.getatts,
    hostName = '10.33.80.170',
    userName = 'labuser',
    password = 'labuser@123'
    ))
ftp_server = ftp()

Dut1 = type("Dut1", (Ciena0904, object), dict (
    __str__ = Ciena0904.getatts,
    interface = "ssh",
    #password = 'diag',
    localIp = '10.33.80.170',
    hostName = '10.33.80.170',
    userName = 'labuser',
    password = 'labuser@123',
    #remoteIp = '',
    #userName = 'diag',
    port = None,
    ))
dut1 = Dut1()
