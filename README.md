# Slankey_Blaseball_Team_Timelines
A visualiser for Blaseball teams over time as a Sankey plot, using Python, the Plotly library and the SIBR Datablase

INTRO

This is a tool that uses data from the Society for Internet Blaseball Research's Datablase stack to visualise timelines of players and teams over time.
The intent is it should be possible to create views of any team and any time span, in order to entertain, inform and educate people on Blaseball history.
It is written in Python 3.8+ or so, utilises the Plotly library extensively, has a lil bit of SQL in there to get data out of the Datablase,
and is the first coding project I've done that I've ever felt like someone else might be interested in. Accordingly, expect Bad Code and Data Crimes.

If you don't know what Blaseball is, my goodness I can't possibly explain here. This video is good: https://www.youtube.com/watch?v=Y5t8DwnDE1k , it's what got
me into this colossal but beautiful waste of time and emotional energy.

I'm Meserach, because I thought that was cool when I was like 17 and I was too lazy to change it since. There's some chance people may be collaborating on this with me soon, 
and if they do they should introduce themselves in a new version of this I guess?

USAGE NOTES

Right now, you need to find the line 153 in "main.py", change the team nickname there to the one you want to see, and then run the code. 
You'll need all the dependencies installed first, of course.
If it works the Sankey plot will automatically open in your default browser.

The plot displays the lineup, rotation, bullpen and becnh of the chosen team over time, including changes to the ordering due to e.g. Reverb. 
It also shows timelines for any player who has ever been on the chose team, however briefyl: their careers outside the team in question are shown
as lines at the bottom of the plot.

LIMITATIONS

Right now it displays one (1) team, and all the players who have ever been on that team, however briefly.
It's also locked at present to displying the whole history of the IBL (Internet Blaseball League).

