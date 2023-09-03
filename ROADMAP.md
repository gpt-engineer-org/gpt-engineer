# Roadmap

We do all our planning centered around our roadmap.

The roadmap itself is a function of our ["key problems to solve"](ROADMAP.md#problems-to-solve) and [philosophy](README.md#project-philosophy).

Anyone is welcome to suggest changes the roadmap via DM or PR.

![image](https://github.com/AntonOsika/gpt-engineer/assets/4467025/4c1c6233-2e99-42a8-bb41-eba702041d76)

# Problems to solve

Our top focus:
1. **Reliability**. Produce bug-free code.
2. **Great UX**. It should be possible to both create codebases and improve codebases intuitively. With rapid handover between AI and human.
3. **Simplicity**. Simple to understand the code and use gpt-engineer.

## Our current focus

We only focus on three things, see below.


- [ ] Great "improve code" UX
  - [ ] Collect and share comparison between 1) gpt-engineer "-i" flag, 2) Aider, 3) Mentat
  - [ ] Incorporate the top advantages of each alternative into gpt-engineer
  - [ ] Git integration, let us create commits
  - [ ] Parse "diffs" from LLM, and apply them as commits
- [ ] Self healing code
  - [ ] 1. Ask the LLM what a QA person would test based on the project specification
  - [ ] 2. Ask the LLM if the generated code is expected to pass QA, or if something should be fixed
  - [ ] 3. Feed any error output, when building the project to LLM and ask it to fix the code and try again
- [ ] Simplify codebase
  - [ ] Remove unnecessary configs (tdd, tdd_plus, clarify, respec). If we have time we benchmark them and store insights before deletion.
  - [ ] Refactor step functions into separate files


## Codebase improvements
By improving the codebase and developer ergonomics, we accelerate progress.

Example of ways:
- [ ] Set up automatic PR review for all PRs with e.g. Codium pr-agent
- [ ] LLM tests in CI: Run super small tests with GPT3.5 in CI, that check that simple code generation still works

# How you can help

You can:

- Look for issues with the label "good first issue"
- Assign yourself to an issue
- Submit a PR to address the issue
- (Ask for feedback in discord if you are unsure about anything)

You can also:
- Do a review of someone else's PR and propose next steps (further review, merge, close)
- Post a "design" as a google doc in our Discord and ask for feedback to address one of the items in the roadmap

We put focus on giving acknowledgemnt to those that do exceptional work.
