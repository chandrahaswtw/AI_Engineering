import json
from ai_engineering.utils.scraping import get_subroutes, scrape_content
import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


def get_client() -> OpenAI:
    # Checked at call time (not import time) so load_dotenv() in main.py has run.
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    return OpenAI()


def fetch_all_links(url: str):
    return get_subroutes(url)


def get_all_content_from_links(urls: list[str]) -> str:
    contents = [scrape_content(url) for url in urls]
    return "\n\n".join(contents)


def get_relevant_links_from_LLM(url: str, all_links: list[str]):

    link_system_prompt = """
    You are provided with a list of links found on a webpage.
    You are able to decide which of the links would be most relevant to include in a brochure about the company,
    such as links to an About page, or a Company page, or Careers/Jobs pages.
    You should respond in JSON as in this example:

    {
        "links": [
            {"type": "about page", "url": "https://full.url/goes/here/about"},
            {"type": "careers page", "url": "https://another.full.url/careers"}
        ]
    }
    """

    link_user_prompt = f"""
    Here is the list of links on the website {url} -
    Please decide which of these are relevant web links for a brochure about the company, 
    respond with the full https URL in JSON format.
    Do not include Terms of Service, Privacy, email links.

    Links (some might be relative links):

    """

    link_user_prompt += "\n".join(all_links)

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": link_system_prompt},
        {
            "role": "user",
            "content": link_user_prompt,
        },
    ]

    response = get_client().chat.completions.create(
        model="gpt-6-luna", messages=messages, response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content

    return json.loads(content)


def create_brouchere_using_LLM(company_name, content, stream: bool = False):

    brochure_system_prompt = """
    You are an assistant that analyzes the contents of several relevant pages from a company website
    and creates a short brochure about the company for prospective customers, investors and recruits.
    Respond in markdown without code blocks.
    Include details of company culture, customers and careers/jobs if you have the information.
    """

    brouchere_user_prompt = f"""
    You are looking at a company called: {company_name}
    Here are the contents of its landing page and other relevant pages;
    use this information to build a short brochure of the company in markdown without code blocks.\n\n
    """

    brouchere_user_prompt += content

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": brochure_system_prompt},
        {
            "role": "user",
            "content": brouchere_user_prompt,
        },
    ]

    if stream:
        # Print tokens as they arrive and also return the full text.
        chunks = get_client().chat.completions.create(
            model="gpt-6-luna", messages=messages, stream=True
        )
        parts: list[str] = []
        for chunk in chunks:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
                parts.append(delta)
        print()
        return "".join(parts)

    response = get_client().chat.completions.create(
        model="gpt-6-luna", messages=messages
    )

    content = response.choices[0].message.content

    return content


def create_brouchre(company_name: str, url: str):

    # STEP 1 - Get all underlying urls.
    all_links = fetch_all_links(url)

    # STEP 2 - LLM call to filter out the relevant links from all the links.
    selected_links = get_relevant_links_from_LLM(url, all_links)

    # STEP 3 - Scrape all data from the urls
    content_from_links = get_all_content_from_links(all_links)

    # STEP 4 - Create brouchere
    brouchere = create_brouchere_using_LLM(
        company_name, content_from_links, stream=True
    )

    return brouchere
