def nextVersion
def Version

pipeline {
    agent any
    environment {
        ECR_URL = "644435390668.dkr.ecr.eu-west-2.amazonaws.com/lior-portfolio"
        IMAGE_NAME = "orders_app"
        CONTAINER_TEST_NAME = "orders_app_test"
        GIT_COMMIT_MSG = sh (script: 'git log -1 --pretty=%B ${GIT_COMMIT}', returnStdout: true).trim()
    }
    stages {
        stage("Find Last Version") {
            when {
                expression { return env.GIT_BRANCH == 'main' }
            }
            steps {
                sshagent(['flask-app']) {
                    script { 
                        println "${env.GIT_COMMIT_MSG}"
                        sh 'git fetch --all --tags'
                        // Version = (env.GIT_BRANCH  =~ /(\d+\.\d+)$/)[0][1]
                        Version = (env.GIT_COMMIT_MSG =~ /\d+\.\d+\/)[0][1]
                        println "Next version: ${Version}" 
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
                expression { return env.GIT_BRANCH =~ """/^feature\/.*$/""" || env.GIT_BRANCH == 'main' }
            }
            steps {
                sh "docker build -t ${IMAGE_NAME}:${nextVersion}"
            }
        }

        stage("Unit Tests") {
            when {
                expression { return env.GIT_BRANCH =~ /^feature\/.*$/ || env.GIT_BRANCH == 'main' }
            }
            steps {
                sh "docker run -d --rm -p 5000:5000 --name ${CONTAINER_TEST_NAME} ${IMAGE_NAME}:${nextVersion}"

            }
        }

        stage("E2E Tests") {
            when {
                expression { return env.GIT_BRANCH =~ /^feature\/.*$/ || env.GIT_BRANCH == 'main' }
            }
            steps {
                sh "docker compose up -d"
                sh "curl -I http://localhost:5000/health"
                sh "docker compose down -v"
            }
        }

        stage("Publish") {
            when {
                expression { return env.GIT_BRANCH == 'main' }
            }
            steps {
                sh "aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 644435390668.dkr.ecr.eu-west-2.amazonaws.com"
                sh "docker tag ${env.IMAGE_NAME}:${nextVersion} ${env.ECR_URL}:${nextVersion}"
                sh "docker push ${env.ECR_URL}:${nextVersion}"
            }
        }
    }

    post {
        always {
            echo "========always========"
        }
        success {
            echo "========pipeline executed successfully ========"
        }
        failure {
            echo "========pipeline execution failed========"
        }
    }
}