# Capability improvement roadmap
- [ ] Continuous capability measurements
  - [ ] Create a step that asks “did it run/work/perfect” in the end [#240](https://github.com/AntonOsika/gpt-engineer/issues/240)
  - [ ] Run the benchmark repeatedly and document the results for the different "step configs" (`STEPS` in `steps.py`) [#239](https://github.com/AntonOsika/gpt-engineer/issues/239)
  - [ ] Document the best performing configs, and feed this into our roadmap
- [ ] Self healing code
  - [ ] Feed the results of failing tests back into GPT4 and ask it to fix the code
- [ ] Let human give feedback
  - [ ] Ask human for what is not working as expected in a loop, and feed it into
GPT4 to fix the code, until the human is happy or gives up
- [ ] Break down the code generation into small parts
  - [ ] For each small part, generate tests for each subpart, and do the loop of running the tests for each part, feeding
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
- Sign up to help [measure the progress of gpt-engineer towards "bootstrapping"](https://forms.gle/TMX68mScyxQUsE6Y9)
- Submit PRs to address one of the items in the roadmap

### Repository ergonomics
- [ ] Set up automatic AI/LLM based PR review

### Ad hoc experiments
- [ ] Microsoft guidance, and benchmark if this helps improve performance

