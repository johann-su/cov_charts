# Covid-19 Chart Bot

<img src="https://user-images.githubusercontent.com/48410810/110496812-2a01c000-80f6-11eb-9e89-902a5072e096.png" alt="drawing" style="width:128px;"/>

This is a Telegram Bot that sends you Charts with the cases and incidence in your region.
https://t.me/CovGermanyBot

## Data
The data used for this bot comes from the [Robert Koch Institute](https://www.rki.de/EN/Home/homepage_node.html) and can be seen and downloaded [here](https://npgeo-corona-npgeo-de.hub.arcgis.com).

## Setup
**Step 1:**
create a .env file and enter the following tokens:
`TELEGRAM_TOKEN` (Telegram api key - can be obtained from botfather in telegram)
`TWITTER_KEY` (twitter api key - can be obtained [here](https://developer.twitter.com/en/products/twitter-api))
`TWITTER_SECRET` (twitter api secret)
`TWITTER_AT` (twitter authentication token)
`TWITTER_ATS` (twitter authentication token secret)

**Step 2:**
run `docker build -t corona-charts .`
`docker run --env-file .env -d corona-charts`