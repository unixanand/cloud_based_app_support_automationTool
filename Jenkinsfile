pipeline {
    agent any  // Uses your local Jenkins agent (Windows machine)
    
    tools {
        git 'Default'  // Uses installed Git
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
                    // Build from Dockerfile in repo root
                    bat 'docker build -t unix_anand/Auto-app:${BUILD_NUMBER} .'
                    // Tag latest
                    bat 'docker tag unix_anand/Auto-app:${BUILD_NUMBER} unix_anand/Auto-app:latest'
                }
            }
        }
        stage('Test Image') {
            steps {
                script {
                    // Run a quick test (e.g., if your app exposes a port)
                    bat 'docker run --rm unix_anand/Auto-app:${BUILD_NUMBER} echo "App is running!"'
                }
            }
        }
        //stage('Push to Registry') {  // Optional: Push to Docker Hub
           // when {
             //   branch 'main'  // Only on main branch
           // }
           // steps {
            //    script {
                    // Login (use Jenkins credentials ID)
              //      withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
               //         bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
               //     }
                    // Push
               //     bat 'docker push unix_anand/Auto-app:${BUILD_NUMBER}'
               //     bat 'docker push unix_anand/Auto-app:latest'
               // }
           // }
       // }
    }
    
    post {
        always {
            bat 'docker system prune -f'  // Clean up dangling images
            cleanWs()  // Clean workspace
        }
        success {
            echo 'Build succeeded! Your Docker image is ready.'
        }
        failure {
            echo 'Build failed—check logs.'
        }
    }
}