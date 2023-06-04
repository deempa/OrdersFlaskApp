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
        NETWORK_NAME = "lab_default"
    }
    stages {
        stage("Find Last Version") {
            when {
                branch 'main'
            }
            steps {
                sshagent(["flask-app"]) { 
                    script {            
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
                branch 'main'
            }
            steps {
                dir('backend') {
                    sh "docker build -t ${IMAGE_NAME}:${nextVersion} ."
                }
                
            }
        }

        stage("E2E Tests") {
            steps {
                sh "docker compose up -d"
                // sh "sleep 20"
                // sh "curl -I http://${PUBLIC_IP}:8087/health"
                sh '''#!/bin/sh
                    for (( i=0; i <= 15; ++i ))
                    do
                        response_code=$(curl -s -o /dev/null -w "%{http_code}" "http://${PUBLIC_IP}:8087/health")
                        if [ "$response_code" -eq 200 ]; then
                            echo "Ping successful!"
                            break
                        fi
                    done

                '''
                sh "docker compose down -v"
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

        stage('Clean and reset') {
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
    }

    post {
        always {
            cleanWs()
            echo "========pipeline executed successfully ========"
        }
        success {
            echo "========pipeline executed successfully ========"
        }
        failure {
            echo "========pipeline execution failed========"
        }
    }
}