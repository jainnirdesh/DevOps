# Lab 1: DevOps Foundations and Continuous Integration

Student: Nirdesh Jain
Repository: https://github.com/jainnirdesh/DevOps

Run locally from this directory:

```sh
sh scripts/run_pipeline.sh
```

The example app implements greeting, farewell and uppercase functions. Build compiles Python; Test checks all functions; Deploy copies the tested app to `deployment/` and executes it. Deployment here is a local artifact demonstration, not a hosted web service.

Jenkins Pipeline: select Pipeline script from SCM, Git repository above, branch `*/main`, script path `Lab 1/Jenkinsfile`. The Jenkins agent needs Python 3 on PATH. Poll SCM checks for changes every five minutes. Push these files before using remote SCM.

Freestyle: same Git repository and branch; Poll SCM `H/5 * * * *`; Execute shell: `sh "Lab 1/scripts/run_pipeline.sh"`.

Original supplied DOCX reports are preserved under docs/reference. Their author, screenshots and AWS results are reference material and are not evidence of this run. Actual local outputs are in evidence/. Task reports document completed and pending verification separately.

Verified Jenkins jobs: [Freestyle](http://localhost:8080/job/devops-lab1-freestyle-local/) and [Pipeline](http://localhost:8080/job/devops-lab1-pipeline-local/), build #1 SUCCESS for each. These local jobs do not poll GitHub.

SCM configurations: jenkins/freestyle-scm.xml and jenkins/pipeline-scm.xml. Local job administration source: jenkins/setup-local.groovy. Applied once through Jenkins startup administration, then removed from startup.
