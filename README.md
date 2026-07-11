# my personal website! 
###### (served with flask because its funny)

this is just a little personal website that talks about me and some of the stuff ive done! the backend is far too large, 
as i have a way of overcomplicating things (im pretty sure there are technically more admin pages than public pages, 
though they are smaller)

this is overengineered in almost every way possible lol. there isnt a bit of javascript here (except for the umami tracker), 
and everything is served dynamically with flask. the stats on the main page are pulled from actual things i selfhost, and 
are cached to avoid people spamming it. that cache is manually handled with sqlite because i didnt know what redis was 
when i set that up :pf:. okay technically theyre not cached anymore, theyre refreshed independently using an apscheduler 
task so the page will never be slow waiting for one to load

the blogs are also stored in sqlite, and i write them with markdown (hopefully ive actually written one by the time you 
read this :P), which is stored in sqlite along with some metadata. when you try to load a blog, the site pulls the 
markdown for said blog, and converts it to html using `markdown_it`

the site also serves `.well-known` files, but it also does that dynamically because i serve this site from two domains 
(thirtyseventh.xyz and graysonv.ca), so theres an admin page to configure them

said admin page is protected by my selfhosted oauth instance, mostly because i thought it would be funny, but who couldve 
guessed that it would be annoying getting oauth working properly?

as for the css and design of the public pages, that took far longer than it should have because its my first time using 
html and css, and i have no clue what im doing. the css specifically is probably spaghetti, but it works. theres definitely some minor issues, but overall im quite happy with the 
way it looks

---

sonnet 4.6 helped with some of the oauth stuff, and also occasionally told me how to do basic css stuff, ex: me just not 
having the class set properly. it also helped me figure out how to use flask blueprints. i mostly used it to point out me 
being an idiot though

---

### running it
if for some reason you want to... run my personal website, youre going to need a few things as i really didnt intend for this.
youll need this stuff running:

1. a voidauth sso server (configured with an oidc app for this, using the default config)
2. a komodo instance to pull docker stats from
3. a grafana instance connected to prometheus connected to uptime kuma to pull uptime data from

after youve got that stuff setup and gotten familiar with it, copy `example.env` to `.env` (or your compose env vars directly) and fill out all of the values (theres some comments to maybe help with this, it should be pretty easy if youve used the software needed before)

then you can run `docker compose up -d` in the directory root and it should build the docker image and launch