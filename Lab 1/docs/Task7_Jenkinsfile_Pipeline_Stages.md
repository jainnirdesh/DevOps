# Lab 1 — Task 7: Jenkinsfile Defining Pipeline Stages

Execution date: 18 November 2026. Reports follow the supplied reference structure; evidence below belongs to this local run.

## Objective

Create a declarative Jenkinsfile defining Build, Test and Deploy, and demonstrate stage execution.

## Step 1 — Write the Jenkinsfile

The Jenkinsfile is in Lab 1/Jenkinsfile because this repository contains a lab subdirectory. Each stage enters Lab 1 after SCM checkout.

```
pipeline {
    agent any
    environment { PATH = "/opt/homebrew/bin:${env.PATH}" }
    triggers { pollSCM('H/5 * * * *') }
    options { disableConcurrentBuilds() }
    stages {
        stage('Build') {
            steps {
                dir('Lab 1') {
                    sh 'python3 --version'
                    sh 'python3 -m py_compile app.py'
                }
            }
        }
        stage('Test') {
            steps {
                dir('Lab 1') { sh 'python3 -m unittest test_app.py -v' }
            }
        }
        stage('Deploy') {
            steps {
                dir('Lab 1') {
                    sh 'mkdir -p deployment && cp app.py deployment/app.py'
                    sh 'python3 deployment/app.py'
                }
            }
        }
    }
    post {
        success { echo 'Pipeline completed successfully' }
        failure { echo 'Pipeline failed' }
    }
}
```

## Stage responsibilities

Build verifies the Python environment and compiles app.py. Test runs four unit tests and stops normal stage progression on failure. Deploy copies the verified app into deployment/ and executes it. Post actions print success or failure.

## Step 2 — Commit the Jenkinsfile to version control

The following publication procedure remains pending:

```
git add "Lab 1"
git commit -m "Add Lab 1 declarative Jenkins pipeline"
git push origin main
```

## Step 3 — Create the Pipeline job

Verified job: devops-lab1-pipeline-local. It uses an inline declarative pipeline with Build, Test and Deploy and copies the local source into its workspace. For remote execution, import jenkins/pipeline-scm.xml with these settings:

```
Definition: Pipeline script from SCM
SCM: Git
Repository URL: https://github.com/jainnirdesh/DevOps.git
Branch Specifier: */main
Script Path: Lab 1/Jenkinsfile
```

## Step 4 — Execute the pipeline

Local Pipeline build #1 completed SUCCESS. The actual console shows Build, Test, Deploy and the success post action. The local inline pipeline validates stage behavior; the repository Jenkinsfile has not yet been executed from GitHub SCM.

Figure 1 — Local Jenkins pipeline build #1 completed successfully (Figure rendered from the actual saved console log.)

```
Started
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /Users/nirdeshjain/.jenkins/workspace/devops-lab1-pipeline-local
[Pipeline] {
[Pipeline] withEnv
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Build)
[Pipeline] sh
+ cp '/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/app.py' .
+ cp '/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/test_app.py' .
+ python3 --version
Python 3.14.2
+ python3 -m py_compile app.py
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Test)
[Pipeline] sh
+ python3 -m unittest test_app.py -v
test_empty_message (test_app.TestApp.test_empty_message) ... ok
test_farewell (test_app.TestApp.test_farewell) ... ok
test_greet (test_app.TestApp.test_greet) ... ok
test_shout (test_app.TestApp.test_shout) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Deploy)
[Pipeline] sh
+ mkdir -p deployment
+ cp app.py deployment/
+ python3 deployment/app.py
Hello, DevOps!
Goodbye, DevOps!
DEVOPS AUTOMATION
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Declarative: Post Actions)
[Pipeline] echo
Pipeline completed successfully
[Pipeline] }
[Pipeline] // stage
[Pipeline] }
[Pipeline] // withEnv
[Pipeline] }
[Pipeline] // node
[Pipeline] End of Pipeline
Finished: SUCCESS
```

## Result

The three-stage declarative pipeline was demonstrated successfully in local Jenkins. The repository Jenkinsfile and SCM job definition are prepared for publication and subsequent remote execution.
