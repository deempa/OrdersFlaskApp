def nextVersion
def Version

pipeline {
    agent any
    environment {
        ECR_URL = "644435390668.dkr.ecr.eu-west-2.amazonaws.com/lior-portfolio"
        IMAGE_NAME = "orders_app"
        CONTAINER_TEST_NAME = "orders_app_test"
        GIT_COMMIT_MSG = sh (script: 'git log -1 --pretty=%B ${GIT_COMMIT}', returnStdout: true).trim()
        PUBLIC_IP = sh (script: 'curl ifconfig.me', returnStdout: true).trim()
    }
    stages {
        stage("Find Last Version") {
            when {
                anyOf {
                    branch 'main'
                    branch "feature/*"
                }            
            }
            steps {
                sshagent(["flask-app"]) { 
                    script {         
                        if (env.BRANCH_NAME =~ ^feature/.*) {
                            nextVersion = "0.0.0"
                        }
                        if (env.GIT_COMMIT_MSG =~ /(\d+\.\d+)$/) {
                            println "Ok"
                        } else {
                            error('Aborting the build - No valid commit message.')
                        } 
                        sh 'git fetch --all --tags'
                        Version = (env.GIT_COMMIT_MSG  =~ /(\d+\.\d+)$/)[0][1]
                        def baseVersion = "${Version}"
                        def lastVersion = sh(script: "git tag | grep '^${baseVersion}' | sort -V | tail -n 1", returnStdout: true).trim()
                        println "Last version of ${baseVersion}: ${lastVersion}"
                        if (lastVersion == "") {
                            nextVersion = "${baseVersion}.0"
                        } else {
                            def versionParts = lastVersion.split("\\.")
                            def lastVersionNumber = Integer.parseInt(versionParts[-1])
                            nextVersion = "${baseVersion}.${lastVersionNumber + 1}"
                        }
                        println "Next version: ${nextVersion}"  
                    }
                }
            }
        }

        stage("Build") {
            when {
                anyOf {
                    branch 'main'
                    branch "feature/*"
                }            
            }
            steps {
                dir('backend') {
                    sh "docker build -t ${IMAGE_NAME}:${nextVersion} ."
                }     
            }
        }

        stage("E2E Tests") {
            when {
                anyOf {
                    branch 'main'
                    branch "feature/*"
                }            
            }
            steps {
                sh "docker compose up -d"
                sh "sleep 7"
                sh "pytest tests/e2e.py"
                sh "docker compose down" 
            }
        }

        stage("Publish") {
            when {
                branch 'main'
            }
            steps {
                sh "aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 644435390668.dkr.ecr.eu-west-2.amazonaws.com"
                sh "docker tag ${env.IMAGE_NAME}:${nextVersion} ${env.ECR_URL}:${nextVersion}"
                sh "docker push ${env.ECR_URL}:${nextVersion}" 
            }
        }

        stage('Push Tag') {
            when {
                branch 'main'
            }
            steps {
                sshagent(['flask-app'])
                {
                    script {
                        echo 'Clean and reset Stage..'
                        sh 'git restore .'
                        sh "git tag ${nextVersion}"
                        sh "git push origin ${nextVersion}"
                        echo 'Finished Clean and reset Stage..'  
                    }
                }
            }
        }

        stage('Update S3 Static') {
            when {
                branch 'main'
            }
            steps {
                sh "aws s3 sync ./backend/static/ s3://lior-porftolio-staticfiles/static"
            }
        }


        stage("Update ArgoCD") {
            when {
                branch 'main'
            }
            steps {
                dir('gitops-config') {
                    git branch: 'main', credentialsId: 'argo-jenkins', url: 'git@github.com:deempa/GitOps-Config-Portfolio.git'
                    sh """yq -i '.image.tag = "${nextVersion}"' infra-apps/ordersapp/values.yaml"""  
                    sh "git add ."
                    sh "git commit -m 'New Version By Jenkins'"
                    sshagent(['argo-jenkins']) {
                        sh "git push origin main"
                    }
                }
            }
        }
    }

    post {
        always {
            sh "docker compose down || echo 'already down'" 
            sh "docker rmi ${env.IMAGE_NAME}:${nextVersion} || echo 'None Image'"
            sh "docker rmi ${env.ECR_URL}:${nextVersion} || echo 'None Image'"
            cleanWs()
        }
        success {
            emailext body: 'The Build was Success - #$BUILD_NUMBER', recipientProviders: [culprits(), developers()], subject: 'Success Build - #$BUILD_NUMBER'
            updateGitlabCommitStatus name: 'build', state: 'success'
        }
        failure {
            emailext body: 'The Build was failed', recipientProviders: [culprits(), developers()], subject: 'Failed Build'
            updateGitlabCommitStatus name: 'build', state: 'failed'
        }
    }
}