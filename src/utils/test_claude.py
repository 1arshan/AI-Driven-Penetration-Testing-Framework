import asyncio
from claude_client import ClaudeClient

async def test_claude_integration():
    client = ClaudeClient()
    
    system_prompt = "You are a cybersecurity expert analyzing reconnaissance data."
    user_message = "Analyze this port scan result: Port 22/tcp open ssh OpenSSH 8.2"
    
    response = await client.generate_response(
        system_prompt=system_prompt,
        user_message=user_message
    )
    
    print("Claude Response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(test_claude_integration())