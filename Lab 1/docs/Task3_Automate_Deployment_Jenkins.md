Lab 1 - Task 3: Automate Deployment Jenkins

Student: Nirdesh Jain
Date: 18 November 2026 (Asia/Kolkata)

scripts/run_pipeline.sh and Jenkinsfile define sequential Build, Test and Deploy. A test failure prevents deployment. Deployment copies app.py to a workspace deployment directory and executes it. Success/failure messages are supplied in the Jenkins post block. This demonstrates artifact deployment, not a public HTTP application. Automatic remote commit triggering has not been demonstrated.

Verified Jenkins results: devops-lab1-freestyle-local build #1 SUCCESS; devops-lab1-pipeline-local build #1 SUCCESS (Build, Test, Deploy completed; four tests passed). Console logs are saved under evidence/. Jobs are available at http://localhost:8080/. The one-time local administration script was removed from Jenkins startup after setup, so restarting Jenkins will not rerun this setup.
