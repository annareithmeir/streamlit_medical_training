import openai

openai.api_key = "k-proj-JxAVaoqzlYkYHBsV3BSjAeXcDx7yEnbqJis9dGBXgsk7ZikzCeAjUi5k1ja4_Hx4W2J-s-rpjIT3BlbkFJTGUy97CzFaeyZzS13cAGGxnv18f7uRCBrse-3HugPGroiDYqOtjItgyvwr8BRkF3MQcZIsAHMA"

try:
    models = openai.Model.list()
    print([model["id"] for model in models["data"]])
except Exception as e:
    print(e)