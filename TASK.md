# (BSc Students) SQR Group Project Assignment

## Evaluation Criteria in the Context of the Course

### Teaching Objectives

The course promotes blending renowned theory with practical exercises. In particular, the course stresses the need for automated quality evaluation at each stage of project development through quality gates for Continuous Integration. While the labs provide the basics for setting up quality gates and assessing individual practical skills, the group project encourages using those techniques in a team setting. Thus, the teaching objectives are:

- Encourage using the acquired knowledge about quality methods in practice.
- Setting the context for automated quality assessment in a team project.
- Encourage practicing continuous integration and quality gates.
- Demonstrate the blend of renowned theory with modern industry practices for continuous integration and automated quality gates.

## Project Selection Criteria

Instructors will assign a Product Manager (PM) to each team. The PM will suggest the project topic and quality requirements.

The overall goal is to practice automated quality gates in CI/CD with a toy group project. The group should include 4-5 people per project. Any subject (mind criteria) is accepted. Each group member must participate. The PMs and teams are advised to negotiate for a project that will maximize practicing the course topics in a closer-to-real context.

### Requirements for Project Selection:

- At least a simple UI (to test it with Selenium).
- The project should use an external API for something (e.g., Authentication, NASA pictures, Sports tracks, Bird songs, Quotes of the day, Maps).
- 3 or more major interconnected features.
- Each team member has to contribute at least 1 distinct feature.

The project content should be negotiated with the assigned PM. The estimated development effort should not exceed 1 week for each project member (excluding presentation preparation).

### Example Projects

- Birds songs catalog and observations.
- Sports tracks backup and mapping.
- Todolist notificator.
- Innocarma - helping out with a broken PC.
- Overheard in Innopolis - clever quotes.
- Inno best deals.
- Personal Software Process backlog app.
- 360-degree team members evaluation app with a personality test.

## Project Quality Requirements

The project has to establish concrete quality requirements in the following areas:

- Maintainability.
- Reliability.
- Performance.
- Security.

The requirements should be based on concrete levels of metrics to be collected with tools. Students are welcome to select tools covered in labs (pytest, coverage, mutmut, hypothesis, locust, selenium, sonar, ruff, flake, bandit, snyk), but also surprise us with other relevant tools. When appropriate, the tools have to be integrated into CI.

## Technical Stack

We prioritize simplicity both for students and TAs. We want you to concentrate on quality matters rather than fighting with frameworks. Thus, we fix the following as the course tech stack:

- Python 3.12.
- uv as an environment and module management.
- FastAPI for the REST.
- OpenAPI for REST docs.
- SQLite for persistency.
- Streamlit for the front.
- GitHub for repo and CI.

## Teamwork

We encourage teamwork very much. All team members should participate in the project work to get all the benefits of the group exercise. If you have a case when a team member does not contribute, please inform the Instructor at a.sadovykh@innopolis.ru or telegram @sadovykh.

## Evaluation Criteria

The cases coming from the industry are very different. However, we may group the criteria in the following order:

1. (15pt) Criteria for artifacts evaluation:
   - Progress on quality gate automation.
   - Level of coverage:
     - Coverage from 60% statement (as per Google min requirements for the coverage).
   - The number of methods applied, for example:
     - Static analysis, including style check and complexity.
     - Unit testing, Integration testing, UI testing.
     - Mutation testing, Fuzz testing, Stress testing.
     - Recovery Implementation or any other reliability mechanisms.
     - UI testing and exploratory testing effort.
   - Results of performance testing.

2. (5pt) Presentations content:
   - Organization and process.
   - Progress and results.
   - Quality automation.
   - Lessons learned.

## (MSc Students) Product Management Assignment

The group project guidelines from previous chapters create a quality requirements specification in the teaching context.

### Teaching Objectives

- Learn to create a complete set of quality requirements at least on the basic level.
- Understand the concrete measures to ensure and validate the quality requirements.
- Practice quality analysis skills.

### Task 1. Project Description (1 page + requirements)

1. Create a 1-page description of the toy project that is feasible for 1 week of development in a team of 5.
2. In addition, create a compact list of concrete quality requirements covering:
   - Maintainability.
   - Reliability.
   - Performance.
   - Security.

3. The requirements must indicate the metrics thresholds to be measurable with the help of concrete and appropriate tools.
4. The required quality levels must be assessed within CI pipelines whenever possible.

!!! Already done in PROJECT.md by the instructor.

### Negotiation Process

- Developers and PMs are invited to negotiate concrete terms and quality levels to be reached.
- This negotiation process has to ensure the feasibility of the toy project and the clearness of quality requirements.
- The minimum level of the quality requirements provided in this document must be preserved.
- The negotiation is allowed within 1 week of the project assignment.

### Task 2. Analysis Report (5 pages max)

- After the project is delivered, the PM must independently run the quality analysis and measure the quality levels achieved.
- The (5-page max) report will indicate the precise levels of quality metrics reached by the toy projects.
- PMs are invited to run additional analyses not covered by the developers to indicate any specific problems.
