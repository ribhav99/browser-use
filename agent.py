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
	task = "open discord website and summarise all the main channels conversations from the omega discord server."
	asyncio.run(main(task))
