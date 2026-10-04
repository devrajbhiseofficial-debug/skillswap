# Deploy SkillSwap Campus on AWS (EC2 + Docker + GitHub Actions)
1. Push this folder to a GitHub repo (branch `main`).
2. AWS Console > EC2 > Launch instance: Amazon Linux 2023, t3.micro/t2.micro, create key pair (.pem).
   Security group inbound: SSH(22) from My IP, HTTP(80) from anywhere.
3. SSH in:  ssh -i key.pem ec2-user@<EC2_PUBLIC_IP>
4. Install tools:
   sudo dnf install -y docker git && sudo systemctl enable --now docker && sudo usermod -aG docker ec2-user
   sudo mkdir -p /usr/local/lib/docker/cli-plugins
   sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
   sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose ; exit  (log in again)
5. git clone <your-repo-url> ~/skillswap && cd ~/skillswap
   export SECRET_KEY=$(openssl rand -hex 16) DB_PASSWORD=<strong-pass>   # or put in a .env file
   docker compose up -d --build
6. Open http://<EC2_PUBLIC_IP> . Health check: /health
7. CI/CD: GitHub repo > Settings > Secrets > Actions: EC2_HOST (public IP), EC2_SSH_KEY (full .pem contents).
   Every push to main runs tests then redeploys automatically.
Upgrades for marks: RDS PostgreSQL, ECR + ECS/Fargate, ALB + HTTPS (ACM), Terraform, CloudWatch alarms.

## AI quiz, video room and HTTPS (added in v4)
- AI understanding quiz: create ~/skillswap/.env on the server with GEMINI_API_KEY=... (free key from aistudio.google.com)
  or ANTHROPIC_API_KEY=... . Without a key the app uses its built-in question bank, so it never breaks.
- Camera and microphone only work on HTTPS (or localhost). To get HTTPS on EC2:
  1. Get a free domain (e.g. DuckDNS) pointing to the EC2 public IP. Open ports 80 and 443 in the security group.
  2. In ~/skillswap/.env add:  DOMAIN=yourname.duckdns.org   and   WEB_PORT=8000
  3. Run:  docker compose --profile https up -d --build
- Video uses WebRTC with Google STUN. For strict college/mobile networks add a TURN server (coturn) and set TURN_URL, TURN_USER, TURN_PASS in .env.
