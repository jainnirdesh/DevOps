# Lab 1: DevOps Foundations & Continuous Integration — Task 1: Record all commands, configurations, screenshots and observations

Execution date: 18 November 2026. Reports follow the supplied reference structure; evidence below belongs to this local run.

## 1. Install and configure Git and Jenkins

Git, Jenkins and Java were already installed on this Mac. The existing installation was verified and reused. Ubuntu apt commands from the reference do not apply to this host. The existing Git identity was retained.

```
$ git --version
git version 2.50.1 (Apple Git-155)
$ python3 --version
Python 3.14.2
$ git config user.name
Nirdesh Jain
$ git config user.email
jainnirdesh1@gmail.com
$ /opt/homebrew/opt/openjdk@21/bin/java -version
openjdk version "21.0.12" 2026-07-21
OpenJDK Runtime Environment Homebrew (build 21.0.12)
OpenJDK 64-Bit Server VM Homebrew (build 21.0.12, mixed mode, sharing)
```

Figure 1 — Git, Python and Java versions and configured Git identity (Figure rendered from the actual saved console log.)

Jenkins responds on http://localhost:8080 and reports version 2.568.2. Authentication remains enabled. Its existing Homebrew service uses OpenJDK 21.

## 2. Version control with Git

An isolated demonstration repository was used to record commits and both merge types without changing the parent repository history. The repository was archived as evidence/git-demo.bundle.

```
$ git init -b main
Initialized empty Git repository in /Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/evidence/git-demo/.git/
$ git config user.name Nirdesh Jain
$ git config user.email jainnirdesh1@gmail.com
$ git add app.py
$ git commit -m Initial commit: greeting application
[main (root-commit) 24e3f1b] Initial commit: greeting application
 1 file changed, 2 insertions(+)
 create mode 100644 app.py
$ git checkout -b feature/farewell
Switched to a new branch 'feature/farewell'
$ git add app.py
$ git commit -m Add farewell function
[feature/farewell 1b02eac] Add farewell function
 1 file changed, 3 insertions(+)
$ git checkout main
Switched to branch 'main'
$ git merge feature/farewell
Updating 24e3f1b..1b02eac
Fast-forward
 app.py | 3 +++
 1 file changed, 3 insertions(+)
$ git checkout -b feature/uppercase
Switched to a new branch 'feature/uppercase'
$ git add app.py
$ git commit -m Add shout function
[feature/uppercase af70cfc] Add shout function
 1 file changed, 3 insertions(+)
$ git checkout main
Switched to branch 'main'
$ git merge --no-ff feature/uppercase -m Merge feature/uppercase into main
Merge made by the 'ort' strategy.
 app.py | 3 +++
 1 file changed, 3 insertions(+)
$ git log --oneline --graph --all --decorate
*   3fea871 (HEAD -> main) Merge feature/uppercase into main
|\
| * af70cfc (feature/uppercase) Add shout function
|/
* 1b02eac (feature/farewell) Add farewell function
* 24e3f1b Initial commit: greeting application
$ git bundle create /Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/evidence/git-demo.bundle --all
```

Figure 2 — Actual branch and merge history (Figure rendered from the actual saved console log.)

Observation: the first merge fast-forwarded main. The second merge used --no-ff and produced merge commit 3fea871. A Git bundle preserves all three branches. No remote push was performed.

## 3. Jenkins Freestyle job

```
Job: devops-lab1-freestyle-local
Source: local application snapshot copied to the Jenkins workspace
Build: python3 app.py
       python3 -m unittest test_app.py -v
Build #1: SUCCESS
```

Figure 3 — Freestyle build #1 test output (Figure rendered from the actual saved console log.)

The remote SCM job template is jenkins/freestyle-scm.xml. It specifies the user repository, */main, H/5 * * * * polling and the lab build script. Remote polling is configured in the template but has not been demonstrated live.

## 4. Jenkinsfile pipeline configuration

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

Figure 4 — Actual local Jenkins pipeline stage output (Figure rendered from the actual saved console log.)

The verified local Pipeline job uses an inline definition and copied source. The repository Jenkinsfile is prepared for Pipeline script from SCM with Script Path Lab 1/Jenkinsfile. These are distinct execution modes.

## Result

Local build, four unit tests, artifact deployment, Git operations and both Jenkins jobs succeeded. Remote GitHub push and SCM-triggered execution remain pending.
