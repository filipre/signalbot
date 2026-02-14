# Examples

The code shown here can be found the [example folder](https://github.com/signalbot-org/signalbot/tree/main/example).

## Bot with several commands

This bot showcases how to use most of the features in the library.
Check the [commands section](#commands) to see the implementation of each command.

``` python
--8<-- "example/bot.py"
```

### Commands

<details><summary>AttachmentCommand</summary>
``` python
--8<-- "example/commands/attachments.py"
```
</details>


<details><summary>DeleteCommand & DeleteLocalAttachmentCommand & ReceiveDeleteCommand</summary>
``` python
--8<-- "example/commands/delete.py"
```
</details>


<details><summary>EditCommand</summary>
``` python
--8<-- "example/commands/edit.py"
```
</details>


<details><summary>HelpCommand</summary>
``` python
--8<-- "example/commands/help.py"
```
</details>


<details><summary>TriggeredCommand</summary>
``` python
--8<-- "example/commands/multiple_triggered.py"
```
</details>


<details><summary>PingCommand</summary>
``` python
--8<-- "example/commands/ping.py"
```
</details>


<details><summary>RegexTriggeredCommand</summary>
``` python
--8<-- "example/commands/regex_triggered.py"
```
</details>


<details><summary>ReplyCommand</summary>
``` python
--8<-- "example/commands/reply.py"
```
</details>


<details><summary>StylesCommand</summary>
``` python
--8<-- "example/commands/styles.py"
```
</details>


<details><summary>TypingCommand</summary>
``` python
--8<-- "example/commands/typing.py"
```
</details>


## Bot with scheduler

This bot showcases how to use the scheduler and also how to use the library without using the `Command` class.
``` python
--8<-- "example/bot_with_scheduler.py"
```
