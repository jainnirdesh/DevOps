Lab 1 - Task 4: Install Configure Git Jenkins

Student: Nirdesh Jain
Date: 18 November 2026 (Asia/Kolkata)

Host: macOS, not the Ubuntu/AWS machine in the supplied reports. Existing installations were reused: Git, Python, Jenkins 2.568.2 and Homebrew OpenJDK 21. See evidence/environment.log. Existing Git identity is Nirdesh Jain <jainnirdesh1@gmail.com>. No global Git settings were changed. Jenkins is served at http://localhost:8080 with authentication enabled.

Verified Jenkins results: devops-lab1-freestyle-local build #1 SUCCESS; devops-lab1-pipeline-local build #1 SUCCESS (Build, Test, Deploy completed; four tests passed). Console logs are saved under evidence/. Jobs are available at http://localhost:8080/. The one-time local administration script was removed from Jenkins startup after setup, so restarting Jenkins will not rerun this setup.
