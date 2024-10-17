from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import FileReadTool

job_read = FileReadTool(file_path='src/interview/job_description/software_engineer.txt')
resume =FileReadTool(file_path='src/interview/resumes/strong_resume.txt')

llm = 'gemini/gemini-1.5-pro'

@CrewBase
class ResumeReviewCrew:
    """Crew for reviewing resumes and evaluating candidates"""

    @agent
    def resume_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['resume_reviewer'],
            llm=llm,
            tools=[resume],
            verbose=True
        )

    @agent
    def job_matcher(self) -> Agent:
        return Agent(
            config=self.agents_config['job_matcher'],
			llm=llm,
            tools=[job_read],
            verbose=True
        )

    @task
    def review_resume(self) -> Task:
        return Task(
            config=self.tasks_config['review_resume'],
            output_file='resume_analysis.md'
        )

    @task
    def evaluate_candidate(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_candidate'],
            output_file='candidate_evaluation.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )