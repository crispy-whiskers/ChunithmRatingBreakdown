from lxml import html
from bisect import insort
import math, sys

class Play:
    def __init__(self, level, score, title, difficulty):
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
        return f'{math.floor(self.rating*100)/100:.2f}\tfrom '+'{:,}'.format(self.score)+f'\ton {self.level}\t{self.title}'
        #string representation of score
        #rating displayed rounded down
        #{:,} for comma denoted numbers

    def __lt__(self, other):
        return self.rating < other.rating

    def __eq__(self, other):
        return self.title.__eq__(other.title) and self.score == other.score
    
    def __repr__(self):
        return self.__str__()
def insert_string(string, position, character):
    list2=list(string)
    list2[position]=character
    return ''.join(list2)

class Best:
    def __init__(self):
        self.top = []
        self.recent = []

    def add(self, play):
        if (play.title not in [x.title for x in self.top]):  # check for dupes of same song
            insort(self.top, play) # insert into ascending order
        else:  # check if play is better than previous play
            i = -1
            for x in self.top:  # find dupe
                if x.title == play.title and play.score > x.score and play.rating >= x.rating:
                    i = self.top.index(x)
                    break
            if i != -1:  # remove if its worse
                self.top.pop(i)
                insort(self.top, play)

        if len(self.top) > 30:  # keep length for inserting
            self.top.pop(0)

        ratingProtection = False

        if play.score > 1_007_500:  
                
                # the score is a triple S, meaning it wont affect the recent average if it doesnt help the recent average
                # if the rating of the play is less than the average of the recent frame without the oldest play in recent, protection kicks in

                current = sorted(self.recent)[20].rating
                added = sorted(self.recent[1:]+[play])[-10 if len(self.recent) > 10 else 0].rating
                if added < current: 
                    ratingProtection = True
            
        if not ratingProtection:
            self.recent.append(play) # add play to recent scores if rating protection hasnt kicked in

        if len(self.recent) > 30:  # keep length
            
            self.recent.pop(0) # remove a score from the recent frame normally

                
                
                
    def __str__(self):
        topavg = round(sum([x.rating for x in self.top]) / 30 , 7)
        # average of top 30, with rounding to prevent floating point errors
        recentavg = round(sum([x.rating for x in sorted(self.recent)[-10:]])/10, 7)
        # average of top 10 of recent 30, with rounding to prevent floating point errors


        return( 'Best 30:\n'+'\n'.join([str(x) for x in reversed(self.top)]) +
                f'\n30 Rating: {topavg}' 
                +'\n\nBest 10 of Recent 30:\n' + '\n'.join([str(x)+f' ({30-self.recent.index(x)}/30)' for x in reversed(sorted(self.recent)[-10:])])+ 
                f'\nRecent Rating:{recentavg}'
                +f'\n\nOverall Rating: {(sum([x.rating for x in self.top])+sum([x.rating for x in sorted(self.recent)[-10:]]))/40}')
        # overall rating is always rounded down by two decimal places, but keeping raw decimal
        # so you can see exactly where you are

if __name__ == "__main__":
    f = open(sys.argv[1], encoding='utf-8').read()

    tree = html.fromstring(f)
    scores = [
        Play(
            float(x.getchildren()[2].values()[1]), 
            int(x.getchildren()[3].text.strip().replace(',', '')),
            x.getchildren()[1].getchildren()[0].getchildren()[0].text,
            x.getchildren()[2].values()[0]
        ) 
        for x in list(filter(lambda i: len(i.getchildren()[2].values()[1]) > 1, 
        tree.xpath('//tr')[1:])) 
        # we do a little scraping
        # you can modify this for your own purposes
    ]

    #run the stuff
    best = Best()
    for x in reversed(scores):
        best.add(x)

    print(best)

#for your purposes: xpath of every bit of data
#title /html/body/div[2]/div/div/div/div/table/tbody/tr[1]/td[2]/div/a
#level /html/body/div[2]/div/div/div/div/table/tbody/tr[1]/td[3]/span
#score /html/body/div[2]/div/div/div/div/table/tbody/tr[1]/td[4]
