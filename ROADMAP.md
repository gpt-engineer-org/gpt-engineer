# Roadmap

There are three main milestones we believe will 2x gpt-engineer's reliability and capability:
- Continuous evaluation of our progress
- Make code generation become small, verifiable steps
- Run tests and fix errors with GPT4

## Steps to achieve our roadmap

- [ ] Continuous evaluation of our progress
  - [ ] Create a step that asks “did it run/work/perfect” in the end of each run [#240](https://github.com/AntonOsika/gpt-engineer/issues/240)
  - [ ] Run the benchmark multiple times, and document the results for the different "step configs" (`STEPS` in `steps.py`) [#239](https://github.com/AntonOsika/gpt-engineer/issues/239)
  - [ ] Document the best performing configs, and feed these learnings into our roadmap
  - [ ] Collect a dataset for gpt engineer to learn from, by storing code generation runs, and if they fail/succeed (on an opt out basis)
- [ ] Self healing code
  - [ ] Feed the results of failing tests back into GPT4 and ask it to fix the code
- [ ] Let human give feedback
  - [ ] Ask human for what is not working as expected in a loop, and feed it into GPT4 to fix the code, until the human is happy or gives up
- [ ] Make code generation become small, verifiable steps
  - [ ] Ask GPT4 to decide how to sequence the entire generation, and do one
  prompt for each subcomponent
  - [ ] For each small part, generate tests for that subpart, and do the loop of running the tests for each part, feeding
results into GPT4, and let it edit the code until they pass
- [ ] LLM tests in CI
  - [ ] Run very small tests with GPT3.5 in CI, to make sure we don't worsen
performance over time
- [ ] Dynamic planning
  - [ ] Let gpt-engineer plan which "steps" to carry out itself, depending on the
task, by giving it few shot example of what are usually "the right-sized steps" to carry
out for other projects

# How you can help out

You can:

- Submit your first PR to address an [issue](https://github.com/AntonOsika/gpt-engineer/issues)
- Submit PRs to address one of the items in the roadmap
- Do your first review of someone else's PR/issue and propose next steps (further review, merge, close)
- Sign up to help [measure the progress of gpt-engineer towards recursively coding itself](https://forms.gle/TMX68mScyxQUsE6Y9)

Volunteer work in any of these gets acknowledged.

### Repository ergonomics
- [ ] Set up automatic PR review for all PRs (based on AI)

### Ad hoc experiments
- [ ] Try Microsoft guidance, and benchmark if this helps improve performance
