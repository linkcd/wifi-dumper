# Wifi dumper

## 1. Deployment
### 1.1 Create 2 S3 buckets:
```bash
- wifidumper
- wifidumper-result
```
They could be created as a part of infra-as-code. If you are using different names, update them in wifidumper-app/lib/wifidumper-infra-stack.ts

### 1.2 Deploy the stateful resources (timestream database) using CDK
```bash
cdk deploy WifidumperInfraStack 
```

### 1.3 Deploy the stateless resources (sqs, lambda, etc) using CDK
```bash
cdk deploy WifidumperAppStack  
```