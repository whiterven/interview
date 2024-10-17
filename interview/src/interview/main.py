#!/usr/bin/env python
import asyncio
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router, or_
from interview.crews.resume_review.src.resume_review.crew import ResumeReviewCrew
from interview.crews.initial_interview.src.initial_interview.crew import InitialInterviewCrew
from crewai_tools import FileReadTool

class InterviewState(BaseModel):
    job_description: str = ""
    resume: str = ""
    resume_analysis: str = ""
    candidate_evaluation: str = ""
    initial_interview_results: str = ""
    final_decision: str = ""
    proceed_to_interview: bool = False

class InterviewFlow(Flow[InterviewState]):
    def __init__(self):
        super().__init__()
        self.job_read_tool = FileReadTool(
            name="Job Description Reader",
            description="Reads job description from file",
            path='src/interview/job_description/software_engineer.txt'
        )
        self.resume_read_tool = FileReadTool(
            name="Resume Reader",
            description="Reads candidate resume from file",
            path='src/interview/resumes/strong_resume.txt'
        )

    @start()
    def initialize_process(self):
        print("Starting the interview process")
        # Use the tool's run method without await
        self.state.job_description = self.job_read_tool.run()
        self.state.resume = self.resume_read_tool.run()

    @listen(initialize_process)
    def review_resume(self):
        print("Reviewing resume")
        resume_crew = ResumeReviewCrew().crew()
        result = resume_crew.kickoff()
        self.state.resume_analysis = result.get("review_resume", "")
        self.state.candidate_evaluation = result.get("evaluate_candidate", "")
        
        try:
            score = int(self.state.candidate_evaluation.split("\n")[0].split(":")[1].strip())
            return "proceed" if score >= 70 else "reject"
        except (IndexError, ValueError):
            print("Error parsing candidate evaluation score")
            return "reject"

    @router(review_resume)
    def route_candidate(self, result):
        if result == "proceed":
            return "proceed_to_interview"
        else:
            return "reject_candidate"

    @listen("proceed_to_interview")
    def conduct_initial_interview(self):
        print("Conducting initial interview")
        interview_crew = InitialInterviewCrew().crew()
        result = interview_crew.kickoff(inputs={
            "job_description": self.state.job_description,
            "resume_analysis": self.state.resume_analysis,
            "candidate_evaluation": self.state.candidate_evaluation
        })
        self.state.initial_interview_results = result.get("conduct_initial_interview", "")
        self.state.final_decision = result.get("make_final_decision", "")
        
        try:
            decision = self.state.final_decision.split("\n")[2].split(":")[1].strip()
            self.state.proceed_to_interview = decision == "Proceed to full interview"
        except IndexError:
            print("Error parsing final decision")
            self.state.proceed_to_interview = False

    @listen("reject_candidate")
    def handle_rejection(self):
        print("Candidate did not meet minimum requirements")
        self.state.final_decision = "Rejected based on initial resume review"

    @listen(or_(conduct_initial_interview, handle_rejection))
    def finalize_process(self):
        if self.state.proceed_to_interview:
            print("Candidate has been approved for a full interview")
        else:
            print("Candidate has been rejected")
        
        return {
            "resume_analysis": self.state.resume_analysis,
            "candidate_evaluation": self.state.candidate_evaluation,
            "initial_interview_results": self.state.initial_interview_results,
            "final_decision": self.state.final_decision,
            "proceed_to_interview": self.state.proceed_to_interview
        }

async def run():
    try:
        interview_flow = InterviewFlow()
        result = await interview_flow.kickoff()
        print("Interview process completed")
        print(f"Final result: {result}")
    except Exception as e:
        print(f"An error occurred during the interview process: {str(e)}")

async def plot():
    """
    Plot the flow.
    """
    interview_flow = InterviewFlow()
    await interview_flow.plot()

def main():
    asyncio.run(run())

def plot_flow():
    asyncio.run(plot())

if __name__ == "__main__":
    main()