#!/usr/local/bin/python3

import datetime
import time
import os
import boto3

def lambda_handler(event, context):
    instName = "" 
    ec = boto3.client('ec2')
    os.environ['TZ'] = 'UTC'
    ts = time.time()
    DayOfWeek = datetime.datetime.fromtimestamp(ts).strftime('%w')
    Year = datetime.datetime.fromtimestamp(ts).strftime('%Y')
    Month = datetime.datetime.fromtimestamp(ts).strftime('%m')
    DayOfMonth = datetime.datetime.fromtimestamp(ts).strftime('%d')
    HourOfDay = datetime.datetime.fromtimestamp(ts).strftime('%-H')
    MinuteOfDay = datetime.datetime.fromtimestamp(ts).strftime('%M')
    SecOfDay = datetime.datetime.fromtimestamp(ts).strftime('%S')
    print (DayOfWeek)
    print (Year)
    print (Month)
    print (DayOfMonth)
    print (HourOfDay)
    print (MinuteOfDay)
    print (SecOfDay)   
    reservations = ec.describe_instances( ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    for instance in instances:
        try:
            for tag in instance['Tags']:
                #if tag['Key'] == 'Name' and tag['Value'][-3:] == '-no':
                #    print "SKIP because -no was found"
                #elif tag['Key'] == 'Name' and "bam::" in tag['Value']:
                #    print "SKIP because bam:: was found"
                if tag['Key'] == 'Name':
                        instName = tag['Value']
        except:
            print ("My bad, this instance has no tags")

        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            devname = dev['DeviceName']
            instanceId = instance['InstanceId']
            #print "Found EBS volume %s on instance %s with instanceID %s mounted at %s" % ( 
            #    vol_id, instName, instance['InstanceId'], devname)
            
            description = "%s-%s-%s-%s-%s-%s-%s-%s:%s:%s" % ( 
                instName, instanceId, devname, vol_id, Year, Month, DayOfMonth, HourOfDay, MinuteOfDay, SecOfDay)
            #print description
            if instName[-3:] == '-no':
                print ("SKIP because -no was found")
            elif "bam::" in instName:
                print ("SKIP because bam:: was found")
            else:
                print ("Creating Snapshot for")
                print (description)
                try:
                  response = ec.create_snapshot(
                  Description=description,
                  VolumeId=vol_id
                )
                except:
                  print ("ERROR: Could not create Snapshot")
                print (response)
                snapshotID = response['SnapshotId']
                #print snapId
                ec2 = boto3.resource('ec2')
                snapshot = ec2.Snapshot(snapshotID)
                snapshot.create_tags(
                  Tags=[
                     {
                        'Key':   'deleteTime',
                        'Value': 'SomeTimeSoon'
                     },
                    ]
                  )