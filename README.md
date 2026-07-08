# my personal website! 
###### (served with flask because its funny)

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