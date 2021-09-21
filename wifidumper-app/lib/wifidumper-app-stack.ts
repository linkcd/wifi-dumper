import * as cdk from '@aws-cdk/core';
import * as iam from '@aws-cdk/aws-iam';
import * as s3 from '@aws-cdk/aws-s3';
import * as lambda from '@aws-cdk/aws-lambda';
import { Duration } from '@aws-cdk/core';
import * as sqs from '@aws-cdk/aws-sqs';
import * as s3n from '@aws-cdk/aws-s3-notifications';
import * as lambdaEventSources from '@aws-cdk/aws-lambda-event-sources';
import * as path from "path";

export class WifidumperAppStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const RAW_DATA_S3_BUCKET = 'wifidumper';
    const RAW_DATA_PATH_FOR_AP = "raw/ap";

    const RESULT_DATA_S3_BUCKET = 'wifidumper-result'
    const OUTPUT_PATH_FOR_AP = "timeline-report/ap"

    // S3
    const rawDataS3Bucket = s3.Bucket.fromBucketName(
      this,
      "rawDataS3Bucket",
      RAW_DATA_S3_BUCKET,
    );

    const resultS3Bucket = new s3.Bucket(this, RESULT_DATA_S3_BUCKET, {
      removalPolicy: cdk.RemovalPolicy.RETAIN
    });

    // SQS
    const newWifidumperLogEventQueue = new sqs.Queue(this, "wifidumper-s3-newlog-event-queue", {
      queueName: "wifidumper-s3-newlog-event-queue",
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      visibilityTimeout: Duration.minutes(1)
    });

    // set up trigger from s3 new object to sqs 
    rawDataS3Bucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(newWifidumperLogEventQueue),
      {prefix: 'raw/ap/'}
    );

    // Lambda
    const dockerfile = path.join(__dirname, "lambda-src/process-ap");
    
    const ap_handler = new lambda.DockerImageFunction(this, "process-ap-rawdata-lambda", {
      functionName: "Wifidumper-process-ap-rawdata",
      code: lambda.DockerImageCode.fromImageAsset(dockerfile, {
        repositoryName : "process-ap-data-lambda-images"
      }),
      memorySize: 128,
      timeout: Duration.minutes(1)
    });

    // setup lambda for handling sqs events
    const eventSource = new lambdaEventSources.SqsEventSource(newWifidumperLogEventQueue);
    ap_handler.addEventSource(eventSource);

    // Permission of lambda to s3
    rawDataS3Bucket.grantRead(ap_handler);
    resultS3Bucket.grantReadWrite(ap_handler);



  }
}
