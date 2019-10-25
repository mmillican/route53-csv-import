import csv
import json
import boto3
import argparse

from DnsRecord import DnsRecord

parser = argparse.ArgumentParser(description='CSV Route53 Importer')
parser.add_argument('--file', action='store', dest='file', required=True,
                    help='The CSV file to import')
parser.add_argument('--domain', action='store', dest='domain', required=True,
                    help='The domain name')
parser.add_argument('--zoneId', action='store', dest='zoneId', required=True,
                    help='The Hosted Zone ID')
parser.add_argument('-c', action='store', dest='comment', required=True,
                    help='Comment to associate with the batch update')
# parser.add_argument('')

args = parser.parse_args()
print(args)

route53Client = boto3.client("route53")

if (not(args.domain.endswith("."))):
    domainName = args.domain + "."  # Must end with `.`

print("IMPORT " + args.file + " INTO ZONE ID " + args.zoneId)

file = open(args.file)
csv = csv.reader(file)

recordCount = 0

r53ChangeBatch = {
    "Comment": args.comment,
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
    HostedZoneId=args.zoneId,
    ChangeBatch=r53ChangeBatch)

print("")

print(json.dumps(r53ChangeBatch))

print("=============")
print("# of records imported: " + str(recordCount))
print("=============")
