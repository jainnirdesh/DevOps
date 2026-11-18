# Lab 1 — Task 6: Basic Jenkins CI/CD Pipeline

Execution date: 18 November 2026. Reports follow the supplied reference structure; evidence below belongs to this local run.

## Objective

Implement a Jenkins job that runs application validation and prepare SCM checkout and automated polling configuration.

## Prerequisite — Jenkins executor availability

The existing Jenkins service and installed plugins were available. The Ubuntu /tmp workaround from the reference was not required or applied on this Mac.

## Step 1 — Create the Freestyle project

Created devops-lab1-freestyle-local through one-time local Jenkins administration. It copies app.py and test_app.py to the Jenkins workspace and runs them.

## Step 2 — Configure Source Code Management

```
Prepared SCM template: jenkins/freestyle-scm.xml
Repository URL: https://github.com/jainnirdesh/DevOps.git
Branch Specifier: */main
```

These are settings in the importable remote-job template. The verified local job uses a local source snapshot. Remote checkout requires the lab files to be published first.

## Step 3 — Configure the automated build trigger

```
Poll SCM: H/5 * * * *
```

This trigger is defined in the remote SCM template. A remote polling build has not yet been demonstrated.

## Step 4 — Define the build step

The configured local job shell step is:

```
export PATH=/opt/homebrew/bin:$PATH
cp "/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/app.py" .
cp "/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/test_app.py" .
python3 app.py
python3 -m unittest test_app.py -v
```

The prepared remote job instead runs the versioned build script:

```
sh "Lab 1/scripts/run_pipeline.sh"
```

## Step 5 — Initial build

Build #1 was scheduled during setup and finished SUCCESS. All four tests passed.

Figure 1 — Actual Freestyle build #1 console result (Figure rendered from the actual saved console log.)

## Step 6 — Trigger an automated build from a commit

Remaining procedure: publish the lab, import the remote SCM template, run an initial build, then push a subsequent commit and wait for polling. Verify the build cause and console output. This remote automation is not yet an executed result.

## Result

The local Freestyle job ran successfully. SCM checkout and polling settings are prepared; automatic GitHub-trigger verification is pending.
