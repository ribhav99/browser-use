import os
import sys
from pathlib import Path

from browser_use.agent.views import ActionResult
import asyncio

from langchain_openai import ChatOpenAI

from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig

browser = Browser(
	config=BrowserConfig(
		# NOTE: you need to close your chrome browser - so that this can open your browser in debug mode
		chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
	)
)


async def main(task):
	agent = Agent(
		task=task,
		llm=ChatOpenAI(model='gpt-4o'),
		browser=browser
	)

	await agent.run()
	await browser.close()


if __name__ == '__main__':
	task = "Open discord and scroll through the announcements channel on the bittensor server. Then summarise announcements from the past week and send this summary in the general channel of the omega labs discord server. Be sure not to get confused between what a server, channel or chat is."
	asyncio.run(main(task))
