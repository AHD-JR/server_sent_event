from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import StreamingResponse
import openai
import os
from fastapi.middleware.cors import CORSMiddleware
import asyncio


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY") 

# Generator function to fetch and yield response chunks from ChatGPT
async def stream_chatgpt_response(prompt: str):
    try:

        # OpenAI Chat Completion API call with streaming
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=True  # Enables streaming mode
        )

        # Yield each part of the response as it comes in
        for chunk in response:
            # Extract the text content from the response chunk
            if 'choices' in chunk and len(chunk['choices']) > 0:
                # Format each chunk according to the SSE protocol with 'data:' and '\n\n'
                yield f"data: {chunk['choices'][0]['delta'].get('content', '')}\n\n"

    except Exception as e:
        # Handle any other errors that might occur
        yield f"data: Error: {str(e)}\n\n"


# Endpoint to handle incoming prompt and start streaming response
@app.post("/chat")
async def chat_with_gpt(request: Request, prompt: str = Form(...)):
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    async def event_generator():
        try:
            # Loop through each chunk, checking if the client is still connected
            async for response_chunk in stream_chatgpt_response(prompt):
                if await request.is_disconnected():
                    break
                yield response_chunk  # Yield each chunk as it comes in

        except Exception as e:
            yield f"data: Error occurred while streaming: {str(e)}\n\n" 

    # StreamingResponse with "text/event-stream" to signal SSE
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ######################Test server side streaming######################
async def event_generator():
    # Simulate real-time data updates
    count = 0
    while True:
        # Yield an event in SSE format
        yield f"data: Event number {count}\n\n"
        count += 1
        # Wait for 1 second between updates
        await asyncio.sleep(1)

# Route for SSE endpoint
@app.get("/stream")
async def sse_endpoint():
    return StreamingResponse(event_generator(), media_type="text/event-stream")
