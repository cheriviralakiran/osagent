import os
import subprocess
from langchain_groq import ChatGroq
os.environ["GROQ_API_KEY"] = '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'
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model="llama3-8b-8192")

from langchain_core.tools import tool

@tool
def execute_command(command):
    """
    Executes the given command inside shell on a machine.
    After executing command, returns first argument as True or False to indicate success or failure.
    Returns second argument with output of the command.

    command: Command to be executed
    """
    try:
        print("Command to be execute is " + command)
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        if process.returncode == 0:
            return True, process.stdout
        else:
            return False, process.stderr
    except Exception as e:
        return False, str(e)

tools = [execute_command]
llm_with_tools = llm.bind_tools(tools)

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
#print(llm_with_tools.invoke(user_prompt))

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

available_tools = {
    "execute_command": execute_command,
}

while True:
    user_prompt = input("What do you want to you about the OS: ") or "Which process is listening port 56036 on my machine? The operating system is macos. First get the command from the prompt and then use execute_command tool for executing the command"
    #print(user_prompt)
    if user_prompt.lower() in ["quit", "exit"]:
        print("Thank You for using our tool.")
        break
    else:
        SYSTEM_MESSAGE = "You are os agent with support of llm. You get command first and then execute command using tools on user machine"
        messages = [SystemMessage(SYSTEM_MESSAGE), HumanMessage(user_prompt)]
        tool_call_identified = True
        while tool_call_identified:
            #print(messages)
            print("Invoking groq")
            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)
            for tool_call in ai_msg.tool_calls:
                print("Executing tool")
                selected_tool = available_tools[tool_call["name"]]
                tool_output = selected_tool.invoke(tool_call["args"])
                #print(tool_output)
                message = ToolMessage(tool_output[1], tool_call_id=tool_call["id"])
                #print(message)
                messages.append(message)
            if len(ai_msg.tool_calls) == 0:
                tool_call_identified = False

        print(ai_msg.content)