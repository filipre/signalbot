# Signal Bot Framework

Todo

## Todos

- [x] Create dummy project
- [ ] Add real code
- [ ] Think about the license again
- [ ] Github actions to test and publish on release  
- [ ] Example bot & commands
- [ ] PR to API project

## Deprecated

Micro framework to create your own signal bots. Just fork this repository and extend it with your commands. The API builds on top of https://github.com/bbernhard/signal-cli-rest-api which provides a Websocket/REST API for https://github.com/AsamK/signal-cli.

## How to run the bot
1. Follow the instructions in `bot.py`
2. `docker-compose up`

Currently, the bot can only listen in groups and not direct messages. You can create a group with yourself and use the bot there.

## How to implement a new command

1. Create a new file in the `commands` folder
2. Inherit from `Command` and implement `handle` to react on incomming messages
3. Optionally, overwrite `init` to schedule tasks or to perform tasks before listening for messages