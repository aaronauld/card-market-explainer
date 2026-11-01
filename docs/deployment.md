# Deployment

The service runs privately on one AWS EC2 server (`t4g.small`, Ubuntu 24.04 on Arm, us-east-1) with Docker Compose. The firewall allows only SSH from one IP address. The API listens on the server's localhost and is reached through an SSH tunnel. It's private because the price data's licence text hasn't arrived (see `data-notes.md`).

Secrets live only in `~/app/.env` on the server (mode 600). The SSH key stays outside this repo.

## Stop the server

EC2 console → Instances → select the instance → **Instance state → Stop instance**.

Never choose **Terminate**: that deletes the server and its data. While stopped, only the disk is billed, and the data is kept.

## Start the server

1. EC2 console → select the instance → **Instance state → Start instance**. Wait for **Running**.
2. Copy the new **Public IPv4 address**. It changes on every start.
3. If your home IP changed, update the SSH rule: the instance's **Security** tab → security group → **Edit inbound rules** → source **My IP**.
4. Connect and start the containers, which don't restart on their own:

   ```bash
   ssh -i C:\Users\aaron\.ssh\RSA.pem ubuntu@NEW_IP
   ```

   ```bash
   cd ~/app && docker compose up -d
   ```

5. Open the tunnel in a new PowerShell window and leave it running:

   ```bash
   ssh -i C:\Users\aaron\.ssh\RSA.pem -L 8001:127.0.0.1:8000 ubuntu@NEW_IP
   ```

6. Open `http://127.0.0.1:8001/docs` and click **Authorize**.

The daily spending limit is held in memory and resets when the API restarts.

## Update the code

Run on your machine, from the project folder:

```bash
git archive -o C:\Users\aaron\deploy.tar HEAD
```

```bash
scp -i C:\Users\aaron\.ssh\RSA.pem C:\Users\aaron\deploy.tar ubuntu@NEW_IP:~
```

Then on the server:

```bash
tar -xf ~/deploy.tar -C ~/app && rm ~/deploy.tar && cd ~/app && docker compose up --build -d
```
