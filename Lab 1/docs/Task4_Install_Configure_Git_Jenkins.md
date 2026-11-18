# Lab 1 — Task 4: Install and Configure Git and Jenkins

Execution date: 18 November 2026. Reports follow the supplied reference structure; evidence below belongs to this local run.

## Objective

Verify and configure the Git and Jenkins environment needed for the lab. Existing installations were used on macOS.

## Environment

```
Platform: local Mac (macOS)
Git: 2.50.1 (Apple Git-155)
Python: 3.14.2
Java: OpenJDK 21.0.12 (Homebrew)
Jenkins: 2.568.2
URL: http://localhost:8080
Service: homebrew.mxcl.jenkins-lts
```

## Step 1 — Install Git

Git was already available, so installation was unnecessary. The reference uses Ubuntu apt; this report records the actual Mac environment.

## Step 2 — Verify the installation

```
git --version
# git version 2.50.1 (Apple Git-155)
```

## Step 3 — Set the Git configuration

The existing identity was Nirdesh Jain <jainnirdesh1@gmail.com>. No global settings were overwritten. Repository-local identity was set in the isolated Git demo.

```
git config user.name "Nirdesh Jain"
git config user.email "jainnirdesh1@gmail.com"
```

## Step 4 — Verify the configuration

```
git config user.name
Nirdesh Jain
git config user.email
jainnirdesh1@gmail.com
```

Figure 1 — Verified installed tooling and identity (Figure rendered from the actual saved console log.)

## Jenkins Installation

The existing Homebrew Jenkins service was reused with Java 21. No new Jenkins installation was performed. The local setup script created the two lab jobs, and the service was restarted to load the one-time administrative initialization. The startup script was removed after successful setup.

```
launchctl kickstart -k gui/$(id -u)/homebrew.mxcl.jenkins-lts
```

Installed Git and Pipeline plugins were present. Jenkins was reachable on localhost:8080, with authentication enabled. No AWS instance, public security group or Ubuntu systemd service was used.

Figure 2 — Successful build confirms Jenkins executes the local pipeline (Figure rendered from the actual saved console log.)

## Result

Existing Git and Jenkins installations were verified, Git identity was confirmed, and both local Jenkins jobs completed successfully.
