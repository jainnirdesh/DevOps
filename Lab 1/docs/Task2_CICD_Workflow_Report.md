# Lab 1: DevOps Foundations & Continuous Integration — Task 2: CI/CD workflow report

Execution date: 18 November 2026. Reports follow the supplied reference structure; evidence below belongs to this local run.

## 1. Introduction

This report describes the Lab 1 CI/CD workflow for a small Python application. Git records source changes, Jenkins performs validation, and the deployment stage copies and executes the tested application.

## 2. Pipeline architecture

```
Verified local workflow:
Local source -> Jenkins workspace -> Build -> Test -> Deploy -> Result

Prepared remote workflow:
Developer -> commit / push -> GitHub main
                           -> Poll SCM (H/5 * * * *)
                           -> Jenkins -> Build -> Test -> Deploy
```

Source repository: github.com/jainnirdesh/DevOps. Lab directory: Lab 1. Runtime: Python 3.14.2. Server: Jenkins 2.568.2 on macOS with OpenJDK 21. Jobs: devops-lab1-freestyle-local and devops-lab1-pipeline-local. The remote workflow requires publishing the lab and importing the provided SCM job templates.

Figure 1 — Version control branch topology (Figure rendered from the actual saved console log.)

## 3. Pipeline stages

Build prints the Python version and compiles app.py. Test runs four unittest cases covering greeting, farewell, uppercase and an empty message. Deploy copies app.py into a workspace deployment directory and runs it. A failed stage prevents subsequent normal stages; post actions report the final result.

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

Figure 2 — Successful execution of all three stages (Figure rendered from the actual saved console log.)

## 4. Automation results

Freestyle build #1: SUCCESS. Pipeline build #1: SUCCESS. Four tests passed. Deployed output: Hello, DevOps!; Goodbye, DevOps!; DEVOPS AUTOMATION. These results are from local source snapshots; no GitHub-triggered build is claimed.

Figure 3 — Freestyle validation output (Figure rendered from the actual saved console log.)

## 5. Observations

SCM polling checks for changes approximately every five minutes after configuration. A Jenkinsfile versions pipeline logic with source code. The Lab 1 subdirectory must be included in the SCM script path. Python must be available on the Jenkins agent PATH. Local artifact execution demonstrates deployment mechanics; it does not start a web server.

## 6. Conclusion

## Result

The local CI/CD stages were verified in Jenkins. The supplied SCM definitions prepare the GitHub integration; publishing and automatic-trigger verification remain pending.
