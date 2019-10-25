class DnsRecord:
    def __init__(self, domainName, type, name, value, ttl):
        self.type = type.replace(" Record", "")
        self.name = name
        self.value = value
        self.ttl = ttl

        if (self.name == ""):
            self.name = domainName

        if (not(self.name.endswith(domainName))):
            self.name = self.name + "." + domainName

        self.changeAction = 'UPSERT'
        self.resourceRecords = [
            {'Value': self.value}
        ]
