Lab 1 - Task 7: Jenkinsfile Pipeline Stages

Student: Nirdesh Jain
Date: 18 November 2026 (Asia/Kolkata)

Lab 1/Jenkinsfile defines Build, Test, Deploy and success/failure post actions. It uses dir("Lab 1") because this lab lives below the repository root. SCM Script Path must be Lab 1/Jenkinsfile. Local validation uses a separate inline Jenkins pipeline so that unpublished files can be exercised. This is distinct from a verified Pipeline-from-SCM run.

Verified Jenkins results: devops-lab1-freestyle-local build #1 SUCCESS; devops-lab1-pipeline-local build #1 SUCCESS (Build, Test, Deploy completed; four tests passed). Console logs are saved under evidence/. Jobs are available at http://localhost:8080/. The one-time local administration script was removed from Jenkins startup after setup, so restarting Jenkins will not rerun this setup.
