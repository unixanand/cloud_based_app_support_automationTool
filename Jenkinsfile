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
                    bat 'docker build -t unix_anand/cloud_based_app_support_automationtool:%BUILD_NUMBER% .'
                    // Tag latest
                    bat 'docker tag unix_anand/cloud_based_app_support_automationtool:%BUILD_NUMBER% unix_anand/cloud_based_app_support_automationtool:latest'
                }
            }
        }
        stage('Test Image') {
            steps {
                script {
                    // Run a quick test (e.g., if your app exposes a port)
                    bat 'docker run --rm unix_anand/cloud_based_app_support_automationtool:%BUILD_NUMBER% echo "App is running!"'
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
               //     bat 'docker push unix_anand/cloud_based_app_support_automationtool:%BUILD_NUMBER%'
               //     bat 'docker push unix_anand/cloud_based_app_support_automationtool:latest'
               // }
           // }
       // }
    }
    stage('Deploy Local') {
		steps {
			bat 'docker stop my-app || exit 0'  // Stop if running
			bat 'docker rm my-app || exit 0'
			bat 'docker run -d -p 8080:80 --name my-app unix_anand/auto-app:latest'
			bat 'echo "Deployed to http://localhost:8080"'
		}
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