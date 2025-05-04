import os
import yaml
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from typing import Dict, Any, List
from pathlib import Path

from app.agents.topic_analysis import TopicAnalysisAgent
from app.agents.category_breakdown import CategoryBreakdownAgent
from app.agents.iterative_refinement import IterativeRefinementAgent
from app.agents.research_integration import ResearchIntegrationAgent
from app.services.lmstudio import LMStudioService
from app.models.prompt import PromptRequest

class PromptEnhancerCrew(CrewBase):
    """CrewAI orchestration for the Prompt Enhancer System"""
    
    def __init__(self):
        # Load configurations
        config_dir = Path(__file__).parent.parent.parent / "config"
        
        with open(config_dir / "agents.yaml", "r") as f:
            self.agents_config = yaml.safe_load(f)
            
        with open(config_dir / "tasks.yaml", "r") as f:
            self.tasks_config = yaml.safe_load(f)
            
        # Initialize LMStudio service
        self.lmstudio_service = LMStudioService()
        
        # Initialize agents
        self.topic_analysis_agent = TopicAnalysisAgent(
            self.agents_config["topic_analysis"],
            self.lmstudio_service
        )
        
        self.category_breakdown_agent = CategoryBreakdownAgent(
            self.agents_config["category_breakdown"],
            self.lmstudio_service
        )
        
        self.iterative_refinement_agent = IterativeRefinementAgent(
            self.agents_config["iterative_refinement"],
            self.lmstudio_service
        )
        
        self.research_integration_agent = ResearchIntegrationAgent(
            self.agents_config["research_integration"],
            self.lmstudio_service
        )
    
    @agent
    def get_topic_analysis_agent(self) -> Agent:
        return self.topic_analysis_agent.agent
    
    @agent
    def get_category_breakdown_agent(self) -> Agent:
        return self.category_breakdown_agent.agent
    
    @agent
    def get_iterative_refinement_agent(self) -> Agent:
        return self.iterative_refinement_agent.agent
    
    @agent
    def get_research_integration_agent(self) -> Agent:
        return self.research_integration_agent.agent
    
    @task
    def topic_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["topic_analysis_task"],
            agent=self.get_topic_analysis_agent()
        )
    
    @task
    def category_breakdown_task(self) -> Task:
        return Task(
            config=self.tasks_config["category_breakdown_task"],
            agent=self.get_category_breakdown_agent()
        )
    
    @task
    def iterative_refinement_task(self) -> Task:
        return Task(
            config=self.tasks_config["iterative_refinement_task"],
            agent=self.get_iterative_refinement_agent()
        )
    
    @task
    def research_integration_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_integration_task"],
            agent=self.get_research_integration_agent()
        )
    
    @crew
    def get_crew(self) -> Crew:
        """Creates the Prompt Enhancer crew"""
        return Crew(
            agents=[
                self.get_topic_analysis_agent(),
                self.get_category_breakdown_agent(),
                self.get_iterative_refinement_agent(),
                self.get_research_integration_agent()
            ],
            tasks=[
                self.topic_analysis_task(),
                self.category_breakdown_task(),
                self.iterative_refinement_task(),
                self.research_integration_task()
            ],
            process=Process.sequential,
            verbose=True
        )
        
    def enhance_prompt(self, prompt_request: PromptRequest) -> Dict[str, Any]:
        """Process a prompt through the enhancement pipeline"""
        # Initialize crew
        crew = self.get_crew()
        
        # Execute the crew with the prompt
        result = crew.kickoff(inputs={"prompt": prompt_request.content})
        
        return {
            "status": "success",
            "enhanced_prompt": result,
            "processing_details": {
                "topic_analysis": self.topic_analysis_agent.last_result,
                "category_breakdown": self.category_breakdown_agent.last_result,
                "iterative_refinement": self.iterative_refinement_agent.last_result,
                "research_integration": self.research_integration_agent.last_result
            }
        }