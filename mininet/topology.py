from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController

##--- Add hosts---##
def addHosts(net, n):
    hosts=[]
    for x in range(n):
        ## Really bad way of doing this - only supports up to 9 hosts but thats all i need
        num = x+1
        hosts.append(net.addHost("h" + str(num), ip="10.0.0." + str(num), mac="00:00:00:00:00:0" + str(num)))
    return hosts

##--- Add Links ---##
def addLinks(net, hosts, switch):
    for x in hosts:
        net.link(x, switch)

if __name__ == "__main__":
    ##--- Add controller ---##
    net = Mininet(controller = RemoteController)
    net.addController("c0", controller=RemoteController, ip="127.0.0.1", port=6653)
    
    ##--- Add hosts --###
    hosts = addHosts(net, 9)
    ##--- Add Switch ---##
    s1 = net.addSwitch("s1", protocols="OpenFlow13")
    ##--- Add Links ---##
    addLinks(net, hosts, s1)
    net.start()        
    CLI(net)
    
    
