## Inspiration
Whenever I get home from work and I have to think, what did I have planned for dinner? Kitchenly dinner manager allows you to plan ahead, and be prepared for the week ahead of time. You can also get suggestions by rating dinners, and asking for your top meals!

## What it does
By adding and rating your dinners, you can always be prepared whether it be figuring out what dinners you have had and liked in the past, or getting home after a long day of work and not remembering what you had planned!

## How I built it
I used (Flask-Ask)[https://github.com/johnwheeler/flask-ask] to develop the app. I was able to test using (ngrok)[https://ngrok.com/]. I deployed using (Zappa)[https://github.com/Miserlou/Zappa] to upload the code to lambda, and provision an API gateway.

## Challenges I ran into
Deploying to lambda led to many challenges. I ran into a couple of issues initially with the packages not loading correctly. This turned out to be an issue with `pip 10` and I had to downgrade manually to `pip 9` whenever I created a virutalenv. 

## Accomplishments that I'm proud of
This has been my first Alexa app that I have gotten to the point of submitting to the App store. Seeing the app through to the end has been an incredible learning experience.

## What I learned
Beyond the frameworks I used to develop the app, I have learned to think about voice assistants in a different way. When developing, you have to spend time interacting physically with the app. A few times while testing, I would ask for information in a way I had not thought about originally. You have to approach the problem organically, and not the typical way you would develop an API.

## What's next for Kitchenly Dinner Manager
The next steps are to assess how people are using the app, and add new features accordingly. I want to create a more robust CI/CD pipeline, and add more robusts tests. This includes unit testing the actual endpoints and then automating the voice interactions if possible. Once these are done, I want to allow users to access their past dinners, and ratings from a website. 
