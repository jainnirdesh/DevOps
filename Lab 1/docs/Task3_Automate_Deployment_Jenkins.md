# Lab 1: DevOps Foundations & Continuous Integration — Task 3: Automate application deployment using Jenkins

Execution date: 18 November 2026. Reports follow the supplied reference structure; evidence below belongs to this local run.

## 1. Objective

Automate application deployment using sequential Jenkins stages, a build trigger and post-build reporting.

## 2. Build trigger

```
triggers { pollSCM('H/5 * * * *') }
```

The repository Jenkinsfile and Freestyle SCM template specify five-minute polling. The validated local jobs were scheduled during local setup and do not poll GitHub.

## 3. Automated build from a commit

After publishing this lab, import the SCM job templates and make a new commit to demonstrate automatic detection. The following commands are the remaining procedure, not executed results:

```
git add "Lab 1"
git commit -m "Add Lab 1 application and Jenkins pipeline"
git push origin main
```

Verify the resulting Jenkins build cause is SCM polling and retain its console output. No such remote trigger was observed in this run.

## 4. Deployment steps

```
stage('Deploy') {
    steps {
        dir('Lab 1') {
            sh 'mkdir -p deployment && cp app.py deployment/app.py'
            sh 'python3 deployment/app.py'
        }
    }
}
```

Deploy runs after Build and Test succeed. The artifact is copied to a workspace-local directory, avoiding collisions with unrelated deployments.

Figure 1 — Local pipeline completed Build, Test and Deploy (Figure rendered from the actual saved console log.)

## 5. Post-build actions

```
post {
    success { echo 'Pipeline completed successfully' }
    failure { echo 'Pipeline failed' }
}
```

## Result

Jenkins local Pipeline build #1 deployed and executed the tested app successfully. Remote commit-triggered deployment remains to be verified.
