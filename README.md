# Hitman Video Checker

This scrapes *all runs from the Hitman WoA games on SRC and then puts it into JSON files, those JSON files then get put through the video checking script where YT video's are checked using the YT API, where unavailable videos are identified, and non YT videos are put into a seperate JSON file. 

In theory and testing, all runs found by this script will have an unavailable youtube video in the main video submission field, runs with ex. an unavailable YT video but with a working BiliBili video in the description will be detected by this script as unavailable.

I have no plans to expand this script to check non YT videos as YT videos are the chosen submission platform for around 94% of runs as of writing this.

*Uses [speedruncompy](https://github.com/ManicJamie/speedruncompy) as opposed to SRC's official v1 API for future proofing as pagination breaks at 10k, I dont know how/it isnt supported by v2 to collect the runs from archived categories on SRC, which is something that you could do with v1, so the run count will always be less than the number it says on SRC games with archived categories

# To Do:
- Send discord message after pages deployment instead of immediately after checking

