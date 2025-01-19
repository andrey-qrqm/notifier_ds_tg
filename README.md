# notifier_ds_tg
Script for sending updates and notifications from discord channel to telegram channel

Firstly, I'm glad to announce, that this Application is currently app in WWW and ready to use. 
I've used it to track activity on my friend's Discord Guild for a couple of weeks, and it's working.
If you want to test it yourself I welcome you to test it with the command to my telegram bot: /add_channel 'Тестобот' or
/add_channel 'Лигушатник'. With this commands Telegram Bot will notify you when somebody is joining/leaving
any voice rooms in these channels.


What actions can it do?

1) In your Telegram App, find my Bot @NotifierFrogsBot ; Start a chat with Bot or add it in already existing chat
2) In your Discord Guild add the bot via link: https://discord.com/oauth2/authorize?client_id=1283029091993518110
3) Now you can set up notifications from Discord Guild into your telegram chat:
4) In Telegram chat with NotifierFrogsBot /add_channel NAME_OF_GUILD - all connections and disconnections to the voice channels will be tracking from this Guild
5) /remove_channel - remove Guild from tracking
6) You can add multiple guilds to track in one chat
7) One guild can be tracked in multiple Telegram channels

CREATE .env

TOKEN_TG = "YOUR TELEGRAM BOT TOKEN"

TOKEN = "YOUR DISCORD BOT TOKEN"

DATABASE_PW = "Your database password"

PORT = "port"

The bot is running on remote server, using AWS EC2


SRH Software Engineering (part for Prof. Edlich)

Requirements, pdf exported from Notion [Requirements](./.github/src/list_of_reqs.pdf)

Diagram of workflow [Workflow](.github/src/Diagram_of_app_relationships.pdf
)

Diagram of Domains [Domain Chart](.github/src/Diagram_DDD_Domain_chart.pdf)

Diagram of CORE [CORE](.github/src/CORE.pdf)

ANA - Analysis [ANA](https://docs.google.com/document/d/1akZDDUQj42m6rsIwgWtXcwa8Xqfb6b6WYqKlHNzBW2w/edit?usp=sharing)

Refactoring example 1:

Delete the else after return and de-indent the code, the logic has not changed, but the time to exec is less now

[Example](https://github.com/andrey-qrqm/notifier_ds_tg/commit/c5fa62ec4a5325bb89cf0a5e4ff52104d6520ed4)

Refactoring example 2:

I've got rid of unnecessary connection set-ups and set-downs. Rewrote as a function and dependencies to better mock-up ability

[Example](https://github.com/andrey-qrqm/notifier_ds_tg/commit/4e69e2d704ea4dc804c0a612ab258b204da4f490)

Build Management:

The app is build using docker-compose as an orchestrator of multiple docker containers.
The Docker compose approach was chosen because this is a multi-container application with the need to define
Network and Volumes. Also it helps with further automatization.

[docker-compose.yml](https://github.com/andrey-qrqm/notifier_ds_tg/blob/main/docker-compose.yml)

CI/CD:

I'm using the GitHub Actions Pipeline to automate Docker image build and push to the Docker Hub

[docker-build-push.yml](https://github.com/andrey-qrqm/notifier_ds_tg/blob/main/.github/workflows/docker-build-push.yml)

Unit Tests:

Unit Tests are made onto two main application (Discord Webhook Server + Bot, and Telegram Webhook Server + Bot)
Tests are made using pytest and unittest.mock

[Notifier Discord Tests](https://github.com/andrey-qrqm/notifier_ds_tg/blob/main/test_notifier_ds.py)
[Notifier Telegram Tests](https://github.com/andrey-qrqm/notifier_ds_tg/blob/main/test_notifier_tg.py)

IDE used: PyCharm Community Edition 

Favorite Short-Cuts:

CTRL + SHIFT + UP (Down) - moving the lines or whole functions through code

CTRL + ALT + M - Extract Method


METRICS

To check code-quality metrics I used the External Tool Pylint (The average rating of code is 7.0)\

To check health of the app I've created personal metrics of delays between event and notification

I've created a second PostgreSQL Table to write in records of timings. Then I'm using Prometheus and Grafana to 
analyze these metrics.

[Metrics.py](https://github.com/andrey-qrqm/notifier_ds_tg/blob/main/metrics.py)
[prometheus.yml](https://github.com/andrey-qrqm/notifier_ds_tg/blob/main/prometheus.yml)



