Lab 1 - Task 6: Basic Jenkins Pipeline

Student: Nirdesh Jain
Date: 18 November 2026 (Asia/Kolkata)

Local Jenkins Freestyle and Pipeline jobs are configured using jenkins/setup-local.groovy. Local jobs copy source into Jenkins workspaces and validate the app. Importable remote SCM job definitions are provided as jenkins/freestyle-scm.xml and jenkins/pipeline-scm.xml. Remote jobs require the Lab 1 files to be present on GitHub main. Freestyle shell runs sh "Lab 1/scripts/run_pipeline.sh" and polls every five minutes. Remote clone and automatic polling are pending verification.

Verified Jenkins results: devops-lab1-freestyle-local build #1 SUCCESS; devops-lab1-pipeline-local build #1 SUCCESS (Build, Test, Deploy completed; four tests passed). Console logs are saved under evidence/. Jobs are available at http://localhost:8080/. The one-time local administration script was removed from Jenkins startup after setup, so restarting Jenkins will not rerun this setup.
