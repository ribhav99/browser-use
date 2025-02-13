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
		planner_llm=ChatOpenAI(model='o3-mini'),
		browser=browser
	)

	await agent.run()
	await browser.close()


if __name__ == '__main__':
	task = "Open X and summarise the top 10 tweets in great detail."
	asyncio.run(main(task))
