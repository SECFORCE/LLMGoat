# LLMGoat
This project is a deliberately vulnerable environment to learn about LLM-specific risks based on the OWASP Top 10 for LLM Applications.

To build the docker image:

`docker build . -t llmgoat`

To run it:

`docker run --name=llmgoat --rm -p5000:5000 -it llmgoat`

![llmgoat](./static/llmgoat.png)![]()
