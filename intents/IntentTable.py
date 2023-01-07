from threading import Timer

from intents.utils import getUsage
from intents.utils import sendPhoneNotifiction

"""
IntentTable - Used to store the devices, used, roles and bandwidth classes to be accessed by webhook

Functions
----------

update_bandiwdth    - Created when the application is first run. Used to start the thread that
                    polls Ryu for bandwidth updates. If it goes over 50mbits it will send notification

add_device          - Used to add a device

get_mac             - Used to get the MAC for a given hostname

new_role            - Adds a new role with a list of intents to apply to the role

delete_device       - In case a device drops, it will delete the device

update_usage        - Used to update the usage when the intent to come through
                      to get the latest statistic


"""
class IntentTable:
    def __init__(self):
        self.devices = Devices()
        self.users = Users()
        self.roles = Roles()
        self.bandwidth = Bandwidth()
        self.log = []
        self.update_bandwidth()
        self.bandwidthLogger = {}

    def update_bandwidth(self):
        if x := self.bandwidth.update_usage():
            if x not in self.bandwidthLogger:
                self.bandwidthLogger = {x: 1}
            else:
                if self.bandwidthLogger[x] == 6:
                    log = self.get_usage()
                    if len(log) == 2:
                        name, hostname = log
                        sendPhoneNotifiction(
                            f"High Bandwidth Usage Alert: {name} is using the most with their {hostname}")
                    else:
                        sendPhoneNotifiction(f"High Bandwidth Usage Alert: {log} is using the most")
                self.bandwidthLogger[x] = self.bandwidthLogger[x] + 1

        t = Timer(interval=10, function=self.update_bandwidth, args=None)
        t.start()

    def add_device(self, hostname, mac, user=False):
        if user:
            self.users.add_user(user, hostname, mac)
            self.users.add_device(user, hostname, mac)
        else:
            self.devices.add_device(hostname, mac)

    def get_mac(self, hostname, user=False):
        if not Users:
            return self.devices.host_to_mac(hostname)
        else:
            u = self.users.get_user(user)
            print(u)
            return u.get("Devices").host_to_mac(hostname)

    def new_role(self, name, intents, user=False):
        self.roles.add_role(name, intents)
        if not user:
            return
        else:
            self.users.add_role(name, name)

    def delete_device(self, mac):
        for x in self.users.items():
            x.delete_device(mac)
        self.devices.delete_device(mac)

    def update_usage(self):
        self.bandwidth.update_usage()

    def get_usage(self):
        usage = self.bandwidth.get_usage()
        counter = 0
        for mac, change in usage.items():
            if counter < change or change == 0:
                if n := self.users.get_user_from_mac(mac):
                    d = self.users.get_user(n)["Devices"]
                    hostname = d.mac_to_host(mac)
                    self.log = [n, hostname]
        print(self.log)
        if len(self.log) == 2:
            name, hostname = self.log
            return name, hostname
        else:
            return self.log


"""
Tables used for tracking devices, users and roles
"""


class Roles:
    def __init__(self):
        self.roles = []

    """
    Add role:
        Parameters:
        Name = Name of Role
        Intents = [IntentFunc, params for func]
    
    Upon adding of role, runs the intent function        
    """

    def add_role(self, name, intents):
        self.roles[name].append(intents)
        intents[0](**intents[1:])

    """
    GetIntents:
        Returns the intent functions for a certain user
    """

    def get_intents(self, name):
        return self.roles[name]


"""
User Class
"""


class Users:
    def __init__(self):
        self.users = {}

    """
    AddUser
        Parameters:
        Name = Name of User
        Role = Role to attach to user (Not needed if no extra intents to be added)
        DeviceMAC = Device to attach to user
    """

    def add_user(self, name, hostname, mac, role=None):
        if name not in self.users:
            if not hostname and mac:
                d = Devices()
            else:
                d = Devices(hostname, mac)

            if not role:
                self.users[name] = {"Devices": d}
            else:
                self.users[name] = {"Role": role, "Devices": d}

    """
    AddDevice:
        Parameters:
        Name = Username
        Hostname = Name of device
        deviceMAC = MAC of new address to add
    """

    def add_device(self, name, hostname, device_mac):
        d = self.users[name]["Devices"]
        d.add_device(hostname, device_mac)
        self.users[name]["Devices"] = d

    def add_role(self, name, role):
        if not self.users[name]:
            return None
        else:
            self.users[name]["Role"] = role

    def get_user(self, name):
        print(name)
        print(self.users)
        if name not in self.users:
            print("hi?")
            return
        return self.users[name]

    def get_user_from_mac(self, mac):
        for name, devices in self.users.items():
            d = devices["Devices"]
            if d.mac_to_host(mac):
                return name
        return None


class Devices:
    def __init__(self, hostname=False, mac=False):
        if not hostname and mac:
            self.devices = {}
        else:
            self.devices = {hostname: mac}

    def add_device(self, name, mac):
        self.devices[name] = mac

    def delete_device(self, mac):
        """
        Devices { Hostname : MAC }

        Loop through devices, find where MAC from Ryu == loop
        """
        for k, v in dict(self.devices).items():
            if v == mac:
                del self.devices[k]
        return None

    def host_to_mac(self, host):
        if not self.devices[host]:
            return None
        else:
            return self.devices[host]

    def mac_to_host(self, mac):
        for hostname, macDevice in self.devices.items():
            if mac == macDevice:
                return hostname
        return None


class Bandwidth:
    def __init__(self):
        self.bytesInFlow = {}
        self.usage = {}

    def calculate_bandwidth(self, change):
        second = change / 10
        # About 50 megabit per second
        if second >= 6250000:
            return True

    def update_usage(self):
        r = getUsage()

        for mac, b in r.items():
            if mac not in self.usage:
                self.bytesInFlow[mac] = b
                self.usage[mac] = b
            else:
                change = b - self.bytesInFlow[mac]
                percentage = change / self.bytesInFlow[mac]
                self.bytesInFlow[mac] = b
                self.usage[mac] = percentage
                if self.calculate_bandwidth(change):
                    return mac

    def get_usage(self):
        return self.usage
