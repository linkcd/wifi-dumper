import * as cdk from '@aws-cdk/core';
import * as iam from '@aws-cdk/aws-iam';
import * as s3 from '@aws-cdk/aws-s3';
import * as lambda from '@aws-cdk/aws-lambda';
import { Duration } from '@aws-cdk/core';
import * as path from "path";

export class WifidumperAppStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const RAW_DATA_S3_BUCKET = 'wifidumper';
    const RAW_DATA_PATH_FOR_AP = "raw/ap";
    const OUTPUT_PATH_FOR_AP = "timeline-report/ap"

    // get existing s3 that contains the raw data
    const rawDataS3Bucket = s3.Bucket.fromBucketName(
      this,
      "rawDataS3Bucket",
      RAW_DATA_S3_BUCKET,
    );

    const dockerfile = path.join(__dirname, "lambda-src/process-ap");
    
    const ap_handler = new lambda.DockerImageFunction(this, "process-ap-rawdata-lambda", {
      code: lambda.DockerImageCode.fromImageAsset(dockerfile, {
        repositoryName : "process-ap-data-lambda-images"
      }),
      memorySize: 128,
      timeout: Duration.minutes(1)
    });



    rawDataS3Bucket.grantReadWrite(ap_handler);
  }
}
