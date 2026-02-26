import os
import re
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# LLM imports
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

# Local tools
from tools.search import combined_web_search
from tools.writer import write_markdown_artifact

load_dotenv()

# Constants
CLAUDE_MD_PATH = Path("/Users/talli/platform-research/CLAUDE.md")

def extract_research_domains() -> List[str]:
    """Parses CLAUDE.md to extract the bulleted list under 'Research Domains'."""
    if not CLAUDE_MD_PATH.exists():
        print(f"Error: {CLAUDE_MD_PATH} not found.")
        return []
        
    content = CLAUDE_MD_PATH.read_text()
    
    # Simple regex to capture the bulleted list under Research Domains
    match = re.search(r"## Research Domains.*?\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if not match:
        print("Could not find 'Research Domains' section.")
        return []
        
    domains_text = match.group(1).strip()
    domains = []
    
    for line in domains_text.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            domains.append(line[2:])
            
    return domains

def setup_agent():
    """Sets up the LangChain ReAct agent with the combined search tool."""
    # Preferred model is Anthropic Claude if available, else Gemini
    if os.getenv("ANTHROPIC_API_KEY"):
        llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.2)
    elif os.getenv("GOOGLE_API_KEY"):
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)
    else:
        raise ValueError("Please set either ANTHROPIC_API_KEY or GOOGLE_API_KEY in your .env file.")
    
    tools = [combined_web_search]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert autonomous research agent for a hyper-multiplexed single-molecule detection platform.
You are tasked with researching specific domains regarding DNA origami, EO-FLIM, ATTO dyes, SMILES nanoparticles, and immunopeptidomics.

Instructions:
1. Use the `combined_web_search` tool to look for recent scientific literature, company announcements, patents, or competitor information.
2. Read the search snippets carefully.
3. Synthesize the information into a comprehensive, highly-technical summary markdown response.
4. Keep track of all the sources, links, and documents you find.
5. In your final response, provide three distinct sections separated by exactly '===CUT===':
   
   [Findings Content]
   ===CUT===
   [Sources/Bibliography Content]
   ===CUT===
   [Summary/Comparison Content]

Ensure your output strictly follows this three-part structure so it can be parsed and written to the correct directories."""),
        ("human", "Research the following domain thoroughly: {input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

def run_research_pipeline():
    """Main execution loop for iterating over domains and saving research artifacts."""
    domains = extract_research_domains()
    if not domains:
        print("No domains found to research. Exiting.")
        return
        
    print(f"Found {len(domains)} research domains. Initializing agent...")
    agent = setup_agent()
    
    for domain in domains:
        print(f"\\n{'='*50}")
        print(f"Starting research on: {domain}")
        print(f"{'='*50}\\n")
        
        try:
            result = agent.invoke({"input": domain})
            output_text = result.get("output", "")
            
            parts = output_text.split("===CUT===")
            if len(parts) == 3:
                findings_content = parts[0].strip()
                sources_content = parts[1].strip()
                summary_content = parts[2].strip()
                
                # Write to disk
                slug_name = re.sub(r"[^a-zA-Z0-9]+", "-", domain[:30].lower())
                
                f_path = write_markdown_artifact("findings", slug_name, findings_content)
                s_path = write_markdown_artifact("sources", slug_name, sources_content)
                sum_path = write_markdown_artifact("summaries", slug_name, summary_content)
                
                print(f"\\n✅ Successfully saved research for '{domain}'")
                print(f"  - {f_path}")
                print(f"  - {s_path}")
                print(f"  - {sum_path}")
                
            else:
                print(f"Warning: Agent output for '{domain}' did not follow the ===CUT=== format. Saving raw output to findings.")
                # Fallback format handling
                write_markdown_artifact("findings", slug_name, output_text)
                
        except Exception as e:
            print(f"\\n❌ Error researching '{domain}': {e}")
            
if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("Warning: Neither ANTHROPIC_API_KEY nor GOOGLE_API_KEY environment variables are set.")
    
    run_research_pipeline()
