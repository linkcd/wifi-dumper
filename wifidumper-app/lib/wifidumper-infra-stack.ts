import * as cdk from '@aws-cdk/core';
import * as iam from '@aws-cdk/aws-iam';
import * as s3 from '@aws-cdk/aws-s3';
import * as ts from '@aws-cdk/aws-timestream';

export class WifidumperInfraStack extends cdk.Stack {

  public static RAW_DATA_S3_BUCKET = 'wifidumper';
  public static RESULT_DATA_S3_BUCKET = 'wifidumper-result';
  public static TSDB_NAME = "wifidumperDB";
  public static AP_TABLE:string  = "accessPointTable";
  public static SHORTLIVE_AP_TABLE = "shortliveAccessPointTable";
  public static CLIENT_TABLE = "clientTable";
  public static SHORTLIVE_CLIENT_TABLE = "shortliveClientTable";

  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const TABLE_RETENTION_POLICY = {
        MemoryStoreRetentionPeriodInHours: (30 * 6).toString(10), //6 months
        MagneticStoreRetentionPeriodInDays: (365 * 3).toString(10) // 3 years
    }

    // const resultS3Bucket = new s3.Bucket(this, WifidumperInfraStack.RESULT_DATA_S3_BUCKET, {
    //   bucketName:WifidumperInfraStack.RESULT_DATA_S3_BUCKET,
    //   removalPolicy: cdk.RemovalPolicy.RETAIN
    // });

    // Timestream
    const wifidumperTSDB = new ts.CfnDatabase(this, WifidumperInfraStack.TSDB_NAME,{
        databaseName : WifidumperInfraStack.TSDB_NAME, 
    });
    wifidumperTSDB.applyRemovalPolicy(cdk.RemovalPolicy.RETAIN);  // make sure DB is not deleted when stack is destroyed.

    const apTable = new ts.CfnTable(this, WifidumperInfraStack.AP_TABLE,{
      databaseName: WifidumperInfraStack.TSDB_NAME, 
      tableName: WifidumperInfraStack.AP_TABLE,
      retentionProperties: TABLE_RETENTION_POLICY
    });
    apTable.node.addDependency(wifidumperTSDB);
    apTable.applyRemovalPolicy(cdk.RemovalPolicy.RETAIN);

    const shortliveAPTable = new ts.CfnTable(this, WifidumperInfraStack.SHORTLIVE_AP_TABLE,{
      databaseName: WifidumperInfraStack.TSDB_NAME, 
      tableName: WifidumperInfraStack.SHORTLIVE_AP_TABLE,
      retentionProperties: TABLE_RETENTION_POLICY
    });
    shortliveAPTable.node.addDependency(wifidumperTSDB);
    shortliveAPTable.applyRemovalPolicy(cdk.RemovalPolicy.RETAIN);

    const clientTable = new ts.CfnTable(this, WifidumperInfraStack.CLIENT_TABLE,{
      databaseName: WifidumperInfraStack.TSDB_NAME, 
      tableName: WifidumperInfraStack.CLIENT_TABLE,
      retentionProperties: TABLE_RETENTION_POLICY
    });
    clientTable.node.addDependency(wifidumperTSDB);
    clientTable.applyRemovalPolicy(cdk.RemovalPolicy.RETAIN);

    const shortliveClientTable = new ts.CfnTable(this, WifidumperInfraStack.SHORTLIVE_CLIENT_TABLE,{
      databaseName: WifidumperInfraStack.TSDB_NAME, 
      tableName: WifidumperInfraStack.SHORTLIVE_CLIENT_TABLE,
      retentionProperties: TABLE_RETENTION_POLICY
    });
    shortliveClientTable.node.addDependency(wifidumperTSDB);
    shortliveClientTable.applyRemovalPolicy(cdk.RemovalPolicy.RETAIN);

  }
}
