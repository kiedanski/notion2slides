# How to Deploy

Followed this [guide](https://www.youtube.com/watch?v=RGIM4JfsSk0)
 
1. Run `scripts/generate_zip.sh` to generate a zip with all the content.
2. Upload `lambda_functino.zip` to AWS
3. Make sure that the handler is configured to be `main.handler`

# To test locally

1. Install requirements
2. Run `uvicorn main:app --reload`