Lab 1 - Task 2: CICD Workflow Report

Student: Nirdesh Jain
Date: 18 November 2026 (Asia/Kolkata)

Workflow: Python source -> Build (py_compile) -> Test (unittest) -> Deploy (workspace artifact and execution). Local pipeline passed all four tests. GitHub remote: https://github.com/jainnirdesh/DevOps.git. Jenkins local jobs validate the application. End-to-end GitHub polling remains pending until Lab 1 files are committed/pushed and SCM jobs are imported. Poll schedule: H/5 * * * *. Jenkinsfile script path: Lab 1/Jenkinsfile.

Verified Jenkins results: devops-lab1-freestyle-local build #1 SUCCESS; devops-lab1-pipeline-local build #1 SUCCESS (Build, Test, Deploy completed; four tests passed). Console logs are saved under evidence/. Jobs are available at http://localhost:8080/. The one-time local administration script was removed from Jenkins startup after setup, so restarting Jenkins will not rerun this setup.
