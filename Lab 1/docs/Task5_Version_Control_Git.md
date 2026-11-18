# Lab 1 — Task 5: Set Up Version Control Using Git

Execution date: 18 November 2026. Reports follow the supplied reference structure; evidence below belongs to this local run.

## Objective

Initialize Git, stage and commit files, create feature branches and demonstrate fast-forward and explicit merge commits.

## Step 1 — Initialize the repository and add source files

The demo repository was isolated under evidence during execution and archived as a Git bundle afterwards.

```
git init -b main
git config user.name "Nirdesh Jain"
git config user.email "jainnirdesh1@gmail.com"
```

```
def greet(name):
    return f"Hello, {name}!"
```

The complete lab application and its test suite are stored in Lab 1/app.py and Lab 1/test_app.py.

```
def greet(name):
    return f"Hello, {name}!"


def farewell(name):
    return f"Goodbye, {name}!"


def shout(message):
    return message.upper()


if __name__ == "__main__":
    print(greet("DevOps"))
    print(farewell("DevOps"))
    print(shout("DevOps automation"))
```

```
import unittest
from app import greet, farewell, shout


class TestApp(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("DevOps"), "Hello, DevOps!")

    def test_farewell(self):
        self.assertEqual(farewell("DevOps"), "Goodbye, DevOps!")

    def test_shout(self):
        self.assertEqual(shout("DevOps automation"), "DEVOPS AUTOMATION")

    def test_empty_message(self):
        self.assertEqual(shout(""), "")


if __name__ == "__main__":
    unittest.main()
```

## Step 2 — Stage and commit

```
git add app.py
git commit -m "Initial commit: greeting application"
# Root commit: 24e3f1b
```

## Step 3 — Create a branch and commit on it

```
git checkout -b feature/farewell
# Add farewell(name) to app.py
git add app.py
git commit -m "Add farewell function"
# Commit: 1b02eac
```

## Step 4 — Merge the branch back into main

```
git checkout main
git merge feature/farewell
# Fast-forward: 24e3f1b -> 1b02eac
```

Main had not advanced after the branch was created, so Git moved its pointer forward without creating a merge commit.

## Step 5 — Second branch with an explicit merge commit

```
git checkout -b feature/uppercase
# Add shout(message) to app.py
git add app.py
git commit -m "Add shout function"
git checkout main
git merge --no-ff feature/uppercase -m "Merge feature/uppercase into main"
git log --oneline --graph --all --decorate
```

Figure 1 — Actual commit graph with explicit merge 3fea871 (Figure rendered from the actual saved console log.)

## Step 6 — Push the repository to GitHub

The parent repository already has origin https://github.com/jainnirdesh/DevOps.git. No remote push was performed. To publish the lab, review and commit the Lab 1 directory in the parent repository, then push main. The isolated demo history is provided as a bundle rather than being merged into the parent history.

## Step 7 — Verify on GitHub

Remote verification remains pending. Locally, the bundle preserves main, feature/farewell and feature/uppercase. To inspect the demo:

```
git clone -b main "Lab 1/evidence/git-demo.bundle" /tmp/lab1-git-demo
git -C /tmp/lab1-git-demo log --oneline --graph --all --decorate
```

## Result

Local initialization, staging, commits, branching and both merge types completed successfully. GitHub publication is pending.
