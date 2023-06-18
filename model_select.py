import openai


def model_select_method():
    model = "gpt-4"
    try:
        openai.Model.retrieve(model)
    except openai.error.InvalidRequestError:
        print(
            "Model gpt-4 not available for provided api key reverting "
            "to gpt-3.5.turbo. Sign up for the gpt-4 wait list here: "
            "https://openai.com/waitlist/gpt-4-api"
        )
        model = "gpt-3.5-turbo"
    return model
