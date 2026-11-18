import jenkins.model.Jenkins
import hudson.model.FreeStyleProject
import hudson.tasks.Shell
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition

def j = Jenkins.get()
def p = j.getItem('devops-lab1-pipeline-local') ?: j.createProject(WorkflowJob, 'devops-lab1-pipeline-local')
p.setDescription('Local Lab 1 validation. SCM configuration is supplied separately; no remote polling demonstrated.')
p.setDefinition(new CpsFlowDefinition("pipeline {\n agent any\n options { disableConcurrentBuilds() }\n environment { PATH = \"/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin\" }\n stages {\n  stage('Build') { steps { sh 'cp \"/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/app.py\" .; cp \"/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/test_app.py\" .; python3 --version; python3 -m py_compile app.py' } }\n  stage('Test') { steps { sh 'python3 -m unittest test_app.py -v' } }\n  stage('Deploy') { steps { sh 'mkdir -p deployment && cp app.py deployment/ && python3 deployment/app.py' } }\n }\n post { success { echo 'Pipeline completed successfully' }; failure { echo 'Pipeline failed' } }\n}", true))
p.save()
def f = j.getItem('devops-lab1-freestyle-local') ?: j.createProject(FreeStyleProject, 'devops-lab1-freestyle-local')
f.setDescription('Local Lab 1 validation; executes app and tests from local snapshot.')
f.getBuildersList().clear()
f.getBuildersList().add(new Shell("export PATH=/opt/homebrew/bin:\$PATH\ncp \"/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/app.py\" .\ncp \"/Users/nirdeshjain/Documents/DevOps-Lab-1/Lab 1/test_app.py\" .\npython3 app.py\npython3 -m unittest test_app.py -v"))
f.save()
p.scheduleBuild2(0)
f.scheduleBuild2(0)
