import sys
import csv
import json
import boto3

from DnsRecord import DnsRecord

route53Client = boto3.client("route53")

csvFilePath = sys.argv[1]
domainName = sys.argv[2]
r53HostedZoneId = sys.argv[3]
batchComment = sys.argv[4]


if (not(domainName.endswith("."))):
    domainName = domainName + "."  # Must end with `.`

print("IMPORT " + csvFilePath + " INTO ZONE ID " + r53HostedZoneId)

file = open(csvFilePath)
csv = csv.reader(file)

recordCount = 0

r53ChangeBatch = {
    "Comment": batchComment,
    "Changes": []
}

mxValues = []
txtValues = []

for row in csv:
    if (row[0] == "Name"):
        continue

    record = DnsRecord(domainName, row[1], row[0], row[2], 1800)
    if (record.type == "SOA" or record.type == "NS"):
        continue

    # TODO: The TXT and MX logic need to be updated
    # So they are more robust and can handle records
    # for sub-domains

    if (record.type == "TXT"):
        if (not(record.value.startswith("\""))):
            record.value = "\"" + record.value
        if (not(record.value.endswith("\""))):
            record.value = record.value + "\""

        txtValues.append({"Value": record.value})
        continue  # don't add individual records to the batch

    if (record.type == "MX"):
        mxValues.append({"Value": record.value})
        continue  # don't add individual records to the batch

    r53ChangeBatch["Changes"].append(
        { 
            "Action": record.changeAction,
            "ResourceRecordSet": {
                "Name": record.name,
                "Type": record.type,
                "TTL": record.ttl,
                "ResourceRecords": [
                    {"Value": record.value}
                ]
            }
        }
    )

    recordCount = recordCount + 1

if (any(mxValues)):
    r53ChangeBatch["Changes"].append(
        { 
            "Action": record.changeAction,
            "ResourceRecordSet": {
                "Name": domainName,
                "Type": "MX",
                "TTL": 300,
                "ResourceRecords": mxValues
            }
        }
    )

if (any(txtValues)):
    r53ChangeBatch["Changes"].append(
        { 
            "Action": record.changeAction,
            "ResourceRecordSet": {
                "Name": domainName,
                "Type": "TXT",
                "TTL": 300,
                "ResourceRecords": txtValues
            }
        }
    )

route53Client.change_resource_record_sets(
    HostedZoneId=r53HostedZoneId,
    ChangeBatch=r53ChangeBatch)

print("")

print(json.dumps(r53ChangeBatch))

print("============="))
print("# of records imported: " + str(recordCount))
print("=============")
