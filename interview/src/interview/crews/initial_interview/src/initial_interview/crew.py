from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew

llm = 'groq/mixtral-8x7b-32768'

@CrewBase
class InitialInterviewCrew:
    """Crew for InitialInterviewCrew"""

    @agent
    def interviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['interviewer'],
            llm=llm,
            verbose=True
        )

    @agent
    def final_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['final_evaluator'],
			llm=llm,
            verbose=True
        )

    @task
    def conduct_initial_interview(self) -> Task:
        return Task(
            config=self.tasks_config['conduct_initial_interview'],
            output_file='initial_interview_results.md'
        )

    @task
    def make_final_decision(self) -> Task:
        return Task(
            config=self.tasks_config['make_final_decision'],
            output_file='final_decision.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the InitialInterveiwCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )