import * as cdk from '@aws-cdk/core';
import * as iam from '@aws-cdk/aws-iam';
import * as s3 from '@aws-cdk/aws-s3';
import * as lambda from '@aws-cdk/aws-lambda';
import { ContextProvider, Duration } from '@aws-cdk/core';
import * as sqs from '@aws-cdk/aws-sqs';
import * as s3n from '@aws-cdk/aws-s3-notifications';
import * as ts from '@aws-cdk/aws-timestream';
import * as lambdaEventSources from '@aws-cdk/aws-lambda-event-sources';
import * as path from "path";
import {WifidumperInfraStack} from "./wifidumper-infra-stack"

export class WifidumperAppStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 source and target
    const rawDataS3Bucket = s3.Bucket.fromBucketName(
      this,
      "rawDataS3Bucket",
      WifidumperInfraStack.RAW_DATA_S3_BUCKET,
    );

    const resultS3Bucket = s3.Bucket.fromBucketName(
      this,
      "resultDataS3Bucket",
      WifidumperInfraStack.RESULT_DATA_S3_BUCKET,
    );

    // SQS PART
    // dead queue for both AP Queue and Client Queue
    const deadLetterQueue = new sqs.Queue(this, "wifidumperdlq", {
      queueName: "wifidumperdlq",
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      retentionPeriod: Duration.days(14)
    });

    // SQS for AP
    const APFileUploadedEventQueue = new sqs.Queue(this, "wifidumper-ap-file-upload-event-queue", {
      queueName: "wifidumper-ap-file-upload-event-queue",
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      visibilityTimeout: Duration.minutes(1),
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: deadLetterQueue
      }
    });

    // SQS for Client
    const ClientFileUploadedEventQueue = new sqs.Queue(this, "wifidumper-client-file-upload-event-queue", {
      queueName: "wifidumper-client-file-upload-event-queue",
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      visibilityTimeout: Duration.minutes(1),
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: deadLetterQueue
      }
    });
  
    // set up triggers from s3 new object to sqs 
    // AP 
    rawDataS3Bucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(APFileUploadedEventQueue),
      {prefix: "raw/ap/" }
    );

    // Client 
    rawDataS3Bucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.SqsDestination(ClientFileUploadedEventQueue),
      {prefix: "raw/client/" }
    );

    const dockerfile = path.join(__dirname, "lambda-src");
    // Lambda for AP
    const APHandler = new lambda.DockerImageFunction(this, "Wifidumper-process-ap-lambda", {
      functionName: "Wifidumper-process-ap-lambda",
      code: lambda.DockerImageCode.fromImageAsset(dockerfile , { 
        file: "Dockerfile-ap"
      }),
      memorySize: 256,
      timeout: Duration.minutes(1),
      environment :{
        "RESULT_DATA_S3_BUCKET" : WifidumperInfraStack.RESULT_DATA_S3_BUCKET,
        "CHECK_TIME_FREQ" : "15T", //default 15min, 50% of data source freq, to avoid missing point in report
        "MAIN_REPORT_OUTPUT_KEY": "timeline-reports/ap.parquet", 
        "SHORT_LIVE_REPORT_OUTPUT_KEY" : "timeline-reports/ap_shortlive.parquet", 
        "AP_TABLE" : WifidumperInfraStack.AP_TABLE,
        "SHORTLIVE_AP_TABLE" : WifidumperInfraStack.SHORTLIVE_AP_TABLE
      }
    });

    // Lambda for Client
    const ClientHandler = new lambda.DockerImageFunction(this, "Wifidumper-process-client-lambda", {
      functionName: "Wifidumper-process-client-lambda",
      code: lambda.DockerImageCode.fromImageAsset(dockerfile , { 
        file: "Dockerfile-client"
      }),
      memorySize: 256,
      timeout: Duration.minutes(1),
      environment :{
        "RESULT_DATA_S3_BUCKET" : WifidumperInfraStack.RESULT_DATA_S3_BUCKET,
        "CHECK_TIME_FREQ" : "10T", //default 15min if not override here
        "MAIN_REPORT_OUTPUT_KEY": "timeline-reports/client.parquet", 
        "SHORT_LIVE_REPORT_OUTPUT_KEY" : "timeline-reports/client_shortlive.parquet",
        "CLIENT_TABLE" : WifidumperInfraStack.CLIENT_TABLE,
        "SHORTLIVE_CLIENT_TABLE" : WifidumperInfraStack.SHORTLIVE_CLIENT_TABLE
      }
    });

    // setup AP lambda for handling sqs events
    const APEventSource = new lambdaEventSources.SqsEventSource(APFileUploadedEventQueue);
    APHandler.addEventSource(APEventSource);

    const ClientEventSource = new lambdaEventSources.SqsEventSource(ClientFileUploadedEventQueue);
    ClientHandler.addEventSource(ClientEventSource);

    // Permission of lambda to s3
    rawDataS3Bucket.grantRead(APHandler);
    resultS3Bucket.grantReadWrite(APHandler);
    rawDataS3Bucket.grantRead(ClientHandler);
    resultS3Bucket.grantReadWrite(ClientHandler);

    //Permission of lambda to Timestream
    // IAM policies
    let ts_arn = "arn:aws:timestream:*:*:database/" + WifidumperInfraStack.TSDB_NAME + "/table/*"
    const timeStreamPolicy = new iam.PolicyStatement({
      actions: ["timestream:*"],
      resources: [ts_arn]
    });
    APHandler.addToRolePolicy(timeStreamPolicy);
    ClientHandler.addToRolePolicy(timeStreamPolicy);
    


  }
}
