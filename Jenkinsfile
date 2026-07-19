pipeline {
    agent any

    options {
        skipDefaultCheckout(false)
        timestamps()
    }

    stages {
        stage('Frontend build') {
            steps {
                dir('frontend') {
                    sh 'npm ci'
                    sh 'npm run build'
                }
            }
        }

        stage('Backend validation') {
            steps {
                dir('backend') {
                    sh 'python3 -m venv .ci-venv'
                    sh '.ci-venv/bin/pip install -r requirements.txt'
                    sh '.ci-venv/bin/python -c "from app.main import app; print(\"FastAPI import passed\")"'
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
                    sh 'curl --fail --silent --show-error -X POST "$RENDER_DEPLOY_HOOK"'
                    sh 'curl --fail --silent --show-error -X POST "$VERCEL_DEPLOY_HOOK"'
                }
            }
        }
    }

    post {
        always {
            dir('backend') {
                sh 'rm -rf .ci-venv'
            }
        }
    }
}
