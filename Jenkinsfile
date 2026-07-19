pipeline {
    agent any

    options {
        skipDefaultCheckout(false)
        timestamps()
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Frontend build') {
            steps {
                dir('frontend') {
                    bat 'npm ci'
                    bat 'npm run build'
                }
            }
        }

        stage('Backend validation') {
            steps {
                dir('backend') {
                    bat 'python -m venv .ci-venv'
                    bat '.ci-venv\\Scripts\\python.exe -m pip install -r requirements.txt'
                    bat '.ci-venv\\Scripts\\python.exe -c "from app.main import app; print(\"FastAPI import passed\")"'
                }
            }
        }

        stage('Deploy production') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([
                    string(credentialsId: 'render-deploy-hook', variable: 'RENDER_DEPLOY_HOOK'),
                    string(credentialsId: 'vercel-deploy-hook', variable: 'VERCEL_DEPLOY_HOOK')
                ]) {
                    powershell 'Invoke-WebRequest -Method POST -Uri $env:RENDER_DEPLOY_HOOK -UseBasicParsing'
                    powershell 'Invoke-WebRequest -Method POST -Uri $env:VERCEL_DEPLOY_HOOK -UseBasicParsing'
                }
            }
        }
    }

    post {
        always {
            dir('backend') {
                bat 'if exist .ci-venv rmdir /s /q .ci-venv'
            }
        }
    }
}
