# Standard libraries
import logging
import sys
from os import path
from pathlib import Path

# Helper functions from the utils folder
from utils.embedding_helper import create_resume_rules_tool, create_resume_tool_from_pdf
from utils.agent_helper import create_resume_agent, query_resume_agent
from utils.keyword_searcher import analyze_keyword_counts, count_keywords

# Will process all PDFs in this folder (can be relative path)
INPUT_FOLDER = "./input"
OUTPUT_FOLDER = "./output"

def process_resume(resume_name, resume_rules_tool, input_folder, output_folder):
    # Extract base filename as id
    resume_id = Path(resume_name).stem

    print(f"\n******** Processing {resume_name} ********")
    # 2. Build the resume document and tool
    print("  > Creating vector embedding from resume pdf ...")
    resume_doc_tool, resume_docs = create_resume_tool_from_pdf(path.join(input_folder, resume_name))
    if resume_doc_tool is None:
        # PDF text extraction failed so output warning and stop
        print("  ! PDF text extraction failed.")
        with open(path.join(output_folder, outfile_name), "w", encoding="utf-8") as output_file:
            output_file.write("The automated analysis tool was unable to extract content from your PDF.")

        return

    # Assume the first line of text is their name
    before, _, after = resume_docs[0].page_content.partition("\n")
    name_guess = before.strip()

    # 3. Create the agent runnable
    print("  > Constructing custom agent ...")
    agent_runnable = create_resume_agent([resume_doc_tool, resume_rules_tool], 0.2)

    # 4. Run Query
    print("  > Querying agent ...")
    questions = [
        f"What the name of the author of this resume? (it is likely '{name_guess}')",
        "Does the resume include contact info? (do not show the contact info, just describe it indirectly)",
        "What is the author's major and minor (if any)?",
        "What is the author's career goal?",
        "When does the author graduate?",
        "What is the author's GPA?",
        "Is this resume complete?",
        "Please rate the completeness and strength of this resume on a scale of 1 to 10 (1 being the lowest and 10 being the highest)."
    ]
    responses = query_resume_agent(questions, agent_runnable, resume_id)

    # 5. Do the keyword analysis (manually, because AI is bad at this and it's not needed)
    skills_kw = [
        "agile", "scrum", "software engineering", "teamwork"
    ]
    skills_kw_counts = count_keywords(resume_docs, skills_kw)

    programming_kw = [
        "Java", "C++", "HTML", "CSS", "JavaScript", "PHP", "SQL", "MySQL"
    ]
    programming_kw_counts = count_keywords(resume_docs, programming_kw)

    advanced_kw = [
        "React", "node.js", "express.js", "C#", "Unity", "Unreal Engine",
        "Godot", "Python", "tensorflow", "numpy", "LangChain", "TypeScript"
    ]
    advanced_kw_counts = count_keywords(resume_docs, advanced_kw)

    # 5. Format and Save results
    print("  > Saving results ...")
    outfile_name = f"{resume_id}.response.md"
    with open(path.join(output_folder, outfile_name), "w", encoding="utf-8") as output_file:
        # Add the opening message to the response file
        add_opening_message(output_file)

        # Loop over AI responses and add to output
        for i, response in enumerate(responses):
            if i < len(questions):
                output_file.write(f"## Q: {questions[i]}\n")
            output_file.write(f"{"".join(response)}\n***\n\n")
        
        # Add skill keyword analysis
        skill_kw_analysis = analyze_keyword_counts(skills_kw_counts, skills_kw,
            "soft skills", "your teamwork/soft skills")
        skill_kw_analysis += "***\n\n"
        output_file.write(skill_kw_analysis)

        # Add programming keyword analysis
        programming_kw_analysis = analyze_keyword_counts(programming_kw_counts, programming_kw,
            "programming language", "programming languages you know")
        programming_kw_analysis += "***\n\n"
        output_file.write(programming_kw_analysis)

        # Add advanced keyword analysis
        advanced_kw_analysis = analyze_keyword_counts(advanced_kw_counts, advanced_kw,
            "optional advanced", "potential advanced programming skills")
        if any(item < 1 for item in advanced_kw_counts):
            advanced_kw_analysis += "\n\n(These only apply to more advanced students. Only include these if you know these languages or skills)\n***\n\n"
        else:
            advanced_kw_analysis += "***\n\n"
        output_file.write(advanced_kw_analysis)
    
