from lxml import html
from bisect import insort
import math

# path to your file here
path = 'E:\Win Env\chuni analyzer\\akane.gg8-10-22.htm'
f = open(path, encoding='utf-8').read()

tree = html.fromstring(f)


class Play:
    def __init__(self, level, score, title):
        self.title = title
        self.score = score
        self.level = level

        # stolen from rhythm game stats library
        # https://github.com/TNG-dev/rg-stats
        levelBase = level*100
        rating = 0
        if score >= 1_007_500:
            rating = levelBase + 200
        elif score >= 1_005_000:
            rating = levelBase + 150 + ((score - 1_005_000) * 10) / 500
        elif score >= 1_000_000:
            rating = levelBase + 100 + ((score - 1_000_000) * 5) / 500
        elif score >= 975_000:
            rating = levelBase + ((score - 975_000) * 2) / 500
        elif score >= 925_000:
            rating = levelBase - 300 + ((score - 925_000) * 3) / 500
        elif score >= 900_000:
            rating = levelBase - 500 + ((score - 900_000) * 4) / 500
        elif score >= 800_000:
            rating = (levelBase - 500) / 2 + ((score - 800_000)
                                              * ((levelBase - 500) / 2)) / 100_000

        self.rating = rating/100

    def __str__(self):
        return f'{round(self.rating,2)}\tfrom {self.score}\ton {self.level}\t{self.title}'
        #string representation of score

    def __lt__(self, other):
        return self.rating < other.rating

    def __eq__(self, other):
        return self.title.__eq__(other.title)


scores = [
    Play(
        float(x.getchildren()[2].values()[1]),
        int(x.getchildren()[3].text.strip().replace(',', '')),
        x.getchildren()[1].getchildren()[0].getchildren()[0].text) for x in tree.xpath('//tr')[1:]
    # we do a little scraping
    # you can modify this for your own purposes
]


class Best:
    def __init__(self):
        self.top = []
        self.recent = []
        self.recentlen = 30

    def add(self, play):
        if (play not in self.top):  # check for dupes
            insort(self.top, play)
        else:  # check if play is better than previous play
            i = -1
            for x in self.top:  # find dupe
                if x.title == play.title and play.rating > x.rating:
                    i = self.top.index(x)
            if i != -1:  # remove if its worse
                self.top.pop(i)
                insort(self.top, play)

        if len(self.top) > 30:  # keep length for inserting
            self.top.pop(0)

        self.recent.append(play)  # add play to recent scores (duh)
        if len(self.recent) > self.recentlen:  # keep length
            if play.score < 1_007_500:  # SSS scores permanently stay in your recent
                self.recent.pop(0)
            else:
                self.recentlen += 1

    def __str__(self):
        self.recent.sort()
        topavg = round(sum([x.rating for x in self.top]) /
                       30, 2)  # average of top 30
        # average of top 10 of recent 30
        recentavg = round(sum([x.rating for x in self.recent[-10:]])/10, 2)

        return ('Best 30:\n'+'\n'.join([str(x) for x in reversed(self.top)]) +
                f'\n30 Rating: {topavg}' +
                '\n\nBest 10 of Recent 30:\n' + '\n'.join([str(x) for x in reversed(self.recent[-10:])]) +
                f'\nRecent Rating:{recentavg}'+
                f'\n\nOverall Rating: {(sum([x.rating for x in self.top])+sum([x.rating for x in self.recent[-10:]]))/40}')
        # overall rating is always rounded down by two decimal places


best = Best()
for x in reversed(scores):
    best.add(x)

print(best)


#title /html/body/div[2]/div/div/div/div/table/tbody/tr[1]/td[2]/div/a
#level /html/body/div[2]/div/div/div/div/table/tbody/tr[1]/td[3]/span
#score /html/body/div[2]/div/div/div/div/table/tbody/tr[1]/td[4]
