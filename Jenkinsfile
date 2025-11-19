pipeline {
    agent any
    
    tools {
        git 'Default'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/unixanand/cloud_based_app_support_automationTool'
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    bat 'docker build -t unix_anand/auto-app:%BUILD_NUMBER% .'
                    bat 'docker tag unix_anand/auto-app:%BUILD_NUMBER% unix_anand/auto-app:latest'
                }
            }
        }
        stage('Test Image') {
            steps {
                script {
                    bat 'docker run --rm unix_anand/auto-app:%BUILD_NUMBER% echo "App is running!"'
                }
            }
        }
        stage('Deploy Local') {  // <-- Inserted HERE, inside 'stages'
            steps {
                bat 'docker stop my-app || exit 0'  // Stop if running (ignores error if not)
                bat 'docker rm my-app || exit 0'    // Remove if exists
                bat 'docker run -d -p 8080:80 --name my-app unix_anand/auto-app:latest'
                bat 'echo "Deployed to http://localhost:8080"'
            }
        }
    }
    
    post {
        always {
            bat 'docker system prune -f'
            cleanWs()
        }
        success {
            echo 'Build succeeded! Local Docker image ready and deployed.'
        }
        failure {
            echo 'Build failed—check logs.'
        }
    }
}