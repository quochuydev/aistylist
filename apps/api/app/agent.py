import asyncio
import json
import logging

from . import data
from .config import GEMINI_API_KEY, IMAGE_MODEL, MODEL, client
from .images import generate_image
from .tools import FUNCS, TOOLS, UI

STYLIST_PROMPT = """You are the AI Stylist orchestrator for a fashion store, coordinating these agents through tools:
- Product catalog agent: extract the relevant entities (occasion, destination, dates, style) from the prompt, search the catalog, consult fashion trends and customer reviews.
- Inventory management agent: check the customer's order history and that recommended products are in stock.
- Weather API agent: check the forecast when a place or date is mentioned.
Only recommend products returned by search_catalog that have stock > 0. Avoid products similar to ones the customer returned.
When done, reply with ONLY a JSON object:
{"summary": "2-3 sentences addressing the customer", "looks": [{"name": "...", "description": "why this works", "product_ids": ["p01", "..."]}]}
Give 2-3 looks of 3-5 products each."""

IMAGE_PROMPT = """You are the image generation agent. For each look, write a vivid prompt for a text-to-image model
(photorealistic full-body fashion photo, describe each garment, setting, lighting). Reply with ONLY a JSON object:
{"prompts": ["prompt for look 1", "..."]}"""


ASK_PROMPT = """You are the AI Stylist. The customer is comparing these looks:
{looks}
Answer their question in 2-4 plain-text sentences. Use tools (e.g. customer reviews, inventory) when they help."""


def parse_json(text):
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    return json.loads(text)


async def run_tool(call):
    try:
        args = json.loads(call.function.arguments or "{}")
        result = await asyncio.to_thread(FUNCS[call.function.name], **args)
    except Exception as e:  # report tool errors back to the model instead of failing the run
        result = {"error": str(e)}
    return {"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)}


def event(**payload):
    return f"data: {json.dumps(payload)}\n\n"


async def run_agent(messages):
    """Tool loop; yields a step event per tool call. The final answer is left in messages[-1]."""
    for _ in range(8):  # ponytail: hard cap on agent turns, keeps a confused model from looping forever
        msg = (await client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)).choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        if not msg.tool_calls:
            return
        for call in msg.tool_calls:
            agent, kb = UI.get(call.function.name, (None, None))
            yield event(type="step", agent=agent, kb=kb, label=f"{call.function.name}({call.function.arguments})")
        messages += await asyncio.gather(*map(run_tool, msg.tool_calls))
    raise RuntimeError("agent did not finish")


async def stylist(prompt: str):
    messages = [{"role": "system", "content": STYLIST_PROMPT}, {"role": "user", "content": prompt}]
    try:
        async for step in run_agent(messages):
            yield step

        result = parse_json(messages[-1]["content"])
        products = {p["id"]: p for p in data.PRODUCTS}
        looks = [
            {**look, "products": [products[i] for i in look.get("product_ids", []) if i in products]}
            for look in result.get("looks", [])
        ]

        yield event(type="step", agent="image", kb=None, label="writing image prompts")
        resp = await client.chat.completions.create(
            model=MODEL, response_format={"type": "json_object"},
            messages=[{"role": "system", "content": IMAGE_PROMPT}, {"role": "user", "content": json.dumps(looks)}],
        )
        for look, image_prompt in zip(looks, parse_json(resp.choices[0].message.content).get("prompts", [])):
            look["image_prompt"] = image_prompt

        if GEMINI_API_KEY:
            yield event(type="step", agent="image", kb="catalog", label=f"generating images ({IMAGE_MODEL})")
            images = await asyncio.gather(*(asyncio.to_thread(generate_image, l["image_prompt"]) for l in looks if "image_prompt" in l))
            for look, image in zip([l for l in looks if "image_prompt" in l], images):
                look["image"] = image

        yield event(type="looks", summary=result.get("summary", ""), looks=looks)
    except Exception:
        logging.exception("stylist run failed")
        yield event(type="error", message="The stylist failed to generate looks. Please try again.")
    yield event(type="done")


async def ask(question: str, looks: list):
    looks = [{k: v for k, v in l.items() if k != "image"} for l in looks if isinstance(l, dict)]  # drop image bytes
    messages = [
        {"role": "system", "content": ASK_PROMPT.format(looks=json.dumps(looks))},
        {"role": "user", "content": question},
    ]
    try:
        async for _ in run_agent(messages):
            pass
    except Exception:
        logging.exception("ask failed")
        return {"error": "The stylist could not answer. Please try again."}
    return {"answer": messages[-1]["content"]}
