from oscpy.server import OSCThreadServer
from time import sleep

osc = OSCThreadServer()
sock = osc.listen(address='0.0.0.0', port=7400, default=True)

@osc.address(b'/accxyz')
def callback(x, y, z):
    print(x)
    print(y)
    print(z)
    # print("got values: {}".format(values))

sleep(1000)
osc.stop()