def add_opening_message(output_file):
    output_file.write("""# AI Review of Resume
This document contains the results of an AI review of your resume. The specific system used was
running on a local machine via [Ollama](https://ollama.com/), powered by the open source weights
from the [Qwen 2.5 Instruct LLM](https://en.wikipedia.org/wiki/Qwen) and the
[Qwen 3 Embedding Model](https://ollama.com/library/qwen3-embedding). No content from your resume
was uploaded to the cloud or provided to a third party in any way.

You can view the full source code of the system that generated this document and manages the local
LLM setup on (GitHub)[https://github.com/UWStout/resume-review-agentic].

## How to Interpret the Results
MOST employers are using tools that try to scan your resume and extract useful information. They
use this information to filter down to only the most relevant applications. Those that do not
pass this filter wind up never being seen by a human. It also often means you get no response
from the employer about your application at all.

Scanning resumes is a HIGHLY flawed process that may result in unfair filtering of your
legitimate job application! This review is meant to **SHOW YOU WHAT AN AI SEES** when it reviews
your resume. Its answers may be incorrect, and its recommendations should not be blindly followed.
If the answer is incorrect it **LIKELY** means it just failed to properly scan your resume.

Use these results to both restructure your resume (add headings, change keywords, expand or
remove sections) and to consider simplifying your formatting. What looks fancy and attractive may
make it harder for the automated systems to scan your resume.

## Other Help
Systems that manage applicants are often called Applicant Tracking Systems (or ATS). These systems
do a lot more than just scan your resume, but that is the part we are concerned with. There are
many website that will offer to do this for you and help you tailor your resume to an ATS, HOWEVER,
most require you to make an account and many are NOT free. They also have dubious privacy
practices and the data in your resume is very sensitive so use care when working with these sites.

A very simple one that I do recommend trying is [Resume Frame](https://resumeframe.com). It is a
simple tool that does not require an account or payment. The results are simple and easy to parse
and it also shows you the **RAW TEXT** that is extracted from your PDF which can help you see exactly
what might be going wrong. **YOU SHOULD ANONYMIZE YOUR RESUME BEFORE USING THIS TOOL!** Change your
name, email, address, and phone number to generic values. The resume is uploaded to their server
which means they may be scraping information from it and using it without your explicit consent.

# AI Review Questions
We created an agentic AI by embedding a set of "resume rules" along with the text of your resume
into the vector space of the LLM. These become part of the reasoning tools that the AI agent can
use to answer questions (beyond the billions of parameters it was trained on). We also provide
a carefully constructed "system prompt" that helps the agent use those tools effectively and
avoid hallucinations. We are specifically using a so called "Instruct" LLM as these are better
at following instructions in the way an agentic AI is supposed to.

The agent still struggles with a few things:
- It often cannot identify your name (because it is not explicitly labeled)
  * I attempt to give it several hints, but it will sometimes be stubborn and refuse to take the hints.
- It is pretty lenient when asked to rank your resume (it often ranks them a few points higher
than I would)
- It will occasionally remember data from other resumes (this is likely a bug on my part but
I haven't been able to fix it yet)
- It is not good at seeing keywords (we instead do this with a simple string search)\n\n""")

def main():
    # Reduce logging
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Get list of resume PDFs
    file_list = [entry for entry in Path(INPUT_FOLDER).iterdir() if entry.is_file() and Path(entry.name).suffix == ".pdf"]
    if len(file_list) < 1:
        print("No PDF files found in {INPUT_DIR}")
        sys.exit(1)

    # 1. Build the resume rules document and tool
    print("> Constructing resume rules vector embedding ...")
    resume_rules_tool, _ = create_resume_rules_tool()

    # Process each resume
    for resume_name in [item.name for item in file_list]:
        process_resume(resume_name, resume_rules_tool, INPUT_FOLDER, OUTPUT_FOLDER)

# Was this script run directly
if __name__ == "__main__":
    main()
