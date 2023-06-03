### Next up
We have noticed that for complex projects the model is "lazy" in implementing many files.

Hence, we want to let LLM generate a new prompt for a "sub-engnieer" that goes through each file, takes other relevant files as context and rewrites the files.


### More things to try
- allow for human edits in the code/add comments and store those edits as diffs, to use as "feedback" in the future etc
- Add step of generating tests
- Fix code based on failing tests
- Allow for rerunning the entire run from scratch, but "replay" human diffs by adding the diffs to the prompt and asking LLM to apply them in the new code
- keep a repository of examples of human feedback that can be reused globally
- Allow for fine grained configuration, per project, so that it can be regenerated from scratch applying all the human diffs that came after the initial AI generation step. Which diffs come in which steps, etc.
