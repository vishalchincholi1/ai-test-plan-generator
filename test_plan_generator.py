import os
import argparse
from typing import Dict, Optional

# Placeholder for LLM client. 
# You can use OpenAI, Anthropic, or any other client compatible with your environment.
# For this example, we'll structure it to be easily pluggable.
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class TestPlanAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.system_prompt_path = "system_prompt.md"
        self.guard_path = "anti_Hallucination_Guard.md"
        self.client = OpenAI(api_key=api_key) if OpenAI and api_key else None
        
        # Load prompt components
        self.system_persona = self._load_file(self.system_prompt_path)
        self.security_guard = self._load_file(self.guard_path)

    def _load_file(self, filepath: str) -> str:
        """Loads content from a file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
            return ""

    def construct_system_message(self) -> str:
        """Combines System Persona and Anti-Hallucination Guard."""
        return f"{self.system_persona}\n\n{self.security_guard}"

    def construct_user_message(self, context: Dict[str, str]) -> str:
        """
        Constructs the user message using the 'RICE POT' structure 
        defined in ai_testPlanning.md.
        """
        rice_pot_template = f"""
Role: Senior QA Lead with expertise in test planning

Intent: Generate a comprehensive test plan for the given application.

Context:
- Project: {context.get('project_name', 'N/A')}
- Application Type: {context.get('app_type', 'N/A')}
- Features in Scope: {context.get('features', 'N/A')}
- Tech Stack: {context.get('tech_stack', 'N/A')}
- Team Size: {context.get('team_size', 'N/A')}
- Timeline: {context.get('timeline', 'N/A')}
- Environment: {context.get('environment', 'N/A')}

Parameters:
- Follow IEEE 829 standard structure.
- Include risk assessment.
- Cover functional and non-functional testing.
- Add entry/exit criteria.
- Define test levels.

Output Format (STRICT as per Anti-Hallucination Guard):
- Verified Facts
- Missing / Unknown Information
- Generated Output (The Test Plan Markdown)
- Self-Validation Check

Task: Generate the complete test plan now.
"""
        return rice_pot_template

    def generate_test_plan(self, context: Dict[str, str]) -> str:
        """Orchestrates the prompt generation and LLM call."""
        system_msg = self.construct_system_message()
        user_msg = self.construct_user_message(context)

        print("\n--- Constructed System Prompt ---")
        print(system_msg[:500] + "...\n(truncated)")
        
        print("\n--- Constructed User Query ---")
        print(user_msg)

        if not self.client:
            return "\n[Logic Validation Mode] LLM Client not initialized. Please provide an API Key to generate real output."

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # or your preferred model
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.2  # Low temperature for deterministic output as requested
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error during generation: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="AI Test Plan Generator Agent")
    parser.add_argument("--project", help="Project Name", required=True)
    parser.add_argument("--type", help="Application Type (Web/Mobile/API)", required=True)
    parser.add_argument("--features", help="Comma-separated features", required=True)
    parser.add_argument("--tech", help="Tech Stack", required=True)
    parser.add_argument("--team", help="Team Size", required=True)
    parser.add_argument("--time", help="Timeline", required=True)
    parser.add_argument("--env", help="Environment (e.g., Staging)", default="Staging")
    parser.add_argument("--api_key", help="LLM API Key", required=False)

    args = parser.parse_args()

    # Collect context
    context = {
        "project_name": args.project,
        "app_type": args.type,
        "features": args.features,
        "tech_stack": args.tech,
        "team_size": args.team,
        "timeline": args.time,
        "environment": args.env
    }

    # Initialize Agent
    # Note: In a real scenario, use os.environ.get("OPENAI_API_KEY") or similar
    agent = TestPlanAgent(api_key=args.api_key or os.environ.get("OPENAI_API_KEY"))
    
    # Generate
    result = agent.generate_test_plan(context)
    
    print("\n\n" + "="*30 + " AGENT OUTPUT " + "="*30)
    print(result)

if __name__ == "__main__":
    main()
